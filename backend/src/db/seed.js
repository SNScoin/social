/**
 * Database seed — creates test data for development.
 * Run with: node src/db/seed.js
 */

const bcrypt = require('bcryptjs');
const pool = require('./pool');
const logger = require('../logger');

async function seed() {
    try {
        // Create test user
        const hashedPassword = await bcrypt.hash('password123', 10);
        const userResult = await pool.query(
            `INSERT INTO users (username, email, hashed_password, display_name)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (email) DO NOTHING
       RETURNING id`,
            ['admin', 'admin@test.com', hashedPassword, 'Admin User']
        );

        const userId = userResult.rows[0]?.id;
        if (!userId) {
            logger.info('Test user already exists, skipping seed');
            return;
        }

        // Create test company (manual)
        await pool.query(
            `INSERT INTO companies (name, owner_id, type)
       VALUES ($1, $2, $3)`,
            ['Test Company', userId, 'manual']
        );

        logger.info('Seed completed: admin@test.com / password123');
    } catch (err) {
        logger.error('Seed failed', err);
        throw err;
    } finally {
        await pool.end();
    }
}

if (require.main === module) {
    seed()
        .then(() => process.exit(0))
        .catch(() => process.exit(1));
}

module.exports = { seed };
