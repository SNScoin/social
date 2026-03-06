/**
 * Refresh All worker — scheduled cron job that re-parses all links.
 */

const { Worker } = require('bullmq');
const { connection, enqueueParseLinkJob } = require('./queue');
const pool = require('../db/pool');
const logger = require('../logger');

function createRefreshAllWorker() {
    try {
        const worker = new Worker(
            'refresh-all',
            async () => {
                logger.info('Starting refresh-all job');
                const result = await pool.query('SELECT id, url, platform FROM links');
                const links = result.rows;
                logger.info({ count: links.length }, 'Enqueuing parse jobs for all links');

                for (const link of links) {
                    await enqueueParseLinkJob(link.id, link.url, link.platform);
                }

                return { processed: links.length };
            },
            { connection }
        );

        worker.on('failed', (job, err) => {
            logger.error({ jobId: job?.id, err: err.message }, 'Refresh-all worker failed');
        });

        worker.on('error', (err) => {
            logger.warn({ err: err.message }, 'Refresh-all worker error (Redis issue)');
        });

        return worker;
    } catch (err) {
        logger.warn({ err: err.message }, 'Could not create refresh-all worker');
        return null;
    }
}

module.exports = { createRefreshAllWorker };
