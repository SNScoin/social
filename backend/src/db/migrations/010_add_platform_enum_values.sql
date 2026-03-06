-- Migration 010: Add additional platform enum values
-- Support LinkedIn, X, and unknown platforms for Monday.com sync

ALTER TYPE platform ADD VALUE IF NOT EXISTS 'linkedin';
ALTER TYPE platform ADD VALUE IF NOT EXISTS 'x';
ALTER TYPE platform ADD VALUE IF NOT EXISTS 'unknown';
