-- Lấy FULL password hash để so sánh
SELECT 
    email,
    hashed_password,
    LENGTH(hashed_password) as length
FROM users 
WHERE email = 'counselor1@ai4mind.com';

-- Expected hash (copy để so sánh):
-- $2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR.
-- Length phải = 60 chars chính xác
