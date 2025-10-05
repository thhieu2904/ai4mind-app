-- Fix: Chuẩn hóa TẤT CẢ role values trong database về lowercase
-- Vì Python enum định nghĩa: student, parent, counselor, admin (lowercase)

-- 1. Kiểm tra các role values hiện tại
SELECT role, COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

-- 2. Update TẤT CẢ về lowercase (cast to text first for enum)
UPDATE users SET role = LOWER(role::text)::userrole;

-- 3. Verify sau khi update
SELECT role, COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

-- Expected: Chỉ thấy lowercase values: student, parent, counselor, admin
-- Không còn STUDENT, PARENT, COUNSELOR, ADMIN

