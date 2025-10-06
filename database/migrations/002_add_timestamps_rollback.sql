-- ============================================================================
-- Migration 002 Rollback: Remove Timestamps
-- ============================================================================
-- Description: Remove timestamps and triggers added in 002_add_timestamps.sql
-- ============================================================================

BEGIN;

-- Remove triggers
DROP TRIGGER IF EXISTS update_counselors_updated_at ON counselors;
DROP TRIGGER IF EXISTS update_parents_updated_at ON parents;
DROP TRIGGER IF EXISTS update_parent_consents_updated_at ON parent_consents;
DROP TRIGGER IF EXISTS update_counselor_conversations_updated_at ON counselor_conversations;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- Remove function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Remove columns
ALTER TABLE counselors 
    DROP COLUMN IF EXISTS created_at,
    DROP COLUMN IF EXISTS updated_at;

ALTER TABLE parents 
    DROP COLUMN IF EXISTS created_at,
    DROP COLUMN IF EXISTS updated_at;

ALTER TABLE parent_consents 
    DROP COLUMN IF EXISTS created_at,
    DROP COLUMN IF EXISTS updated_at;

ALTER TABLE counselor_conversations 
    DROP COLUMN IF EXISTS updated_at;

COMMIT;
