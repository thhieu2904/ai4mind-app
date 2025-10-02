-- ========================================
-- SUPABASE ROW LEVEL SECURITY (RLS)
-- ========================================
-- 
-- Run these commands in Supabase SQL Editor
-- https://app.supabase.com/project/YOUR_PROJECT/sql
--
-- Purpose: Secure data access at database level
-- Date: October 1, 2025
--
-- ========================================

-- ========================================
-- 1. ENABLE RLS ON TABLES
-- ========================================

-- Enable RLS on students table
ALTER TABLE students ENABLE ROW LEVEL SECURITY;

-- Enable RLS on voice_analyses table  
ALTER TABLE voice_analyses ENABLE ROW LEVEL SECURITY;

-- Enable RLS on assessments table
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

-- Enable RLS on conversations table (if exists)
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;


-- ========================================
-- 2. DROP EXISTING POLICIES (if re-running)
-- ========================================

DROP POLICY IF EXISTS "Students can view own profile" ON students;
DROP POLICY IF EXISTS "Students can update own profile" ON students;
DROP POLICY IF EXISTS "Counselors can view assigned students" ON students;
DROP POLICY IF EXISTS "Admins can view all students" ON students;

DROP POLICY IF EXISTS "Students can view own voice analyses" ON voice_analyses;
DROP POLICY IF EXISTS "Service can insert voice analyses" ON voice_analyses;
DROP POLICY IF EXISTS "Students can delete own voice analyses" ON voice_analyses;
DROP POLICY IF EXISTS "Counselors can view assigned voice analyses" ON voice_analyses;
DROP POLICY IF EXISTS "Admins can view all voice analyses" ON voice_analyses;

DROP POLICY IF EXISTS "Students can view own assessments" ON assessments;
DROP POLICY IF EXISTS "Students can insert own assessments" ON assessments;
DROP POLICY IF EXISTS "Counselors can view assigned assessments" ON assessments;
DROP POLICY IF EXISTS "Admins can view all assessments" ON assessments;


-- ========================================
-- 3. STUDENTS TABLE POLICIES
-- ========================================

-- Policy: Students can view their own profile
CREATE POLICY "Students can view own profile"
ON students FOR SELECT
USING (
    -- Check if the user_id of the student matches the authenticated user
    -- Convert auth.uid() to integer to match user_id type
    user_id = (auth.jwt() ->> 'sub')::integer
);

-- Policy: Students can update their own profile
CREATE POLICY "Students can update own profile"
ON students FOR UPDATE
USING (
    user_id = (auth.jwt() ->> 'sub')::integer
)
WITH CHECK (
    user_id = (auth.jwt() ->> 'sub')::integer
);

-- Policy: Counselors can view assigned students
-- TODO: Implement student_counselor_assignments table first
CREATE POLICY "Counselors can view assigned students"
ON students FOR SELECT
USING (
    -- For now, allow all counselors to view all students
    -- TODO: Add assignment check
    auth.jwt() ->> 'role' = 'counselor'
    
    -- Future implementation:
    -- id IN (
    --     SELECT student_id FROM student_counselor_assignments
    --     WHERE counselor_id IN (
    --         SELECT id FROM counselors WHERE user_id = (auth.jwt() ->> 'sub')::integer
    --     )
    -- )
);

-- Policy: Admins can view all students
CREATE POLICY "Admins can view all students"
ON students FOR SELECT
USING (
    auth.jwt() ->> 'role' = 'admin'
);


-- ========================================
-- 4. VOICE_ANALYSES TABLE POLICIES
-- ========================================

-- Policy: Students can view their own voice analyses
CREATE POLICY "Students can view own voice analyses"
ON voice_analyses FOR SELECT
USING (
    -- Check if the student_id belongs to the authenticated user
    student_id IN (
        SELECT id FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Service role can insert voice analyses
-- This is for the API server to insert data
CREATE POLICY "Service can insert voice analyses"
ON voice_analyses FOR INSERT
WITH CHECK (
    -- Only service_role can insert
    auth.role() = 'service_role'
);

-- Policy: Students can delete their own voice analyses
CREATE POLICY "Students can delete own voice analyses"
ON voice_analyses FOR DELETE
USING (
    student_id IN (
        SELECT id FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Counselors can view assigned students' voice analyses
CREATE POLICY "Counselors can view assigned voice analyses"
ON voice_analyses FOR SELECT
USING (
    -- For now, allow all counselors
    -- TODO: Add assignment check
    auth.jwt() ->> 'role' = 'counselor'
);

-- Policy: Admins can view all voice analyses
CREATE POLICY "Admins can view all voice analyses"
ON voice_analyses FOR SELECT
USING (
    auth.jwt() ->> 'role' = 'admin'
);


-- ========================================
-- 5. ASSESSMENTS TABLE POLICIES
-- ========================================

-- Policy: Students can view their own assessments
CREATE POLICY "Students can view own assessments"
ON assessments FOR SELECT
USING (
    student_id IN (
        SELECT id FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Students can insert their own assessments
CREATE POLICY "Students can insert own assessments"
ON assessments FOR INSERT
WITH CHECK (
    student_id IN (
        SELECT id FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Counselors can view assigned students' assessments
CREATE POLICY "Counselors can view assigned assessments"
ON assessments FOR SELECT
USING (
    -- For now, allow all counselors
    -- TODO: Add assignment check
    auth.jwt() ->> 'role' = 'counselor'
);

-- Policy: Admins can view all assessments
CREATE POLICY "Admins can view all assessments"
ON assessments FOR SELECT
USING (
    auth.jwt() ->> 'role' = 'admin'
);


-- ========================================
-- 6. STORAGE POLICIES (for audio files)
-- ========================================

-- Enable RLS on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Drop existing storage policies (if re-running)
DROP POLICY IF EXISTS "Students can view own audio files" ON storage.objects;
DROP POLICY IF EXISTS "Students can upload to own folder" ON storage.objects;
DROP POLICY IF EXISTS "Students can delete own audio files" ON storage.objects;
DROP POLICY IF EXISTS "Service role full access" ON storage.objects;

-- Policy: Students can view their own audio files
CREATE POLICY "Students can view own audio files"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'audio-files'
    AND (storage.foldername(name))[1] IN (
        -- Get student_id from folder path
        SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Students can upload to their own folder
CREATE POLICY "Students can upload to own folder"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'audio-files'
    AND (storage.foldername(name))[1] IN (
        SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Students can delete their own audio files
CREATE POLICY "Students can delete own audio files"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'audio-files'
    AND (storage.foldername(name))[1] IN (
        SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
    )
);

-- Policy: Service role has full access (for API server operations)
CREATE POLICY "Service role full access"
ON storage.objects FOR ALL
USING (
    auth.role() = 'service_role'
);


-- ========================================
-- 7. VERIFICATION QUERIES
-- ========================================

-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('students', 'voice_analyses', 'assessments');

-- List all policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public'
AND tablename IN ('students', 'voice_analyses', 'assessments')
ORDER BY tablename, policyname;

-- List storage policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies 
WHERE schemaname = 'storage'
AND tablename = 'objects';


-- ========================================
-- 8. NOTES
-- ========================================

/*
IMPORTANT:
1. Run these commands in Supabase SQL Editor
2. Make sure to replace 'counselor', 'admin', 'student' with actual role values in JWT
3. TODO: Implement student_counselor_assignments table for proper counselor access
4. Service role key should NEVER be exposed to client-side code
5. Test policies with different user roles before deploying to production

TESTING RLS:
1. Create 2 test users (student1@test.com, student2@test.com)
2. Try to access student2's data using student1's token
3. Should get 403 Forbidden or empty results
4. Test with counselor and admin roles

JWT PAYLOAD SHOULD CONTAIN:
{
  "sub": "user-id",
  "email": "student@test.com",
  "role": "student",  // or "counselor", "admin"
  ...
}
*/
