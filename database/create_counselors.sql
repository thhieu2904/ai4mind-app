-- Create 3 counselor accounts with proper bcrypt hashed passwords
-- Password cho tất cả: Counselor123!

DO $$
DECLARE
    user1_id INTEGER;
    user2_id INTEGER;
    user3_id INTEGER;
BEGIN
    -- User 1: Dr. Nguyễn Văn A
    INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
    VALUES (
        'counselor1@ai4mind.com', 
        '$2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR.',
        'TS. Nguyễn Văn A', 
        'counselor', 
        TRUE, 
        TRUE
    )
    RETURNING id INTO user1_id;
    
    INSERT INTO counselors (user_id, license_number, specialization, years_of_experience, bio, is_available)
    VALUES (
        user1_id, 
        'PSY-001-2020', 
        'Tâm lý lâm sàng, Lo âu, Trầm cảm',
        8,
        'Chuyên gia tâm lý lâm sàng với 8 năm kinh nghiệm hỗ trợ sinh viên',
        TRUE
    );
    
    -- User 2: ThS. Trần Thị B
    INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
    VALUES (
        'counselor2@ai4mind.com', 
        '$2b$12$nOiTgPmKEDxbCizWJCbBn.ygPx9d1YerMfLdbhALoiIxR0QvZqKB2',
        'ThS. Trần Thị B', 
        'counselor', 
        TRUE, 
        TRUE
    )
    RETURNING id INTO user2_id;
    
    INSERT INTO counselors (user_id, license_number, specialization, years_of_experience, bio, is_available)
    VALUES (
        user2_id,
        'PSY-002-2018',
        'Tâm lý học tích cực, Stress management',
        5,
        'Tư vấn viên chuyên về stress và cân bằng cuộc sống',
        TRUE
    );
    
    -- User 3: ThS. Lê Văn C (không available - để test)
    INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
    VALUES (
        'counselor3@ai4mind.com', 
        '$2b$12$2JeDZu9Mo6BYzgIG73oyweryG/r8Y/3wWBWTw5cGPKrgQxcU05Epy',
        'ThS. Lê Văn C', 
        'counselor', 
        TRUE, 
        TRUE
    )
    RETURNING id INTO user3_id;
    
    INSERT INTO counselors (user_id, license_number, specialization, years_of_experience, bio, is_available)
    VALUES (
        user3_id,
        'PSY-003-2021',
        'Tâm lý trẻ em, Tâm lý giáo dục',
        3,
        'Chuyên gia tâm lý giáo dục',
        FALSE -- Không available
    );
    
    RAISE NOTICE 'Created 3 counselor accounts successfully';
    RAISE NOTICE 'Email: counselor1@ai4mind.com | Password: Counselor123!';
    RAISE NOTICE 'Email: counselor2@ai4mind.com | Password: Counselor123!';
    RAISE NOTICE 'Email: counselor3@ai4mind.com | Password: Counselor123!';
END $$;

-- Verify
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.role,
    c.license_number,
    c.specialization,
    c.years_of_experience,
    c.is_available
FROM users u
LEFT JOIN counselors c ON c.user_id = u.id
WHERE u.role = 'counselor'
ORDER BY u.id;
