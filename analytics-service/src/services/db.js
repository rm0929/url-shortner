const { Pool } = require("pg");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function initDB() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS click_events (
      id SERIAL PRIMARY KEY,
      short_code VARCHAR(20) NOT NULL,
      clicked_at TIMESTAMPTZ NOT NULL,
      cache_hit BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_click_events_short_code
      ON click_events(short_code);
  `);
  console.log("[db] Tables ready");
}

async function recordClick({ short_code, timestamp, cache_hit }) {
  await pool.query(
    `INSERT INTO click_events (short_code, clicked_at, cache_hit)
     VALUES ($1, $2, $3)`,
    [short_code, timestamp, cache_hit]
  );
}

async function getStats(short_code) {
  const result = await pool.query(
    `SELECT
       COUNT(*)::int AS total_clicks,
       SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END)::int AS cache_hits,
       MIN(clicked_at) AS first_click,
       MAX(clicked_at) AS last_click
     FROM click_events
     WHERE short_code = $1`,
    [short_code]
  );
  return result.rows[0];
}

module.exports = { pool, initDB, recordClick, getStats };
