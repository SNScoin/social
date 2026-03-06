-- Migration 009: Add dynamic Monday board columns
-- Store ALL column definitions and per-link column data as JSONB

ALTER TABLE monday_configs ADD COLUMN IF NOT EXISTS board_columns JSONB DEFAULT '[]';
ALTER TABLE links ADD COLUMN IF NOT EXISTS monday_data JSONB DEFAULT '{}';
