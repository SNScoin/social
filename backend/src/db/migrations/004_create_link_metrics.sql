-- Migration 004: Create link_metrics table
-- Timestamp: 2026-03-05

CREATE TABLE IF NOT EXISTS link_metrics (
  id SERIAL PRIMARY KEY,
  link_id INTEGER REFERENCES links(id) ON DELETE CASCADE UNIQUE,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
