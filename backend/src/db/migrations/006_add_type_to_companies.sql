-- Migration 006: Upgrade legacy schema to match expected structure
-- Timestamp: 2026-03-05
-- Fixes schema mismatches from pre-migration tables

-- 1. companies: add 'type' column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'companies' AND column_name = 'type'
    ) THEN
        ALTER TABLE companies ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'manual';
    END IF;
END $$;

-- 2. companies: add 'logo_url' for branding
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'companies' AND column_name = 'logo_url'
    ) THEN
        ALTER TABLE companies ADD COLUMN logo_url TEXT;
    END IF;
END $$;

-- 3. companies: add 'description' 
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'companies' AND column_name = 'description'
    ) THEN
        ALTER TABLE companies ADD COLUMN description TEXT;
    END IF;
END $$;

-- 4. companies: add 'updated_at'
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'companies' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE companies ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- 5. monday_configs: rename api_key → api_token if needed
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'monday_configs' AND column_name = 'api_key'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'monday_configs' AND column_name = 'api_token'
    ) THEN
        ALTER TABLE monday_configs RENAME COLUMN api_key TO api_token;
    END IF;
END $$;

-- 6. monday_configs: add missing columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monday_configs' AND column_name = 'workspace_name') THEN
        ALTER TABLE monday_configs ADD COLUMN workspace_name VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monday_configs' AND column_name = 'board_name') THEN
        ALTER TABLE monday_configs ADD COLUMN board_name VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monday_configs' AND column_name = 'source_column_id') THEN
        ALTER TABLE monday_configs ADD COLUMN source_column_id VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monday_configs' AND column_name = 'views_column_id') THEN
        ALTER TABLE monday_configs ADD COLUMN views_column_id VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monday_configs' AND column_name = 'likes_column_id') THEN
        ALTER TABLE monday_configs ADD COLUMN likes_column_id VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monday_configs' AND column_name = 'comments_column_id') THEN
        ALTER TABLE monday_configs ADD COLUMN comments_column_id VARCHAR(255);
    END IF;
END $$;

-- 7. monday_configs: make api_token NOT NULL if it isn't already
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'monday_configs' AND column_name = 'api_token' AND is_nullable = 'YES'
    ) THEN
        -- Set empty values to placeholder first
        UPDATE monday_configs SET api_token = 'MIGRATE_ME' WHERE api_token IS NULL;
        ALTER TABLE monday_configs ALTER COLUMN api_token SET NOT NULL;
    END IF;
END $$;

-- 8. monday_configs: add unique constraint on company_id if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'monday_configs'::regclass AND contype = 'u'
    ) THEN
        BEGIN
            ALTER TABLE monday_configs ADD CONSTRAINT monday_configs_company_id_key UNIQUE (company_id);
        EXCEPTION WHEN duplicate_object THEN
            NULL; -- already exists under different name
        END;
    END IF;
END $$;

-- 9. Ensure timestamps use TIMESTAMPTZ consistently
DO $$
BEGIN
    -- monday_configs.created_at
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'monday_configs' AND column_name = 'created_at'
        AND data_type = 'timestamp without time zone'
    ) THEN
        ALTER TABLE monday_configs ALTER COLUMN created_at TYPE TIMESTAMPTZ;
        ALTER TABLE monday_configs ALTER COLUMN created_at SET DEFAULT NOW();
    END IF;
    -- monday_configs.updated_at
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'monday_configs' AND column_name = 'updated_at'
        AND data_type = 'timestamp without time zone'
    ) THEN
        ALTER TABLE monday_configs ALTER COLUMN updated_at TYPE TIMESTAMPTZ;
        ALTER TABLE monday_configs ALTER COLUMN updated_at SET DEFAULT NOW();
    END IF;
END $$;
