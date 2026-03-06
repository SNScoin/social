/**
 * Company service — business logic for CRUD + stats.
 */

const pool = require('../db/pool');

async function listCompanies(ownerId) {
    const result = await pool.query(
        `SELECT c.*
         FROM companies c
         WHERE c.owner_id = $1
         ORDER BY c.created_at DESC`,
        [ownerId]
    );

    // Enrich with Monday board name if available
    if (result.rows.length > 0) {
        try {
            const mondayResult = await pool.query(
                'SELECT company_id, board_name FROM monday_configs WHERE company_id = ANY($1)',
                [result.rows.map(r => r.id)]
            );
            const mondayMap = new Map(mondayResult.rows.map(r => [r.company_id, r.board_name]));
            result.rows.forEach(r => { r.monday_board_name = mondayMap.get(r.id) || null; });
        } catch {
            // monday_configs table may not exist yet — skip
            result.rows.forEach(r => { r.monday_board_name = null; });
        }
    }

    return result.rows;
}

async function getCompanyById(id, ownerId) {
    const result = await pool.query(
        'SELECT * FROM companies WHERE id = $1 AND owner_id = $2',
        [id, ownerId]
    );
    if (result.rows.length === 0) {
        const err = new Error('Company not found');
        err.status = 404;
        err.code = 'COMPANY_NOT_FOUND';
        throw err;
    }
    const company = result.rows[0];

    // If Monday company, attach board_columns
    if (company.type === 'monday') {
        try {
            const mc = await pool.query(
                'SELECT board_columns, source_column_id FROM monday_configs WHERE company_id = $1',
                [id]
            );
            if (mc.rows.length > 0) {
                company.board_columns = mc.rows[0].board_columns || [];
                company.source_column_id = mc.rows[0].source_column_id;
            }
        } catch { /* ignore if table doesn't exist */ }
    }

    return company;
}

async function createManualCompany(name, ownerId) {
    const result = await pool.query(
        'INSERT INTO companies (name, owner_id, type) VALUES ($1, $2, $3) RETURNING *',
        [name, ownerId, 'manual']
    );
    return result.rows[0];
}

async function createFromMonday(data, ownerId) {
    const client = await pool.connect();
    try {
        await client.query('BEGIN');

        // Create company
        const companyResult = await client.query(
            'INSERT INTO companies (name, owner_id, type) VALUES ($1, $2, $3) RETURNING *',
            [data.board_name || 'Monday Company', ownerId, 'monday']
        );
        const company = companyResult.rows[0];

        // Save Monday config
        await client.query(
            `INSERT INTO monday_configs
             (company_id, api_token, workspace_id, workspace_name, board_id, board_name,
              source_column_id, views_column_id, likes_column_id, comments_column_id)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
            [
                company.id, data.api_token, data.workspace_id, data.workspace_name,
                data.board_id, data.board_name, data.source_column_id,
                data.views_column_id, data.likes_column_id, data.comments_column_id,
            ]
        );

        await client.query('COMMIT');

        // TODO: Enqueue job to import links from Monday board + parse them

        return { ...company, monday_configured: true };
    } catch (err) {
        await client.query('ROLLBACK');
        throw err;
    } finally {
        client.release();
    }
}

async function getCompanyStats(id) {
    const result = await pool.query(
        `SELECT
             COUNT(l.id) AS total_links,
             COALESCE(SUM(lm.views), 0) AS total_views,
             COALESCE(SUM(lm.likes), 0) AS total_likes,
             COALESCE(SUM(lm.comments), 0) AS total_comments
         FROM links l
         LEFT JOIN link_metrics lm ON lm.link_id = l.id
         WHERE l.company_id = $1`,
        [id]
    );
    return result.rows[0];
}

async function syncCompany(id, ownerId, io) {
    const company = await getCompanyById(id, ownerId);

    if (company.type !== 'monday') {
        const err = new Error('Only Monday.com companies can be synced');
        err.status = 400;
        err.code = 'INVALID_REQUEST';
        throw err;
    }

    // 1. Get Monday config
    const configResult = await pool.query(
        'SELECT * FROM monday_configs WHERE company_id = $1',
        [id]
    );
    if (configResult.rows.length === 0) {
        const err = new Error('Monday.com configuration not found');
        err.status = 404;
        err.code = 'CONFIG_NOT_FOUND';
        throw err;
    }
    const config = configResult.rows[0];

    const axios = require('axios');
    const { validateSocialUrl } = require('social-common');
    const MONDAY_API_URL = 'https://api.monday.com/v2';

    // 2. Fetch board column definitions (all columns)
    const colResponse = await axios.post(
        MONDAY_API_URL,
        { query: `query { boards(ids: [${config.board_id}]) { columns { id title type settings_str } } }` },
        { headers: { Authorization: config.api_token, 'Content-Type': 'application/json' } }
    );
    const boardColumns = colResponse.data?.data?.boards?.[0]?.columns || [];

    // Save column definitions to monday_configs
    await pool.query(
        'UPDATE monday_configs SET board_columns = $1, updated_at = NOW() WHERE company_id = $2',
        [JSON.stringify(boardColumns), id]
    );

    // 3. Fetch ALL items with ALL column values + subitems (paginated)
    let allItems = [];
    let cursor = null;

    do {
        const query = cursor
            ? `query { next_items_page(cursor: "${cursor}") { cursor items { id name column_values { id text value } subitems { id name column_values { id text value } } } } }`
            : `query { boards(ids: [${config.board_id}]) { items_page(limit: 100) { cursor items { id name column_values { id text value } subitems { id name column_values { id text value } } } } } }`;

        const response = await axios.post(
            MONDAY_API_URL,
            { query },
            { headers: { Authorization: config.api_token, 'Content-Type': 'application/json' } }
        );

        const page = cursor
            ? response.data?.data?.next_items_page
            : response.data?.data?.boards?.[0]?.items_page;

        if (page?.items) {
            for (const item of page.items) {
                // Add the parent item
                allItems.push(item);

                // Flatten subitems — these contain the actual post links
                if (item.subitems && item.subitems.length > 0) {
                    for (const sub of item.subitems) {
                        // Tag subitem with parent info for context
                        sub._parentName = item.name;
                        sub._parentId = item.id;
                        sub._isSubitem = true;
                        allItems.push(sub);
                    }
                }
            }
        }
        cursor = page?.cursor || null;
    } while (cursor);

    // 4. Process each item — extract URL from source column, build monday_data
    const processedItems = [];
    for (const item of allItems) {
        // Build monday_data map: { column_id: display_value }
        const mondayData = {};
        let sourceUrl = '';

        for (const col of item.column_values) {
            // Get the display text for each column
            let displayValue = col.text || '';

            // For the source column, ALWAYS extract URL from JSON value.url
            if (col.id === config.source_column_id) {
                if (col.value) {
                    try {
                        const parsed = JSON.parse(col.value);
                        sourceUrl = (parsed.url || '').trim();
                        displayValue = parsed.url || displayValue; // Show actual URL, not label
                    } catch { /* not JSON */ }
                }
                // Fallback: try extracting URL from text (may contain "label - url")
                if (!sourceUrl && displayValue) {
                    const urlMatch = displayValue.match(/https?:\/\/[^\s]+/);
                    if (urlMatch) sourceUrl = urlMatch[0].trim();
                }
            }

            // For link-type columns (not source), extract URL for display
            if (col.type === 'link' && col.id !== config.source_column_id && col.value) {
                try {
                    const parsed = JSON.parse(col.value);
                    displayValue = parsed.url || displayValue;
                } catch { /* not JSON */ }
            }

            // For status columns (Brand, Platform), try to get the label
            if (!displayValue && col.value) {
                try {
                    const parsed = JSON.parse(col.value);
                    if (parsed.label) displayValue = parsed.label;
                    else if (parsed.text) displayValue = parsed.text;
                    else if (parsed.url) displayValue = parsed.url;
                } catch { /* not JSON */ }
            }

            mondayData[col.id] = displayValue;
        }

        if (!sourceUrl) continue;

        // Detect platform
        let platform = 'unknown';
        try {
            const validation = validateSocialUrl(sourceUrl);
            platform = validation.platform;
        } catch {
            // Not a recognized social URL — still import it but mark as unknown
        }

        processedItems.push({
            mondayItemId: item.id,
            mondayItemName: item.name,
            url: sourceUrl,
            platform,
            mondayData,
            isSubitem: !!item._isSubitem,
            parentMondayItemId: item._parentId || null,
        });
    }

    // 5. Get existing links to avoid duplicates
    const existingLinks = await pool.query(
        'SELECT url, monday_item_id FROM links WHERE company_id = $1',
        [id]
    );
    const existingUrls = new Set(existingLinks.rows.map(r => r.url));
    const existingItemIds = new Set(existingLinks.rows.map(r => r.monday_item_id).filter(Boolean));

    const newItems = processedItems.filter(item =>
        !existingUrls.has(item.url) && !existingItemIds.has(item.mondayItemId)
    );

    // 6. Also update monday_data for existing items
    for (const item of processedItems) {
        if (existingItemIds.has(item.mondayItemId)) {
            await pool.query(
                'UPDATE links SET monday_data = $1, updated_at = NOW() WHERE company_id = $2 AND monday_item_id = $3',
                [JSON.stringify(item.mondayData), id, item.mondayItemId]
            );
        }
    }

    // 7. Create new links and parse them
    const { getParser } = require('social-parsers');
    let processed = 0;
    let linksAdded = 0;

    for (const item of newItems) {
        processed++;

        if (io) {
            io.emit('sync:progress', {
                companyId: id,
                processed,
                total: newItems.length,
                currentItem: item.mondayItemName,
            });
        }

        try {
            const linkResult = await pool.query(
                'INSERT INTO links (url, platform, user_id, company_id, title, monday_item_id, monday_data, is_subitem, parent_monday_item_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING *',
                [item.url, item.platform, ownerId, id, item.mondayItemName, item.mondayItemId, JSON.stringify(item.mondayData), item.isSubitem, item.parentMondayItemId]
            );
            const link = linkResult.rows[0];

            await pool.query('INSERT INTO link_metrics (link_id) VALUES ($1)', [link.id]);

            // Parse if platform is recognized
            if (item.platform !== 'unknown') {
                try {
                    const parser = getParser(item.platform);
                    const result = await parser.parse(item.url);

                    const metrics = {
                        views: result.views || 0,
                        likes: result.likes || 0,
                        comments: result.comments || 0,
                    };

                    await pool.query(
                        'UPDATE link_metrics SET views=$1, likes=$2, comments=$3, updated_at=NOW() WHERE link_id=$4',
                        [metrics.views, metrics.likes, metrics.comments, link.id]
                    );

                    if (result.title) {
                        await pool.query('UPDATE links SET title=$1 WHERE id=$2', [result.title, link.id]);
                    }

                    // Write stats back to Monday.com columns
                    try {
                        const mutations = [];
                        if (config.views_column_id) {
                            mutations.push(`change_simple_column_value(board_id: ${config.board_id}, item_id: ${item.mondayItemId}, column_id: "${config.views_column_id}", value: "${metrics.views}")`);
                        }
                        if (config.likes_column_id) {
                            mutations.push(`change_simple_column_value(board_id: ${config.board_id}, item_id: ${item.mondayItemId}, column_id: "${config.likes_column_id}", value: "${metrics.likes}")`);
                        }
                        if (config.comments_column_id) {
                            mutations.push(`change_simple_column_value(board_id: ${config.board_id}, item_id: ${item.mondayItemId}, column_id: "${config.comments_column_id}", value: "${metrics.comments}")`);
                        }

                        for (const mutation of mutations) {
                            await axios.post(
                                MONDAY_API_URL,
                                { query: `mutation { ${mutation} { id } }` },
                                { headers: { Authorization: config.api_token, 'Content-Type': 'application/json' } }
                            );
                        }
                    } catch (writeErr) {
                        console.error('Failed to write back to Monday:', writeErr.message);
                    }

                    if (io) {
                        io.emit('metrics:updated', { linkId: link.id, ...metrics, title: result.title });
                    }
                } catch (parseErr) {
                    console.error(`Parse failed for ${item.url}:`, parseErr.message);
                }
            }

            linksAdded++;
        } catch (err) {
            console.error(`Failed to create link for ${item.url}:`, err.message);
        }
    }

    // 8. Emit sync complete
    if (io) {
        io.emit('sync:complete', {
            companyId: id,
            linksAdded,
            linksRemoved: 0,
            total: processedItems.length,
        });
    }

    return { message: 'Sync complete', linksAdded, totalItems: processedItems.length, skippedDuplicates: processedItems.length - newItems.length };
}

async function deleteCompany(id, ownerId) {
    const result = await pool.query(
        'DELETE FROM companies WHERE id = $1 AND owner_id = $2 RETURNING id',
        [id, ownerId]
    );

    if (result.rows.length === 0) {
        const err = new Error('Company not found');
        err.status = 404;
        err.code = 'COMPANY_NOT_FOUND';
        throw err;
    }

    return { message: 'Company deleted', id };
}

async function updateCompany(id, ownerId, updates) {
    // Build dynamic SET clause
    const fields = [];
    const values = [];
    let idx = 1;

    if (updates.name !== undefined) {
        fields.push(`name = $${idx++}`);
        values.push(updates.name.trim());
    }

    if (fields.length === 0) {
        const err = new Error('No fields to update');
        err.status = 400;
        err.code = 'NO_UPDATE_FIELDS';
        throw err;
    }

    values.push(id, ownerId);
    const result = await pool.query(
        `UPDATE companies SET ${fields.join(', ')} WHERE id = $${idx++} AND owner_id = $${idx} RETURNING *`,
        values
    );

    if (result.rows.length === 0) {
        const err = new Error('Company not found');
        err.status = 404;
        err.code = 'COMPANY_NOT_FOUND';
        throw err;
    }

    return result.rows[0];
}

async function deleteCompany(id, ownerId) {
    // Verify ownership
    const check = await pool.query('SELECT id FROM companies WHERE id = $1 AND owner_id = $2', [id, ownerId]);
    if (check.rows.length === 0) {
        const err = new Error('Company not found'); err.status = 404; err.code = 'NOT_FOUND'; throw err;
    }

    // Delete in correct order (foreign key constraints)
    const linkIds = await pool.query('SELECT id FROM links WHERE company_id = $1', [id]);
    if (linkIds.rows.length > 0) {
        const ids = linkIds.rows.map(r => r.id);
        await pool.query('DELETE FROM link_metrics WHERE link_id = ANY($1)', [ids]);
    }
    await pool.query('DELETE FROM links WHERE company_id = $1', [id]);
    await pool.query('DELETE FROM monday_configs WHERE company_id = $1', [id]);
    await pool.query('DELETE FROM companies WHERE id = $1', [id]);

    return { message: 'Company deleted successfully' };
}

module.exports = {
    listCompanies,
    getCompanyById,
    createManualCompany,
    createFromMonday,
    getCompanyStats,
    syncCompany,
    deleteCompany,
    updateCompany,
};
