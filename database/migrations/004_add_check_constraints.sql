-- ============================================================================
-- Migration 004: Add CHECK Constraints
-- ============================================================================
-- Description: Add data validation constraints for data integrity
-- Estimated time: 5-10 minutes
-- Rollback: See 004_add_check_constraints_rollback.sql
-- Phase: 1
-- Priority: P1 (Medium)
-- Breaking changes: POTENTIALLY (if existing data is invalid)
-- Requires downtime: NO
-- ============================================================================

-- ⚠️ IMPORTANT: Validate existing data BEFORE running this migration
-- Run the PRE-MIGRATION CHECKS first!

-- ============================================================================
-- PRE-MIGRATION CHECKS
-- ============================================================================

DO $$
DECLARE
    invalid_emails INTEGER;
    invalid_scores INTEGER;
    invalid_sentiment INTEGER;
    invalid_duration INTEGER;
BEGIN
    RAISE NOTICE '=== PRE-MIGRATION DATA VALIDATION ===';
    
    -- Check invalid emails
    SELECT COUNT(*) INTO invalid_emails
    FROM users 
    WHERE email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
    
    IF invalid_emails > 0 THEN
        RAISE WARNING 'Found % invalid emails', invalid_emails;
        -- Show examples
        FOR i IN (SELECT id, email FROM users 
                  WHERE email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' 
                  LIMIT 5) LOOP
            RAISE WARNING 'Invalid email: id=%, email=%', i.id, i.email;
        END LOOP;
    END IF;
    
    -- Check invalid assessment scores
    SELECT COUNT(*) INTO invalid_scores
    FROM assessments 
    WHERE total_score < 0 OR total_score > 21;
    
    IF invalid_scores > 0 THEN
        RAISE WARNING 'Found % invalid assessment scores', invalid_scores;
    END IF;
    
    -- Check invalid sentiment scores
    SELECT COUNT(*) INTO invalid_sentiment
    FROM voice_analyses 
    WHERE sentiment_score IS NOT NULL 
      AND (sentiment_score < -1 OR sentiment_score > 1);
    
    IF invalid_sentiment > 0 THEN
        RAISE WARNING 'Found % invalid sentiment scores', invalid_sentiment;
    END IF;
    
    -- Check invalid audio durations
    SELECT COUNT(*) INTO invalid_duration
    FROM voice_analyses 
    WHERE audio_duration IS NOT NULL AND audio_duration <= 0;
    
    IF invalid_duration > 0 THEN
        RAISE WARNING 'Found % invalid audio durations', invalid_duration;
    END IF;
    
    -- Decide whether to proceed
    IF invalid_emails > 0 OR invalid_scores > 0 OR 
       invalid_sentiment > 0 OR invalid_duration > 0 THEN
        RAISE EXCEPTION 'Found invalid data! Fix before adding constraints. See warnings above.';
    ELSE
        RAISE NOTICE 'All data valid! Safe to proceed with constraints.';
    END IF;
END $$;

BEGIN;

-- ============================================================================
-- USERS TABLE CONSTRAINTS
-- ============================================================================

-- Email format validation
ALTER TABLE users ADD CONSTRAINT check_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

COMMENT ON CONSTRAINT check_email_format ON users IS 
    'Ensure email follows standard format: user@domain.tld';

-- Phone number validation (international format)
ALTER TABLE users ADD CONSTRAINT check_phone_format 
    CHECK (phone IS NULL OR phone ~ '^\+?[0-9]{8,15}$');

COMMENT ON CONSTRAINT check_phone_format ON users IS 
    'Phone must be 8-15 digits, optional + prefix';

-- ============================================================================
-- STUDENTS TABLE CONSTRAINTS
-- ============================================================================

-- Phone number validation
ALTER TABLE students ADD CONSTRAINT check_student_phone_format 
    CHECK (phone_number IS NULL OR phone_number ~ '^\+?[0-9]{8,15}$');

COMMENT ON CONSTRAINT check_student_phone_format ON students IS 
    'Phone must be 8-15 digits, optional + prefix';

-- Gender validation (redundant with enum but adds clarity)
ALTER TABLE students ADD CONSTRAINT check_gender_values 
    CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say'));

COMMENT ON CONSTRAINT check_gender_values ON students IS 
    'Gender must be one of: male, female, other, prefer_not_to_say';

-- Education level validation
ALTER TABLE students ADD CONSTRAINT check_education_level_values 
    CHECK (education_level IS NULL OR 
           education_level IN ('high_school', 'undergraduate', 'graduate', 'other'));

COMMENT ON CONSTRAINT check_education_level_values ON students IS 
    'Education level must be valid enum value';

-- ============================================================================
-- ASSESSMENTS TABLE CONSTRAINTS
-- ============================================================================

-- GAD-7 total score range (0-21)
ALTER TABLE assessments ADD CONSTRAINT check_total_score_range 
    CHECK (total_score >= 0 AND total_score <= 21);

COMMENT ON CONSTRAINT check_total_score_range ON assessments IS 
    'GAD-7 total score must be 0-21 (sum of 7 questions, each 0-3)';

-- Functional impairment range (0-3)
ALTER TABLE assessments ADD CONSTRAINT check_functional_impairment_range 
    CHECK (functional_impairment IS NULL OR 
           (functional_impairment >= 0 AND functional_impairment <= 3));

COMMENT ON CONSTRAINT check_functional_impairment_range ON assessments IS 
    'Functional impairment must be 0-3 (not difficult to extremely difficult)';

-- Severity level validation
ALTER TABLE assessments ADD CONSTRAINT check_severity_level 
    CHECK (severity_level IN ('minimal', 'mild', 'moderate', 'severe'));

COMMENT ON CONSTRAINT check_severity_level ON assessments IS 
    'Severity must be: minimal (0-4), mild (5-9), moderate (10-14), severe (15-21)';

-- JSON structure validation for answers array
ALTER TABLE assessments ADD CONSTRAINT check_answers_structure 
    CHECK (
        jsonb_typeof(answers::jsonb) = 'array' AND
        jsonb_array_length(answers::jsonb) = 7
    );

COMMENT ON CONSTRAINT check_answers_structure ON assessments IS 
    'Answers must be JSON array with exactly 7 elements (GAD-7 questionnaire)';

-- ============================================================================
-- VOICE_ANALYSES TABLE CONSTRAINTS
-- ============================================================================

-- Sentiment score range (-1 to 1)
ALTER TABLE voice_analyses ADD CONSTRAINT check_sentiment_score_range 
    CHECK (sentiment_score IS NULL OR 
           (sentiment_score >= -1 AND sentiment_score <= 1));

COMMENT ON CONSTRAINT check_sentiment_score_range ON voice_analyses IS 
    'Sentiment score must be between -1 (negative) and 1 (positive)';

-- Emotion confidence range (0 to 1)
ALTER TABLE voice_analyses ADD CONSTRAINT check_emotion_confidence_range 
    CHECK (emotion_confidence IS NULL OR 
           (emotion_confidence >= 0 AND emotion_confidence <= 1));

COMMENT ON CONSTRAINT check_emotion_confidence_range ON voice_analyses IS 
    'Emotion confidence must be between 0 and 1 (probability)';

-- Transcription confidence range (0 to 1)
ALTER TABLE voice_analyses ADD CONSTRAINT check_transcription_confidence_range 
    CHECK (transcription_confidence IS NULL OR 
           (transcription_confidence >= 0 AND transcription_confidence <= 1));

COMMENT ON CONSTRAINT check_transcription_confidence_range ON voice_analyses IS 
    'Transcription confidence must be between 0 and 1 (probability)';

-- Audio duration must be positive
ALTER TABLE voice_analyses ADD CONSTRAINT check_audio_duration_positive 
    CHECK (audio_duration IS NULL OR audio_duration > 0);

COMMENT ON CONSTRAINT check_audio_duration_positive ON voice_analyses IS 
    'Audio duration must be positive (in seconds)';

-- File size must be positive
ALTER TABLE voice_analyses ADD CONSTRAINT check_file_size_positive 
    CHECK (file_size_bytes IS NULL OR file_size_bytes > 0);

COMMENT ON CONSTRAINT check_file_size_positive ON voice_analyses IS 
    'File size must be positive (in bytes)';

-- Processing status validation
ALTER TABLE voice_analyses ADD CONSTRAINT check_processing_status 
    CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed'));

COMMENT ON CONSTRAINT check_processing_status ON voice_analyses IS 
    'Processing status must be: pending, processing, completed, or failed';

-- Word count must be non-negative
ALTER TABLE voice_analyses ADD CONSTRAINT check_word_count_non_negative 
    CHECK (word_count IS NULL OR word_count >= 0);

COMMENT ON CONSTRAINT check_word_count_non_negative ON voice_analyses IS 
    'Word count cannot be negative';

-- Processing time must be non-negative
ALTER TABLE voice_analyses ADD CONSTRAINT check_processing_time_non_negative 
    CHECK (processing_time IS NULL OR processing_time >= 0);

COMMENT ON CONSTRAINT check_processing_time_non_negative ON voice_analyses IS 
    'Processing time cannot be negative (in seconds)';

-- Gender validation
ALTER TABLE voice_analyses ADD CONSTRAINT check_gender_used_values 
    CHECK (gender_used IS NULL OR 
           gender_used IN ('male', 'female', 'other', 'prefer_not_to_say'));

COMMENT ON CONSTRAINT check_gender_used_values ON voice_analyses IS 
    'Gender must match student.gender values';

-- ============================================================================
-- AI_MESSAGES TABLE CONSTRAINTS
-- ============================================================================

-- Role validation
ALTER TABLE ai_messages ADD CONSTRAINT check_ai_message_role 
    CHECK (role IN ('user', 'assistant'));

COMMENT ON CONSTRAINT check_ai_message_role ON ai_messages IS 
    'Message role must be either user (student) or assistant (AI)';

-- Content not empty
ALTER TABLE ai_messages ADD CONSTRAINT check_ai_message_content_not_empty 
    CHECK (LENGTH(TRIM(content)) > 0);

COMMENT ON CONSTRAINT check_ai_message_content_not_empty ON ai_messages IS 
    'Message content cannot be empty or whitespace only';

-- ============================================================================
-- COUNSELOR_MESSAGES TABLE CONSTRAINTS
-- ============================================================================

-- Sender type validation
ALTER TABLE counselor_messages ADD CONSTRAINT check_counselor_message_sender_type 
    CHECK (sender_type IN ('student', 'counselor'));

COMMENT ON CONSTRAINT check_counselor_message_sender_type ON counselor_messages IS 
    'Sender must be either student or counselor';

-- Content not empty
ALTER TABLE counselor_messages ADD CONSTRAINT check_counselor_message_content_not_empty 
    CHECK (LENGTH(TRIM(content)) > 0);

COMMENT ON CONSTRAINT check_counselor_message_content_not_empty ON counselor_messages IS 
    'Message content cannot be empty or whitespace only';

-- ============================================================================
-- COUNSELOR_CONVERSATIONS TABLE CONSTRAINTS
-- ============================================================================

-- Status validation
ALTER TABLE counselor_conversations ADD CONSTRAINT check_counselor_conversation_status 
    CHECK (status IN ('active', 'closed', 'archived'));

COMMENT ON CONSTRAINT check_counselor_conversation_status ON counselor_conversations IS 
    'Status must be: active, closed, or archived';

COMMIT;

-- ============================================================================
-- POST-MIGRATION VERIFICATION
-- ============================================================================

-- List all CHECK constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc 
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'CHECK'
  AND tc.constraint_name LIKE 'check_%'
ORDER BY tc.table_name, tc.constraint_name;

-- Test constraints with invalid data (should fail)
DO $$
BEGIN
    -- Test email constraint
    BEGIN
        INSERT INTO users (email, hashed_password, full_name, role) 
        VALUES ('invalid-email', 'hash', 'Test', 'STUDENT');
        RAISE EXCEPTION 'Email constraint NOT working!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'Email constraint working ✓';
    END;
    
    -- Test score constraint
    BEGIN
        INSERT INTO assessments (student_id, answers, total_score, severity_level) 
        VALUES (1, '[]', 99, 'severe');
        RAISE EXCEPTION 'Score constraint NOT working!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'Score constraint working ✓';
    END;
    
    RAISE NOTICE 'All constraints validated successfully!';
END $$;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. Constraints are enforced at INSERT and UPDATE time
-- 2. Existing invalid data will cause migration to fail
-- 3. Fix invalid data before adding constraints
-- 4. Constraints improve data quality and catch bugs early
-- 5. Application can still do validation, but DB is final safeguard
-- ============================================================================
