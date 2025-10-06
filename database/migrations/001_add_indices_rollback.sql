-- ============================================================================
-- Migration 001 Rollback: Remove Performance Indices
-- ============================================================================
-- Description: Remove all indices added in 001_add_indices.sql
-- Use this if you need to rollback the index addition
-- ============================================================================

BEGIN;

-- Students indices
DROP INDEX IF EXISTS idx_students_user_id;

-- Assessments indices
DROP INDEX IF EXISTS idx_assessments_student_created;
DROP INDEX IF EXISTS idx_assessments_severity;

-- Voice analyses indices
DROP INDEX IF EXISTS idx_voice_analyses_status;
DROP INDEX IF EXISTS idx_voice_analyses_student_created;
DROP INDEX IF EXISTS idx_voice_analyses_assessment;

-- AI conversations indices
DROP INDEX IF EXISTS idx_ai_conversations_student_active;
DROP INDEX IF EXISTS idx_ai_conversations_last_message;

-- AI messages indices
DROP INDEX IF EXISTS idx_ai_messages_conversation_created;

-- Counselor conversations indices
DROP INDEX IF EXISTS idx_counselor_conversations_student;
DROP INDEX IF EXISTS idx_counselor_conversations_counselor;
DROP INDEX IF EXISTS idx_counselor_conversations_last_message;

-- Counselor messages indices
DROP INDEX IF EXISTS idx_counselor_messages_conversation_created;
DROP INDEX IF EXISTS idx_counselor_messages_unread;

-- Full-text search indices
DROP INDEX IF EXISTS idx_users_email_gin;
DROP INDEX IF EXISTS idx_voice_analyses_transcription_fts;

COMMIT;

-- Verify removal
SELECT indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND indexname LIKE 'idx_%';
