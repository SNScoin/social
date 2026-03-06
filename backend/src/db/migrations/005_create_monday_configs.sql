-- Migration 005: Create monday_configs table
-- Timestamp: 2026-03-05

CREATE TABLE IF NOT EXISTS monday_configs (
  id SERIAL PRIMARY KEY,
  company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE UNIQUE,
  api_token TEXT NOT NULL,
  workspace_id VARCHAR(255),
  workspace_name VARCHAR(255),
  board_id VARCHAR(255),
  board_name VARCHAR(255),
  source_column_id VARCHAR(255),
  views_column_id VARCHAR(255),
  likes_column_id VARCHAR(255),
  comments_column_id VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
