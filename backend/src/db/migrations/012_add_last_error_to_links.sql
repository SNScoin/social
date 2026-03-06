-- Migration 012: Add last_error to links
-- Timestamp: 2026-03-06

ALTER TABLE links ADD COLUMN IF NOT EXISTS last_error VARCHAR(255);
