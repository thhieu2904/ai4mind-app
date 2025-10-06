-- Fix: Chỉ chuẩn hóa counselor role về lowercase
-- Các role khác (STUDENT, PARENT, ADMIN) giữ nguyên

-- 1. Kiểm tra counselor roles hiện tại
SELECT email, role, full_name
FROM users
WHERE role ILIKE '%counselor%'
ORDER BY role;

-- 2. Update chỉ counselor về lowercase
UPDATE users 
SET role = 'counselor' 
WHERE role = 'COUNSELOR' OR role = 'Counselor';

-- 3. Verify
SELECT email, role, full_name
FROM users
WHERE role = 'counselor'
ORDER BY email;

-- Expected: Tất cả counselor roles đều là 'counselor' (lowercase)
