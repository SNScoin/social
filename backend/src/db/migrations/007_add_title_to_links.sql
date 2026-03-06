-- Migration 007: Add title column to links table
ALTER TABLE links ADD COLUMN IF NOT EXISTS title TEXT;
