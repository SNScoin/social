const { Pool } = require('pg');
const config = require('../config/env');
const logger = require('../logger');

const pool = new Pool({
    connectionString: config.databaseUrl,
});

pool.on('error', (err) => {
    logger.error('Unexpected database pool error', err);
});

module.exports = pool;
