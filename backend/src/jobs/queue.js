const { Queue } = require('bullmq');
const config = require('../config/env');
const logger = require('../logger');

const connection = { url: config.redisUrl };

// Lazy-initialised queues — may be null if Redis is unavailable or too old
let parseLinkQueue = null;
let refreshAllQueue = null;

try {
    parseLinkQueue = new Queue('parse-link', { connection });
    refreshAllQueue = new Queue('refresh-all', { connection });
} catch (err) {
    logger.warn({ err: err.message }, 'BullMQ queues not initialised (Redis may not be available)');
}

// --- Helper: add a parse job ---
async function enqueueParseLinkJob(linkId, url, platform) {
    if (!parseLinkQueue) {
        logger.warn({ linkId, platform }, 'Cannot enqueue job — Redis not available');
        return;
    }
    await parseLinkQueue.add('parse', { linkId, url, platform }, {
        attempts: 3,
        backoff: { type: 'exponential', delay: 5000 },
    });
    logger.info({ linkId, platform }, 'Enqueued parse-link job');
}

module.exports = { parseLinkQueue, refreshAllQueue, enqueueParseLinkJob, connection };
