-- Migration 002: Create companies table
-- Timestamp: 2026-03-05

CREATE TABLE IF NOT EXISTS companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(20) NOT NULL DEFAULT 'manual' CHECK (type IN ('manual', 'monday')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
