/**
 * Parse Link worker — processes individual link parsing via BullMQ.
 * Calls the social-parsers package to fetch real metrics from YouTube, TikTok, etc.
 */

const { Worker } = require('bullmq');
const { connection } = require('./queue');
const pool = require('../db/pool');
const logger = require('../logger');
const { getParser } = require('social-parsers');

function createParseLinkWorker(io) {
    try {
        const worker = new Worker(
            'parse-link',
            async (job) => {
                const { linkId, url, platform } = job.data;
                logger.info({ linkId, url, platform }, 'Processing parse-link job');

                let metrics = { views: 0, likes: 0, comments: 0 };
                let title = null;

                try {
                    // Get the platform parser and fetch real metrics
                    const parser = getParser(platform);
                    const result = await parser.parse(url);

                    metrics = {
                        views: result.views || 0,
                        likes: result.likes || 0,
                        comments: result.comments || 0,
                    };
                    title = result.title || null;

                    logger.info({ linkId, metrics, title }, 'Parser returned metrics');
                } catch (parseErr) {
                    logger.error({ linkId, platform, err: parseErr.message }, 'Parser failed — aborting to prevent overwriting with zeros');
                    await pool.query('UPDATE links SET last_error = $1 WHERE id = $2', [parseErr.message.substring(0, 250), linkId]);
                    if (io) io.emit('link:error', { linkId, error: parseErr.message });
                    return; // Exit job successfully so it doesn't retry, but don't overwrite DB
                }

                // Upsert metrics into link_metrics
                await pool.query(
                    `INSERT INTO link_metrics (link_id, views, likes, comments, updated_at)
                     VALUES ($1, $2, $3, $4, NOW())
                     ON CONFLICT (link_id) DO UPDATE SET
                       views = $2, likes = $3, comments = $4, updated_at = NOW()`,
                    [linkId, metrics.views, metrics.likes, metrics.comments]
                );

                // Update link title if parser returned one, and clear any existing errors
                await pool.query(
                    'UPDATE links SET title = COALESCE($1, title), last_error = NULL WHERE id = $2',
                    [title, linkId]
                );

                // Update monday_data JSONB so the dynamic table reflects parsed values
                // AND write back to Monday.com via API
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

                // Emit live update via Socket.IO
                if (io) {
                    io.emit('metrics:updated', { linkId, ...metrics, title });
                }

                logger.info({ linkId, metrics }, 'Parse-link job completed');
                return metrics;
            },
            {
                connection,
                concurrency: 3,
            }
        );

        worker.on('failed', (job, err) => {
            logger.error({ jobId: job?.id, err: err.message }, 'Parse-link worker failed');
        });

        worker.on('error', (err) => {
            logger.warn({ err: err.message }, 'Parse-link worker error (Redis issue)');
        });

        return worker;
    } catch (err) {
        logger.warn({ err: err.message }, 'Could not create parse-link worker');
        return null;
    }
}

module.exports = { createParseLinkWorker };
