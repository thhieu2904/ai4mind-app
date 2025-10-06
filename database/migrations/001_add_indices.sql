-- ============================================================================
-- Migration 001: Add Performance Indices
-- ============================================================================
-- Description: Add strategic indices to improve query performance
-- Estimated time: 5-10 minutes (depends on data size)
-- Rollback: See 001_add_indices_rollback.sql
-- Phase: 1
-- Priority: P0 (High)
-- Breaking changes: NO
-- Requires downtime: NO
-- ============================================================================

-- IMPORTANT: Use CONCURRENTLY to avoid locking tables during index creation
-- This allows normal operations to continue while indices are being built

BEGIN;

-- ============================================================================
-- 1. STUDENTS INDICES
-- ============================================================================

-- Fast lookup by user_id (used in auth and profile queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_students_user_id 
    ON students(user_id);

COMMENT ON INDEX idx_students_user_id IS 
    'Fast lookup of student profile by user_id';

-- ============================================================================
-- 2. ASSESSMENTS INDICES
-- ============================================================================

-- Get all assessments for a student, sorted by date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assessments_student_created 
    ON assessments(student_id, created_at DESC);

COMMENT ON INDEX idx_assessments_student_created IS 
    'Get student assessment history sorted by date';

-- Filter assessments by severity level
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assessments_severity 
    ON assessments(severity_level);

COMMENT ON INDEX idx_assessments_severity IS 
    'Filter assessments by severity (for counselor dashboard)';

-- ============================================================================
-- 3. VOICE ANALYSES INDICES
-- ============================================================================

-- Find pending/processing voice analyses (for background worker)
-- Partial index: only index non-completed records
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_status 
    ON voice_analyses(processing_status) 
    WHERE processing_status != 'completed';

COMMENT ON INDEX idx_voice_analyses_status IS 
    'Find pending/processing voice analyses (partial index for efficiency)';

-- Get all voice analyses for a student, sorted by date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_student_created 
    ON voice_analyses(student_id, created_at DESC);

COMMENT ON INDEX idx_voice_analyses_student_created IS 
    'Get student voice analysis history sorted by date';

-- Fast lookup voice analysis by assessment
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_assessment 
    ON voice_analyses(assessment_id);

COMMENT ON INDEX idx_voice_analyses_assessment IS 
    'Find voice analyses for a specific assessment';

-- ============================================================================
-- 4. AI CONVERSATIONS INDICES
-- ============================================================================

-- Get active conversations for a student
-- Partial index: only index active conversations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_conversations_student_active 
    ON ai_conversations(student_id, is_active) 
    WHERE is_active = true;

COMMENT ON INDEX idx_ai_conversations_student_active IS 
    'Find active AI conversations for a student';

-- Sort conversations by last activity
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_conversations_last_message 
    ON ai_conversations(last_message_at DESC);

COMMENT ON INDEX idx_ai_conversations_last_message IS 
    'Sort conversations by recent activity';

-- ============================================================================
-- 5. AI MESSAGES INDICES
-- ============================================================================

-- Get all messages in a conversation, sorted by time
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_messages_conversation_created 
    ON ai_messages(conversation_id, created_at);

COMMENT ON INDEX idx_ai_messages_conversation_created IS 
    'Get conversation message history in chronological order';

-- ============================================================================
-- 6. COUNSELOR CONVERSATIONS INDICES
-- ============================================================================

-- Find conversations for a student by status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_conversations_student 
    ON counselor_conversations(student_id, status);

COMMENT ON INDEX idx_counselor_conversations_student IS 
    'Find student conversations by status';

-- Find conversations for a counselor by status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_conversations_counselor 
    ON counselor_conversations(counselor_id, status);

COMMENT ON INDEX idx_counselor_conversations_counselor IS 
    'Find counselor conversations by status';

-- Sort conversations by last activity
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_conversations_last_message 
    ON counselor_conversations(last_message_at DESC);

COMMENT ON INDEX idx_counselor_conversations_last_message IS 
    'Sort counselor conversations by recent activity';

-- ============================================================================
-- 7. COUNSELOR MESSAGES INDICES
-- ============================================================================

-- Get all messages in a conversation, sorted by time
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_messages_conversation_created 
    ON counselor_messages(conversation_id, created_at);

COMMENT ON INDEX idx_counselor_messages_conversation_created IS 
    'Get counselor conversation message history in chronological order';

-- Find unread messages in a conversation
-- Partial index: only index unread messages
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_messages_unread 
    ON counselor_messages(conversation_id, is_read) 
    WHERE is_read = false;

COMMENT ON INDEX idx_counselor_messages_unread IS 
    'Find unread messages in a conversation (for notification badge)';

-- ============================================================================
-- 8. FULL-TEXT SEARCH INDICES
-- ============================================================================

-- Enable pg_trgm extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Fast email search (for user lookup)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_gin 
    ON users USING gin(email gin_trgm_ops);

COMMENT ON INDEX idx_users_email_gin IS 
    'Fast fuzzy email search using trigram similarity';

-- Full-text search on voice transcriptions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_transcription_fts 
    ON voice_analyses USING gin(to_tsvector('english', COALESCE(transcription, '')));

COMMENT ON INDEX idx_voice_analyses_transcription_fts IS 
    'Full-text search on voice transcriptions';

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check all created indices
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Check index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. CONCURRENTLY keyword allows table to remain accessible during creation
-- 2. Partial indices (WHERE clause) save space and improve performance
-- 3. Multi-column indices: order matters! Most selective column should be first
-- 4. Monitor index usage with pg_stat_user_indexes after deployment
-- 5. Drop unused indices to save disk space and write performance
-- ============================================================================
