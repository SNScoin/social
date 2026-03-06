const { Router } = require('express');
const pool = require('../db/pool');
const auth = require('../middleware/auth');
const { parserLimiter } = require('../middleware/rateLimiter');
const { validateSocialUrl } = require('social-common');
const { enqueueParseLinkJob, parseLinkQueue } = require('../jobs/queue');
const { getParser } = require('social-parsers');
const logger = require('../logger');

const router = Router();

/**
 * Direct parse fallback — runs inline when Redis/BullMQ is unavailable.
 * Returns metrics immediately instead of waiting for a background job.
 */
async function parseDirectly(linkId, url, platform) {
    try {
        const parser = getParser(platform);
        const result = await parser.parse(url);

        const metrics = {
            views: result.views || 0,
            likes: result.likes || 0,
            comments: result.comments || 0,
        };

        // Upsert metrics
        await pool.query(
            `INSERT INTO link_metrics (link_id, views, likes, comments, updated_at)
             VALUES ($1, $2, $3, $4, NOW())
             ON CONFLICT (link_id) DO UPDATE SET
               views = $2, likes = $3, comments = $4, updated_at = NOW()`,
            [linkId, metrics.views, metrics.likes, metrics.comments]
        );

        // Update title and clear error
        await pool.query(
            'UPDATE links SET title = COALESCE($1, title), last_error = NULL WHERE id = $2',
            [result.title || null, linkId]
        );

        // Also update monday_data JSONB and write back to Monday.com
        try {
            const linkRow = await pool.query('SELECT company_id, monday_data, monday_item_id FROM links WHERE id = $1', [linkId]);
            if (linkRow.rows.length > 0 && linkRow.rows[0].company_id) {
                const mcRow = await pool.query(
                    'SELECT api_token, board_id, views_column_id, likes_column_id, comments_column_id FROM monday_configs WHERE company_id = $1',
                    [linkRow.rows[0].company_id]
                );
                if (mcRow.rows.length > 0) {
                    const mc = mcRow.rows[0];
                    const mondayData = linkRow.rows[0].monday_data || {};
                    if (mc.views_column_id) mondayData[mc.views_column_id] = String(metrics.views);
                    if (mc.likes_column_id) mondayData[mc.likes_column_id] = String(metrics.likes);
                    if (mc.comments_column_id) mondayData[mc.comments_column_id] = String(metrics.comments);
                    await pool.query('UPDATE links SET monday_data = $1 WHERE id = $2', [JSON.stringify(mondayData), linkId]);

                    // Write back to Monday.com
                    const mondayItemId = linkRow.rows[0].monday_item_id;
                    if (mc.api_token && mondayItemId) {
                        const columnValues = {};
                        if (mc.views_column_id) columnValues[mc.views_column_id] = String(metrics.views);
                        if (mc.likes_column_id) columnValues[mc.likes_column_id] = String(metrics.likes);
                        if (mc.comments_column_id) columnValues[mc.comments_column_id] = String(metrics.comments);

                        // Get the item's actual board_id (subitems have a different board)
                        const boardQuery = `{ items(ids: [${mondayItemId}]) { board { id } } }`;
                        const boardRes = await fetch('https://api.monday.com/v2', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Authorization': mc.api_token },
                            body: JSON.stringify({ query: boardQuery }),
                        });
                        const boardJson = await boardRes.json();
                        const itemBoardId = boardJson?.data?.items?.[0]?.board?.id;

                        if (itemBoardId) {
                            const mutation = `mutation { change_multiple_column_values(board_id: ${itemBoardId}, item_id: ${mondayItemId}, column_values: ${JSON.stringify(JSON.stringify(columnValues))}) { id } }`;
                            const mondayRes = await fetch('https://api.monday.com/v2', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json', 'Authorization': mc.api_token },
                                body: JSON.stringify({ query: mutation }),
                            });
                            const mondayJson = await mondayRes.json();
                            if (mondayJson.errors) {
                                logger.warn({ linkId, mondayItemId, itemBoardId, errors: mondayJson.errors }, 'Monday write-back had errors');
                            } else {
                                logger.info({ linkId, mondayItemId, itemBoardId }, 'Monday write-back successful');
                            }
                        } else {
                            logger.warn({ linkId, mondayItemId }, 'Could not resolve board_id for Monday item');
                        }
                    }
                }
            }
        } catch (e) {
            logger.warn({ linkId, err: e.message }, 'Failed to update monday_data / write-back after parse');
        }

        logger.info({ linkId, metrics }, 'Direct parse completed');
        return { ...metrics, title: result.title || null };
    } catch (err) {
        logger.error({ linkId, err: err.message }, 'Direct parse failed');
        await pool.query('UPDATE links SET last_error = $1 WHERE id = $2', [err.message.substring(0, 250), linkId]);
        return { views: 0, likes: 0, comments: 0, title: null, error: err.message };
    }
}

/**
 * Try BullMQ first; if Redis is down, fall back to direct parse.
 */
async function parseLink(linkId, url, platform) {
    if (parseLinkQueue) {
        try {
            await enqueueParseLinkJob(linkId, url, platform);
            return { queued: true };
        } catch (err) {
            logger.warn({ linkId, err: err.message }, 'BullMQ enqueue failed — falling back to direct parse');
        }
    }
    // Fallback: parse directly
    return parseDirectly(linkId, url, platform);
}

// GET /api/v1/links?companyId=
router.get('/', auth, async (req, res, next) => {
    try {
        const { companyId } = req.query;

        if (!companyId) {
            return res.status(400).json({ error: 'MISSING_REQUIRED_FIELD', message: 'companyId is required' });
        }

        const result = await pool.query(
            `SELECT l.*, 
              json_build_object('views', COALESCE(lm.views, 0), 'likes', COALESCE(lm.likes, 0), 'comments', COALESCE(lm.comments, 0), 'updated_at', lm.updated_at) AS metrics
       FROM links l
       LEFT JOIN link_metrics lm ON lm.link_id = l.id
       WHERE l.company_id = $1
       ORDER BY l.created_at DESC`,
            [companyId]
        );

        res.json(result.rows);
    } catch (err) {
        next(err);
    }
});

// POST /api/v1/links — add link (manual companies only)
router.post('/', auth, parserLimiter, async (req, res, next) => {
    try {
        const { url, company_id, platform } = req.body;

        if (!url || !company_id) {
            return res.status(400).json({ error: 'MISSING_REQUIRED_FIELD', message: 'url and company_id are required' });
        }

        // Verify company is manual and owned by user
        const company = await pool.query(
            'SELECT * FROM companies WHERE id = $1 AND owner_id = $2',
            [company_id, req.user.id]
        );

        if (company.rows.length === 0) {
            return res.status(404).json({ error: 'COMPANY_NOT_FOUND', message: 'Company not found' });
        }

        // Validate URL and detect platform
        let detectedPlatform = platform;
        try {
            const result = validateSocialUrl(url);
            detectedPlatform = result.platform;
        } catch (err) {
            return res.status(400).json({ error: 'INVALID_URL', message: err.message });
        }

        const linkResult = await pool.query(
            'INSERT INTO links (url, platform, user_id, company_id) VALUES ($1, $2, $3, $4) RETURNING *',
            [url, detectedPlatform, req.user.id, company_id]
        );
        const link = linkResult.rows[0];

        // Create empty metrics row
        await pool.query(
            'INSERT INTO link_metrics (link_id) VALUES ($1)',
            [link.id]
        );

        // Parse: try BullMQ, fall back to direct parse
        const parseResult = await parseLink(link.id, url, detectedPlatform);

        if (parseResult.queued) {
            // BullMQ will handle it in the background
            res.status(201).json({ ...link, metrics: { views: 0, likes: 0, comments: 0 } });
        } else {
            // Direct parse — return real metrics immediately
            res.status(201).json({
                ...link,
                title: parseResult.title || link.title,
                metrics: { views: parseResult.views, likes: parseResult.likes, comments: parseResult.comments },
            });
        }
    } catch (err) {
        next(err);
    }
});

// POST /api/v1/links/:id/refresh
router.post('/:id/refresh', auth, parserLimiter, async (req, res, next) => {
    try {
        const { id } = req.params;

        const link = await pool.query(
            `SELECT l.* FROM links l
       JOIN companies c ON c.id = l.company_id
       WHERE l.id = $1 AND c.owner_id = $2`,
            [id, req.user.id]
        );

        if (link.rows.length === 0) {
            return res.status(404).json({ error: 'LINK_NOT_FOUND', message: 'Link not found' });
        }

        const l = link.rows[0];
        const parseResult = await parseLink(l.id, l.url, l.platform);

        if (parseResult.queued) {
            res.json({ message: 'Refresh started', link_id: parseInt(id) });
        } else {
            // Direct parse — return real metrics immediately
            res.json({
                message: 'Refresh complete',
                link_id: parseInt(id),
                metrics: { views: parseResult.views, likes: parseResult.likes, comments: parseResult.comments },
                title: parseResult.title,
            });
        }
    } catch (err) {
        next(err);
    }
});

// DELETE /api/v1/links/:id (manual companies only)
router.delete('/:id', auth, async (req, res, next) => {
    try {
        const { id } = req.params;

        // Verify link belongs to a manual company owned by user
        const link = await pool.query(
            `SELECT l.id FROM links l
       JOIN companies c ON c.id = l.company_id
       WHERE l.id = $1 AND c.owner_id = $2 AND c.type = 'manual'`,
            [id, req.user.id]
        );

        if (link.rows.length === 0) {
            return res.status(404).json({ error: 'LINK_NOT_FOUND', message: 'Link not found or cannot be deleted' });
        }

        await pool.query('DELETE FROM link_metrics WHERE link_id = $1', [id]);
        await pool.query('DELETE FROM links WHERE id = $1', [id]);
        res.json({ message: 'Link deleted', id: parseInt(id) });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
