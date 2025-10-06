-- ============================================================================
-- Migration 002: Add Timestamps
-- ============================================================================
-- Description: Add created_at and updated_at to tables missing them
-- Estimated time: 1-2 minutes
-- Rollback: See 002_add_timestamps_rollback.sql
-- Phase: 1
-- Priority: P1 (Medium)
-- Breaking changes: NO (only additions)
-- Requires downtime: NO
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. ADD COLUMNS
-- ============================================================================

-- Counselors table
ALTER TABLE counselors 
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN counselors.created_at IS 'When the counselor profile was created';
COMMENT ON COLUMN counselors.updated_at IS 'Last update timestamp (auto-updated by trigger)';

-- Parents table
ALTER TABLE parents 
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN parents.created_at IS 'When the parent profile was created';
COMMENT ON COLUMN parents.updated_at IS 'Last update timestamp (auto-updated by trigger)';

-- Parent consents table
ALTER TABLE parent_consents 
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN parent_consents.created_at IS 'When the consent was created';
COMMENT ON COLUMN parent_consents.updated_at IS 'Last update timestamp (auto-updated by trigger)';

-- Counselor conversations table
ALTER TABLE counselor_conversations 
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN counselor_conversations.updated_at IS 'Last update timestamp (auto-updated by trigger)';

-- ============================================================================
-- 2. CREATE TRIGGER FUNCTION
-- ============================================================================

-- Function to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column IS 
    'Automatically update updated_at column on row update';

-- ============================================================================
-- 3. CREATE TRIGGERS
-- ============================================================================

-- Trigger for counselors
DROP TRIGGER IF EXISTS update_counselors_updated_at ON counselors;
CREATE TRIGGER update_counselors_updated_at 
    BEFORE UPDATE ON counselors 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for parents
DROP TRIGGER IF EXISTS update_parents_updated_at ON parents;
CREATE TRIGGER update_parents_updated_at 
    BEFORE UPDATE ON parents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for parent_consents
DROP TRIGGER IF EXISTS update_parent_consents_updated_at ON parent_consents;
CREATE TRIGGER update_parent_consents_updated_at 
    BEFORE UPDATE ON parent_consents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for counselor_conversations
DROP TRIGGER IF EXISTS update_counselor_conversations_updated_at ON counselor_conversations;
CREATE TRIGGER update_counselor_conversations_updated_at 
    BEFORE UPDATE ON counselor_conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Also add to other tables that already have updated_at but no trigger
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check columns were added
SELECT 
    table_name,
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name IN ('created_at', 'updated_at')
ORDER BY table_name, column_name;

-- Check triggers were created
SELECT 
    trigger_name,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_name LIKE '%updated_at%'
ORDER BY event_object_table;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. created_at has DEFAULT NOW() so existing rows get current timestamp
-- 2. updated_at is NULL initially for existing rows (expected behavior)
-- 3. updated_at will be auto-populated on first UPDATE
-- 4. Triggers fire BEFORE UPDATE to ensure timestamp is set
-- ============================================================================
