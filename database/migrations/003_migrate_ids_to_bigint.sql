-- ============================================================================
-- Migration 003: Migrate IDs to BIGINT
-- ============================================================================
-- Description: Migrate all ID columns from INTEGER to BIGINT for scalability
-- Estimated time: 30-60 minutes (depends on data size)
-- Rollback: NOT RECOMMENDED (data corruption risk)
-- Phase: 1
-- Priority: P0 (High)
-- Breaking changes: YES (requires code update)
-- Requires downtime: YES (2-3 hours recommended)
-- ============================================================================

-- ⚠️⚠️⚠️ CRITICAL WARNINGS ⚠️⚠️⚠️
-- 1. BACKUP DATABASE BEFORE RUNNING THIS MIGRATION
-- 2. TEST ON STAGING ENVIRONMENT FIRST
-- 3. SCHEDULE MAINTENANCE WINDOW (2-3 hours)
-- 4. NOTIFY ALL USERS IN ADVANCE
-- 5. HAVE ROLLBACK PLAN READY
-- 6. UPDATE APPLICATION CODE BEFORE RUNNING (see docs)

-- ============================================================================
-- PRE-MIGRATION CHECKS
-- ============================================================================

DO $$
DECLARE
    users_count BIGINT;
    students_count BIGINT;
    assessments_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO users_count FROM users;
    SELECT COUNT(*) INTO students_count FROM students;
    SELECT COUNT(*) INTO assessments_count FROM assessments;
    
    RAISE NOTICE '=== PRE-MIGRATION DATA COUNT ===';
    RAISE NOTICE 'Users: %', users_count;
    RAISE NOTICE 'Students: %', students_count;
    RAISE NOTICE 'Assessments: %', assessments_count;
    
    -- Check if any ID is close to INTEGER limit
    IF users_count > 2000000000 THEN
        RAISE EXCEPTION 'Users count approaching INTEGER limit! Migration required ASAP.';
    END IF;
END $$;

BEGIN;

-- ============================================================================
-- STEP 1: DISABLE FOREIGN KEY CHECKS (for faster migration)
-- ============================================================================

ALTER TABLE students DROP CONSTRAINT IF EXISTS students_user_id_fkey;
ALTER TABLE students DROP CONSTRAINT IF EXISTS fk_students_emergency_contact_parent;
ALTER TABLE parents DROP CONSTRAINT IF EXISTS parents_user_id_fkey;
ALTER TABLE counselors DROP CONSTRAINT IF EXISTS counselors_user_id_fkey;
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS assessments_student_id_fkey;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS voice_analyses_student_id_fkey;
ALTER TABLE voice_analyses DROP CONSTRAINT IF EXISTS voice_analyses_assessment_id_fkey;
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_conversation_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_voice_analysis_id_fkey;
ALTER TABLE ai_conversations DROP CONSTRAINT IF EXISTS ai_conversations_student_id_fkey;
ALTER TABLE ai_conversations DROP CONSTRAINT IF EXISTS ai_conversations_latest_assessment_id_fkey;
ALTER TABLE ai_messages DROP CONSTRAINT IF EXISTS ai_messages_conversation_id_fkey;
ALTER TABLE ai_messages DROP CONSTRAINT IF EXISTS ai_messages_related_assessment_id_fkey;
ALTER TABLE counselor_conversations DROP CONSTRAINT IF EXISTS fk_counselor_conversations_student;
ALTER TABLE counselor_conversations DROP CONSTRAINT IF EXISTS fk_counselor_conversations_counselor;
ALTER TABLE counselor_messages DROP CONSTRAINT IF EXISTS fk_counselor_messages_conversation;
ALTER TABLE parent_consents DROP CONSTRAINT IF EXISTS parent_consents_student_id_fkey;
ALTER TABLE parent_consents DROP CONSTRAINT IF EXISTS parent_consents_parent_id_fkey;

RAISE NOTICE 'Foreign keys dropped';

-- ============================================================================
-- STEP 2: MIGRATE ROOT TABLE - USERS
-- ============================================================================

RAISE NOTICE 'Migrating users.id...';
ALTER TABLE users ALTER COLUMN id TYPE BIGINT;
ALTER SEQUENCE users_id_seq AS BIGINT;

-- ============================================================================
-- STEP 3: MIGRATE LEVEL 1 TABLES (depend on users)
-- ============================================================================

-- Students
RAISE NOTICE 'Migrating students...';
ALTER TABLE students ALTER COLUMN id TYPE BIGINT;
ALTER TABLE students ALTER COLUMN user_id TYPE BIGINT;
ALTER SEQUENCE students_id_seq AS BIGINT;

-- Parents
RAISE NOTICE 'Migrating parents...';
ALTER TABLE parents ALTER COLUMN id TYPE BIGINT;
ALTER TABLE parents ALTER COLUMN user_id TYPE BIGINT;
ALTER SEQUENCE parents_id_seq AS BIGINT;

-- Counselors
RAISE NOTICE 'Migrating counselors...';
ALTER TABLE counselors ALTER COLUMN id TYPE BIGINT;
ALTER TABLE counselors ALTER COLUMN user_id TYPE BIGINT;
ALTER SEQUENCE counselors_id_seq AS BIGINT;

-- Students emergency contact (depends on parents)
RAISE NOTICE 'Migrating students emergency contact...';
ALTER TABLE students ALTER COLUMN emergency_contact_parent_id TYPE BIGINT;

-- ============================================================================
-- STEP 4: MIGRATE LEVEL 2 TABLES (depend on students)
-- ============================================================================

-- Assessments
RAISE NOTICE 'Migrating assessments...';
ALTER TABLE assessments ALTER COLUMN id TYPE BIGINT;
ALTER TABLE assessments ALTER COLUMN student_id TYPE BIGINT;
ALTER SEQUENCE assessments_id_seq AS BIGINT;

-- Conversations
RAISE NOTICE 'Migrating conversations...';
ALTER TABLE conversations ALTER COLUMN id TYPE BIGINT;
ALTER TABLE conversations ALTER COLUMN student_id TYPE BIGINT;
ALTER SEQUENCE conversations_id_seq AS BIGINT;

-- AI conversations (already BIGINT id, just FKs)
RAISE NOTICE 'Migrating ai_conversations FKs...';
ALTER TABLE ai_conversations ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE ai_conversations ALTER COLUMN latest_assessment_id TYPE BIGINT;

-- Counselor conversations (already BIGINT id, just FKs)
RAISE NOTICE 'Migrating counselor_conversations FKs...';
ALTER TABLE counselor_conversations ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE counselor_conversations ALTER COLUMN counselor_id TYPE BIGINT;

-- Parent consents
RAISE NOTICE 'Migrating parent_consents...';
ALTER TABLE parent_consents ALTER COLUMN id TYPE BIGINT;
ALTER TABLE parent_consents ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE parent_consents ALTER COLUMN parent_id TYPE BIGINT;
ALTER SEQUENCE parent_consents_id_seq AS BIGINT;

-- ============================================================================
-- STEP 5: MIGRATE LEVEL 3 TABLES (depend on level 2)
-- ============================================================================

-- Voice analyses
RAISE NOTICE 'Migrating voice_analyses...';
ALTER TABLE voice_analyses ALTER COLUMN id TYPE BIGINT;
ALTER TABLE voice_analyses ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE voice_analyses ALTER COLUMN assessment_id TYPE BIGINT;
ALTER SEQUENCE voice_analyses_id_seq AS BIGINT;

-- Messages
RAISE NOTICE 'Migrating messages...';
ALTER TABLE messages ALTER COLUMN id TYPE BIGINT;
ALTER TABLE messages ALTER COLUMN conversation_id TYPE BIGINT;
ALTER TABLE messages ALTER COLUMN voice_analysis_id TYPE BIGINT;
ALTER SEQUENCE messages_id_seq AS BIGINT;

-- AI messages (already BIGINT)
RAISE NOTICE 'Migrating ai_messages FKs...';
ALTER TABLE ai_messages ALTER COLUMN conversation_id TYPE BIGINT;
ALTER TABLE ai_messages ALTER COLUMN related_assessment_id TYPE BIGINT;

-- Counselor messages (already BIGINT)
RAISE NOTICE 'Migrating counselor_messages FKs...';
ALTER TABLE counselor_messages ALTER COLUMN conversation_id TYPE BIGINT;

-- ============================================================================
-- STEP 6: RECREATE FOREIGN KEY CONSTRAINTS
-- ============================================================================

RAISE NOTICE 'Recreating foreign key constraints...';

-- Students
ALTER TABLE students 
    ADD CONSTRAINT students_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE students 
    ADD CONSTRAINT fk_students_emergency_contact_parent 
    FOREIGN KEY (emergency_contact_parent_id) REFERENCES parents(id) ON DELETE SET NULL;

-- Parents
ALTER TABLE parents 
    ADD CONSTRAINT parents_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Counselors
ALTER TABLE counselors 
    ADD CONSTRAINT counselors_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Assessments
ALTER TABLE assessments 
    ADD CONSTRAINT assessments_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Voice analyses
ALTER TABLE voice_analyses 
    ADD CONSTRAINT voice_analyses_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE voice_analyses 
    ADD CONSTRAINT voice_analyses_assessment_id_fkey 
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE;

-- Conversations
ALTER TABLE conversations 
    ADD CONSTRAINT conversations_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Messages
ALTER TABLE messages 
    ADD CONSTRAINT messages_conversation_id_fkey 
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
ALTER TABLE messages 
    ADD CONSTRAINT messages_voice_analysis_id_fkey 
    FOREIGN KEY (voice_analysis_id) REFERENCES voice_analyses(id) ON DELETE SET NULL;

-- AI conversations
ALTER TABLE ai_conversations 
    ADD CONSTRAINT ai_conversations_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE ai_conversations 
    ADD CONSTRAINT ai_conversations_latest_assessment_id_fkey 
    FOREIGN KEY (latest_assessment_id) REFERENCES assessments(id) ON DELETE SET NULL;

-- AI messages
ALTER TABLE ai_messages 
    ADD CONSTRAINT ai_messages_conversation_id_fkey 
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id) ON DELETE CASCADE;
ALTER TABLE ai_messages 
    ADD CONSTRAINT ai_messages_related_assessment_id_fkey 
    FOREIGN KEY (related_assessment_id) REFERENCES assessments(id) ON DELETE SET NULL;

-- Counselor conversations
ALTER TABLE counselor_conversations 
    ADD CONSTRAINT fk_counselor_conversations_student 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE counselor_conversations 
    ADD CONSTRAINT fk_counselor_conversations_counselor 
    FOREIGN KEY (counselor_id) REFERENCES counselors(id) ON DELETE CASCADE;

-- Counselor messages
ALTER TABLE counselor_messages 
    ADD CONSTRAINT fk_counselor_messages_conversation 
    FOREIGN KEY (conversation_id) REFERENCES counselor_conversations(id) ON DELETE CASCADE;

-- Parent consents
ALTER TABLE parent_consents 
    ADD CONSTRAINT parent_consents_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE parent_consents 
    ADD CONSTRAINT parent_consents_parent_id_fkey 
    FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE;

RAISE NOTICE 'Foreign keys recreated';

COMMIT;

-- ============================================================================
-- POST-MIGRATION VERIFICATION
-- ============================================================================

DO $$
DECLARE
    r RECORD;
    mismatched_count INTEGER := 0;
BEGIN
    RAISE NOTICE '=== POST-MIGRATION VERIFICATION ===';
    
    -- Check all ID columns are now BIGINT
    FOR r IN (
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
          AND column_name LIKE '%id%'
          AND table_name NOT IN ('alembic_version', 'medical_centers')
        ORDER BY table_name, column_name
    ) LOOP
        IF r.data_type != 'bigint' THEN
            RAISE WARNING 'MISMATCH: %.% is %', r.table_name, r.column_name, r.data_type;
            mismatched_count := mismatched_count + 1;
        ELSE
            RAISE NOTICE 'OK: %.% is BIGINT', r.table_name, r.column_name;
        END IF;
    END LOOP;
    
    IF mismatched_count > 0 THEN
        RAISE EXCEPTION 'Found % columns that are not BIGINT!', mismatched_count;
    ELSE
        RAISE NOTICE 'SUCCESS: All ID columns migrated to BIGINT';
    END IF;
    
    -- Verify foreign keys
    RAISE NOTICE '';
    RAISE NOTICE '=== FOREIGN KEY VERIFICATION ===';
    FOR r IN (
        SELECT conname, conrelid::regclass, confrelid::regclass
        FROM pg_constraint
        WHERE contype = 'f'
          AND connamespace = 'public'::regnamespace
        ORDER BY conrelid::regclass::text
    ) LOOP
        RAISE NOTICE 'FK: % on % references %', r.conname, r.conrelid, r.confrelid;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '=== MIGRATION COMPLETE ===';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Update application code (SQLAlchemy models)';
    RAISE NOTICE '2. Deploy new application code';
    RAISE NOTICE '3. Test all CRUD operations';
    RAISE NOTICE '4. Monitor for 48 hours';
END $$;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. This migration is IRREVERSIBLE without full database restore
-- 2. All sequences are also migrated to BIGINT
-- 3. Foreign keys are recreated with proper CASCADE rules
-- 4. Application code MUST be updated to use BigInteger in SQLAlchemy
-- 5. No data is lost, only column types are changed
-- 6. Index on id columns are automatically updated
-- ============================================================================
