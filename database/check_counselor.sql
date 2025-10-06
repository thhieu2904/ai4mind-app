-- Kiểm tra counselor user có tồn tại không và password hash có đúng không

SELECT 
    u.id,
    u.email,
    u.full_name,
    u.role,
    u.is_active,
    u.is_verified,
    LENGTH(u.hashed_password) as hash_length,
    SUBSTRING(u.hashed_password, 1, 10) as hash_prefix,
    c.license_number,
    c.specialization,
    c.is_available
FROM users u
LEFT JOIN counselors c ON c.user_id = u.id
WHERE u.email = 'counselor1@ai4mind.com';

-- Expected results:
-- hash_length should be 60
-- hash_prefix should be '$2b$12$Yb1'
-- If no results → User chưa được tạo, cần chạy create_counselors.sql
-- If hash_length != 60 → Hash bị lỗi, cần chạy lại với hash đúng
