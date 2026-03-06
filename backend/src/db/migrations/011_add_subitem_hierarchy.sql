-- Migration 011: Add parent-child link relationship for Monday.com sub-items
-- Parent items are profiles, sub-items are actual posts/videos

ALTER TABLE links ADD COLUMN IF NOT EXISTS parent_monday_item_id VARCHAR(255);
ALTER TABLE links ADD COLUMN IF NOT EXISTS is_subitem BOOLEAN DEFAULT FALSE;
