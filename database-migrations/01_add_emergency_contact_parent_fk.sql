-- =====================================================
-- Migration: Add emergency_contact_parent_id Foreign Key
-- Date: 2025-10-03
-- Description: Replace emergency_contact fields with foreign key to parents table
-- =====================================================

-- BƯỚC 1: Thêm column mới emergency_contact_parent_id
-- Tạm thời cho phép NULL để migrate data
ALTER TABLE students 
ADD COLUMN emergency_contact_parent_id INTEGER;

-- BƯỚC 2: Thêm foreign key constraint
ALTER TABLE students
ADD CONSTRAINT fk_students_emergency_contact_parent
FOREIGN KEY (emergency_contact_parent_id) 
REFERENCES parents(id) 
ON DELETE SET NULL;  -- Nếu parent bị xóa, set NULL (không xóa student)

-- BƯỚC 3: Tạo index để tối ưu query
CREATE INDEX idx_students_emergency_contact_parent_id 
ON students(emergency_contact_parent_id);

-- =====================================================
-- OPTIONAL: Migrate existing data (nếu có data cũ)
-- =====================================================
-- Nếu bạn có data emergency_contact_name/phone hiện tại và muốn preserve:
-- 
-- 1. Tạo parent accounts tạm cho emergency contacts cũ:
/*
INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified, created_at)
SELECT 
    'parent_temp_' || s.id || '@ai4mind.temp' as email,  -- Email tạm
    '$2b$12$dummyhashfortemporaryparent123456789012345678' as hashed_password,  -- Temp password hash
    COALESCE(s.emergency_contact_name, 'Chưa cập nhật') as full_name,
    'parent' as role,
    false as is_active,  -- Inactive vì chưa verify
    false as is_verified,
    NOW() as created_at
FROM students s
WHERE s.emergency_contact_name IS NOT NULL
ON CONFLICT DO NOTHING;

-- 2. Tạo parent records:
INSERT INTO parents (user_id, phone_number)
SELECT 
    u.id as user_id,
    s.emergency_contact_phone as phone_number
FROM students s
JOIN users u ON u.email = 'parent_temp_' || s.id || '@ai4mind.temp'
WHERE s.emergency_contact_name IS NOT NULL
ON CONFLICT DO NOTHING;

-- 3. Link students với parents vừa tạo:
UPDATE students s
SET emergency_contact_parent_id = p.id
FROM parents p
JOIN users u ON p.user_id = u.id
WHERE u.email = 'parent_temp_' || s.id || '@ai4mind.temp';
*/

-- =====================================================
-- BƯỚC 4: Xóa các columns cũ (sau khi migrate xong)
-- =====================================================
-- CẢNH BÁO: Chỉ chạy sau khi đã migrate data và verify kỹ!
-- Uncomment 3 dòng dưới khi sẵn sàng:

-- ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_name;
-- ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_phone;
-- ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_relationship;

-- =====================================================
-- BƯỚC 5 (OPTIONAL): Set NOT NULL constraint
-- =====================================================
-- Sau khi tất cả students đều có emergency_contact_parent_id:
-- ALTER TABLE students 
-- ALTER COLUMN emergency_contact_parent_id SET NOT NULL;

-- =====================================================
-- Rollback script (nếu cần quay lại)
-- =====================================================
/*
-- Xóa constraint và column
ALTER TABLE students DROP CONSTRAINT IF EXISTS fk_students_emergency_contact_parent;
DROP INDEX IF EXISTS idx_students_emergency_contact_parent_id;
ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_parent_id;

-- Restore columns cũ nếu cần (chỉ nếu chưa DROP ở BƯỚC 4)
-- ALTER TABLE students ADD COLUMN emergency_contact_name VARCHAR(255);
-- ALTER TABLE students ADD COLUMN emergency_contact_phone VARCHAR(20);
-- ALTER TABLE students ADD COLUMN emergency_contact_relationship VARCHAR(100);
*/
