require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: 'postgresql://postgres:123Panda1313!@localhost:5432/social_stats'
});

(async () => {
    try {
        const res = await pool.query("SELECT id, platform, url FROM links WHERE platform IN ('instagram', 'facebook') AND url IS NOT NULL LIMIT 10");
        console.log(JSON.stringify(res.rows, null, 2));
    } catch (e) {
        console.error(e);
    } finally {
        await pool.end();
    }
})();
