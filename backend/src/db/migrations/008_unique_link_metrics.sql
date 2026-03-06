-- Migration 008: Add UNIQUE constraint on link_metrics.link_id
-- Required for ON CONFLICT (link_id) upsert pattern used by parser worker
CREATE UNIQUE INDEX IF NOT EXISTS link_metrics_link_id_unique ON link_metrics (link_id);
