/**
 * Migration runner — reads .sql files from migrations/ folder in order,
 * tracks which ones have been applied in a _migrations table.
 *
 * Usage: node src/db/migrate.js
 */

const fs = require('fs');
const path = require('path');
const pool = require('./pool');
const logger = require('../logger');

const MIGRATIONS_DIR = path.join(__dirname, 'migrations');

async function migrate() {
  const client = await pool.connect();

  try {
    // 1. Create _migrations tracking table if it doesn't exist
    await client.query(`
      CREATE TABLE IF NOT EXISTS _migrations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        applied_at TIMESTAMPTZ DEFAULT NOW()
      )
    `);

    // 2. Get list of already-applied migrations
    const applied = await client.query('SELECT name FROM _migrations ORDER BY name');
    const appliedSet = new Set(applied.rows.map(r => r.name));

    // 3. Read all .sql files from migrations/ folder, sorted by name
    const files = fs.readdirSync(MIGRATIONS_DIR)
      .filter(f => f.endsWith('.sql'))
      .sort();

    if (files.length === 0) {
      logger.info('No migration files found');
      return;
    }

    // 4. Run each unapplied migration in a transaction
    let count = 0;
    for (const file of files) {
      if (appliedSet.has(file)) {
        logger.debug({ file }, 'Already applied, skipping');
        continue;
      }

      const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf-8');

      await client.query('BEGIN');
      try {
        await client.query(sql);
        await client.query('INSERT INTO _migrations (name) VALUES ($1)', [file]);
        await client.query('COMMIT');
        logger.info({ file }, '✅ Applied migration');
        count++;
      } catch (err) {
        await client.query('ROLLBACK');
        logger.error({ file, error: err.message }, '❌ Migration failed, rolled back');
        throw err;
      }
    }

    if (count === 0) {
      logger.info('All migrations already applied — database is up to date');
    } else {
      logger.info({ count }, `Applied ${count} new migration(s)`);
    }
  } finally {
    client.release();
    await pool.end();
  }
}

// Run directly
if (require.main === module) {
  migrate()
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
}

module.exports = { migrate };
