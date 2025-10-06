-- ============================================================================
-- Migration 004 Rollback: Remove CHECK Constraints
-- ============================================================================
-- Description: Remove all CHECK constraints added in 004
-- ============================================================================

BEGIN;

-- Users
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_email_format;
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_phone_format;

-- Students
ALTER TABLE students DROP CONSTRAINT IF EXISTS check_student_phone_format;
ALTER TABLE students DROP CONSTRAINT IF EXISTS check_gender_values;
ALTER TABLE students DROP CONSTRAINT IF EXISTS check_education_level_values;

-- Assessments
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS check_total_score_range;
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS check_functional_impairment_range;
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS check_severity_level;
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS check_answers_structure;

-- Voice analyses
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_sentiment_score_range;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_emotion_confidence_range;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_transcription_confidence_range;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_audio_duration_positive;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_file_size_positive;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_processing_status;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_word_count_non_negative;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_processing_time_non_negative;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS check_gender_used_values;

-- AI messages
ALTER TABLE ai_messages DROP CONSTRAINT IF EXISTS check_ai_message_role;
ALTER TABLE ai_messages DROP CONSTRAINT IF EXISTS check_ai_message_content_not_empty;

-- Counselor messages
ALTER TABLE counselor_messages DROP CONSTRAINT IF EXISTS check_counselor_message_sender_type;
ALTER TABLE counselor_messages DROP CONSTRAINT IF EXISTS check_counselor_message_content_not_empty;

-- Counselor conversations
ALTER TABLE counselor_conversations DROP CONSTRAINT IF EXISTS check_counselor_conversation_status;

COMMIT;

-- Verify removal
SELECT 
    table_name,
    constraint_name
FROM information_schema.table_constraints
WHERE table_schema = 'public'
  AND constraint_type = 'CHECK'
  AND constraint_name LIKE 'check_%';
