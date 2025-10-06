-- FIX: Update password hash cho counselor1 với hash CHÍNH XÁC

UPDATE users 
SET hashed_password = '$2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR.'
WHERE email = 'counselor1@ai4mind.com';

-- Verify
SELECT 
    email,
    LENGTH(hashed_password) as hash_length,
    hashed_password
FROM users 
WHERE email = 'counselor1@ai4mind.com';

-- Expected: hash_length = 60
