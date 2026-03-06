-- Migration 003: Create links table
-- Timestamp: 2026-03-05

CREATE TABLE IF NOT EXISTS links (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  platform VARCHAR(50) NOT NULL,
  title VARCHAR(500),
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
  monday_item_id VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
