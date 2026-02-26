-- ============================================================
-- AI4Mind - FULL DATABASE INITIALIZATION (FRESH START)
-- ============================================================
-- Chạy file này trong Supabase SQL Editor để tạo toàn bộ schema
-- URL: https://supabase.com/dashboard/project/<YOUR_PROJECT_ID>/sql
--
-- Thứ tự: Schema → Tables → Indexes → RLS → Seed Data
-- ============================================================


-- ============================================================
-- 0. EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";        -- gen_random_uuid(), crypt()


-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

-- Xóa nếu đã tồn tại (để chạy lại được)
DROP TYPE IF EXISTS userrole CASCADE;

CREATE TYPE userrole AS ENUM (
    'STUDENT',
    'PARENT',
    'COUNSELOR',
    'ADMIN'
);


-- ============================================================
-- 2. BẢNG USERS (Base authentication)
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id                SERIAL PRIMARY KEY,
    email             VARCHAR(255) UNIQUE NOT NULL,
    hashed_password   VARCHAR(255) NOT NULL,
    full_name         VARCHAR(255) NOT NULL,
    phone             VARCHAR(20),
    role              userrole NOT NULL,
    is_active         BOOLEAN DEFAULT TRUE,
    is_verified       BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE,
    last_login        TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_email  ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role   ON users (role);


-- ============================================================
-- 3. BẢNG PARENTS (trước students vì students FK → parents)
-- ============================================================

CREATE TABLE IF NOT EXISTS parents (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone_number    VARCHAR(20),
    address         TEXT,
    occupation      VARCHAR(255)
);


-- ============================================================
-- 4. BẢNG STUDENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS students (
    id                          SERIAL PRIMARY KEY,
    user_id                     INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_code                VARCHAR(20) UNIQUE,
    date_of_birth               DATE,
    phone_number                VARCHAR(20),
    address                     TEXT,
    gender                      VARCHAR(20) DEFAULT 'prefer_not_to_say',   -- male, female, other, prefer_not_to_say
    university                  VARCHAR(255),
    major                       VARCHAR(255),
    education_level             VARCHAR(50),    -- high_school, undergraduate, graduate, other
    grade                       VARCHAR(50),    -- '10','11','12','1'-'5', etc.
    emergency_contact_parent_id INTEGER REFERENCES parents(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_students_user_id      ON students (user_id);
CREATE INDEX IF NOT EXISTS idx_students_student_code ON students (student_code);


-- ============================================================
-- 5. BẢNG COUNSELORS
-- ============================================================

CREATE TABLE IF NOT EXISTS counselors (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_number      VARCHAR(100) UNIQUE,
    specialization      VARCHAR(255),
    years_of_experience INTEGER,
    bio                 TEXT,
    phone_number        VARCHAR(20),
    office_location     VARCHAR(255),
    is_available        BOOLEAN DEFAULT TRUE
);


-- ============================================================
-- 6. BẢNG PARENT CONSENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS parent_consents (
    id          SERIAL PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    parent_id   INTEGER NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    is_approved INTEGER DEFAULT 0   -- 0: pending, 1: approved, -1: rejected
);

CREATE INDEX IF NOT EXISTS idx_parent_consents_student ON parent_consents (student_id);
CREATE INDEX IF NOT EXISTS idx_parent_consents_parent  ON parent_consents (parent_id);


-- ============================================================
-- 7. BẢNG ASSESSMENTS (GAD-7)
-- ============================================================

CREATE TABLE IF NOT EXISTS assessments (
    id                      SERIAL PRIMARY KEY,
    student_id              INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    answers                 JSONB NOT NULL,                -- [0,1,2,3,...] (7 đáp án)
    total_score             INTEGER NOT NULL,              -- 0–21
    severity_level          VARCHAR(50) NOT NULL,          -- minimal, mild, moderate, severe
    functional_impairment   INTEGER,                       -- 0–3
    analysis                TEXT,                          -- AI analysis (Vietnamese)
    recommendations         JSONB,                         -- Array of strings
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes                   TEXT
);

CREATE INDEX IF NOT EXISTS idx_assessments_student_id  ON assessments (student_id);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at  ON assessments (created_at DESC);


-- ============================================================
-- 8. BẢNG VOICE ANALYSES
-- ============================================================

CREATE TABLE IF NOT EXISTS voice_analyses (
    id                          SERIAL PRIMARY KEY,
    student_id                  INTEGER NOT NULL REFERENCES students(id)    ON DELETE CASCADE,
    assessment_id               INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,

    -- File info
    audio_file_path             VARCHAR(500) NOT NULL,
    file_size_bytes             INTEGER,
    audio_duration              FLOAT,
    audio_format                VARCHAR(10),

    -- Prompt
    prompt_id                   INTEGER,
    prompt_text                 TEXT,

    -- Transcription (Deepgram)
    transcription               TEXT,
    transcription_language      VARCHAR(10) DEFAULT 'vi',
    word_count                  INTEGER,
    transcription_confidence    FLOAT,

    -- Audio features (Librosa)
    audio_features              JSONB,      -- {pitch_mean, pitch_std, energy_mean, speech_rate, pause_count, voice_stability, mfccs}

    -- Emotion detection
    detected_emotions           JSONB,      -- {anxiety: 0.75, sadness: 0.60, anger: 0.10, neutral: 0.20}
    dominant_emotion            VARCHAR(50),
    emotion_confidence          FLOAT,

    -- Text / Semantic
    sentiment_score             FLOAT,      -- -1 to 1
    keywords                    JSONB,      -- [{word, count, weight}, ...]
    psychological_markers       JSONB,      -- {negative_words, positive_words, self_reference, uncertainty}

    -- Gender-normalized
    gender_used                 VARCHAR(20),
    normalized_features         JSONB,

    -- Comprehensive Gemini analysis
    comprehensive_analysis      TEXT,
    comprehensive_recommendations JSONB,

    -- Processing metadata
    created_at                  TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at                TIMESTAMP WITH TIME ZONE,
    processing_status           VARCHAR(20) DEFAULT 'pending' NOT NULL,   -- pending, processing, completed, failed
    processing_time             FLOAT,

    -- Error handling
    has_error                   INTEGER DEFAULT 0,
    error_message               TEXT
);

CREATE INDEX IF NOT EXISTS idx_voice_analyses_student_id    ON voice_analyses (student_id);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_assessment_id ON voice_analyses (assessment_id);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_created_at    ON voice_analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_dominant_emo  ON voice_analyses (dominant_emotion);


-- ============================================================
-- 9. BẢNG CONVERSATIONS + MESSAGES (AI chat cũ - legacy)
-- ============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title           VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE,
    last_message_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS messages (
    id                  SERIAL PRIMARY KEY,
    conversation_id     INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                VARCHAR(20) NOT NULL,   -- 'user' or 'assistant'
    content             TEXT NOT NULL,
    voice_analysis_id   INTEGER REFERENCES voice_analyses(id) ON DELETE SET NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id);


-- ============================================================
-- 10. BẢNG AI_CONVERSATIONS + AI_MESSAGES (chat mới)
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_conversations (
    id                      SERIAL PRIMARY KEY,
    student_id              INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    latest_assessment_id    INTEGER REFERENCES assessments(id) ON DELETE SET NULL,
    title                   VARCHAR(255) DEFAULT 'Chat với AI' NOT NULL,
    is_active               BOOLEAN DEFAULT TRUE NOT NULL,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_message_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_conversations_student   ON ai_conversations (student_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_active    ON ai_conversations (is_active);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_last_msg  ON ai_conversations (last_message_at DESC);

CREATE TABLE IF NOT EXISTS ai_messages (
    id                      SERIAL PRIMARY KEY,
    conversation_id         INTEGER NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role                    VARCHAR(20) NOT NULL,   -- 'user' or 'assistant'
    content                 TEXT NOT NULL,
    related_assessment_id   INTEGER REFERENCES assessments(id) ON DELETE SET NULL,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation ON ai_messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_created_at   ON ai_messages (created_at);


-- ============================================================
-- 11. BẢNG COUNSELOR_CONVERSATIONS + COUNSELOR_MESSAGES
-- ============================================================

CREATE TABLE IF NOT EXISTS counselor_conversations (
    id              BIGSERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES students(id)   ON DELETE CASCADE,
    counselor_id    INTEGER NOT NULL REFERENCES counselors(id) ON DELETE CASCADE,
    status          VARCHAR(50) NOT NULL DEFAULT 'active',   -- active, closed, archived
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE (student_id, counselor_id)                         -- mỗi cặp có 1 conversation
);

CREATE INDEX IF NOT EXISTS idx_cc_student    ON counselor_conversations (student_id);
CREATE INDEX IF NOT EXISTS idx_cc_counselor  ON counselor_conversations (counselor_id);
CREATE INDEX IF NOT EXISTS idx_cc_status     ON counselor_conversations (status);
CREATE INDEX IF NOT EXISTS idx_cc_last_msg   ON counselor_conversations (last_message_at DESC);

CREATE TABLE IF NOT EXISTS counselor_messages (
    id              BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES counselor_conversations(id) ON DELETE CASCADE,
    sender_type     VARCHAR(20) NOT NULL,    -- 'student' or 'counselor'
    content         TEXT NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cm_conversation ON counselor_messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_cm_created_at   ON counselor_messages (created_at);
CREATE INDEX IF NOT EXISTS idx_cm_is_read      ON counselor_messages (is_read);


-- ============================================================
-- 12. BẢNG MEDICAL_CENTERS
-- ============================================================

CREATE TABLE IF NOT EXISTS medical_centers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    address         TEXT NOT NULL,
    description     TEXT,
    latitude        DECIMAL(10, 8) NOT NULL,
    longitude       DECIMAL(11, 8) NOT NULL,
    phone           VARCHAR(20),
    email           VARCHAR(100),
    website         VARCHAR(255),
    services        TEXT[] DEFAULT ARRAY[]::TEXT[],
    opening_hours   JSONB DEFAULT '{}'::jsonb,
    image_url       TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mc_location ON medical_centers (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_mc_services ON medical_centers USING GIN(services);
CREATE INDEX IF NOT EXISTS idx_mc_name     ON medical_centers (name);


-- ============================================================
-- 13. SEED DATA: ADMIN USER
-- ============================================================
-- Password: Admin@123! (bcrypt hash bên dưới)

INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
VALUES (
    'admin@ai4mind.com',
    '$2b$12$DYFrWx1Jb0jughg1CDUvtuUHeoai.7aE2vgOoDPhE/EP.5gBPcp/C',
    'Admin AI4Mind',
    'ADMIN',
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;


-- ============================================================
-- 14. SEED DATA: COUNSELORS
-- ============================================================
-- Password (tất cả): Counselor123!

DO $$
DECLARE
    user1_id INTEGER;
    user2_id INTEGER;
    user3_id INTEGER;
BEGIN
    -- Counselor 1: TS. Nguyễn Văn A
    IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'counselor1@ai4mind.com') THEN
        INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
        VALUES (
            'counselor1@ai4mind.com',
            '$2b$12$UUPZJI9/gZYBU63ert5c.efwpr4y43h33YQlsPb8BZK1P7rkayVpW',
            'TS. Nguyễn Văn A',
            'COUNSELOR',
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
    END IF;

    -- Counselor 2: ThS. Trần Thị B
    IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'counselor2@ai4mind.com') THEN
        INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
        VALUES (
            'counselor2@ai4mind.com',
            '$2b$12$UUPZJI9/gZYBU63ert5c.efwpr4y43h33YQlsPb8BZK1P7rkayVpW',
            'ThS. Trần Thị B',
            'COUNSELOR',
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
    END IF;

    -- Counselor 3: ThS. Lê Văn C
    IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'counselor3@ai4mind.com') THEN
        INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
        VALUES (
            'counselor3@ai4mind.com',
            '$2b$12$UUPZJI9/gZYBU63ert5c.efwpr4y43h33YQlsPb8BZK1P7rkayVpW',
            'ThS. Lê Văn C',
            'COUNSELOR',
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
            FALSE
        );
    END IF;

    RAISE NOTICE 'Seed counselors: done';
END $$;


-- ============================================================
-- 15. SEED DATA: MEDICAL CENTERS (TP.HCM)
-- ============================================================

INSERT INTO medical_centers (name, address, latitude, longitude, phone, email, website, services, opening_hours, description)
VALUES

-- 1. BV Tâm thần TP.HCM
(
    'Bệnh viện Tâm thần Thành phố Hồ Chí Minh',
    '766 Võ Văn Kiệt, Phường 1, Quận 5, TP. Hồ Chí Minh',
    10.7544, 106.6605,
    '028.3855.4269', 'info@tamthan-tphcm.com.vn', 'http://www.tamthan-tphcm.com.vn',
    ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Trị liệu Tâm lý', 'Điều trị Nghiện'],
    '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:30","sunday":"Closed"}'::jsonb,
    'Bệnh viện chuyên khoa tâm thần hàng đầu TP.HCM'
),

-- 2. Trung tâm Tư vấn Tâm lý UMC
(
    'Trung tâm Tư vấn Tâm lý UMC',
    '203 Nguyễn Văn Thủ, Đa Kao, Quận 1, TP. Hồ Chí Minh',
    10.7879, 106.6947,
    '028.3824.3757', 'contact@umc.edu.vn', 'https://umc.edu.vn',
    ARRAY['Tư vấn Tâm lý', 'Trị liệu Nhóm', 'Đánh giá Tâm lý', 'Coaching'],
    '{"monday":"08:00-20:00","tuesday":"08:00-20:00","wednesday":"08:00-20:00","thursday":"08:00-20:00","friday":"08:00-20:00","saturday":"08:00-17:00","sunday":"Closed"}'::jsonb,
    'Trung tâm tư vấn của Đại học Y Dược TP.HCM'
),

-- 3. Viện Sức khỏe Tâm thần Quốc gia (BV Bạch Mai Hà Nội)
(
    'Viện Sức khỏe Tâm thần - Bệnh viện Bạch Mai',
    '78 Giải Phóng, Phương Mai, Đống Đa, Hà Nội',
    21.0015, 105.8435,
    '024.3869.3731', NULL, 'https://bachmai.gov.vn',
    ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Nghiên cứu Lâm sàng'],
    '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:30","sunday":"Closed"}'::jsonb,
    'Viện tâm thần hàng đầu phía Bắc Việt Nam'
),

-- 4. Khoa Tâm lý BV Nhi Đồng 1
(
    'Khoa Tâm lý - Bệnh viện Nhi Đồng 1',
    '341 Sư Vạn Hạnh, Phường 10, Quận 10, TP. Hồ Chí Minh',
    10.7756, 106.6677,
    '028.3927.1119', NULL, 'http://www.benhviennhi.org.vn',
    ARRAY['Tư vấn Tâm lý Trẻ em', 'Đánh giá Phát triển', 'Trị liệu Hành vi'],
    '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:30","sunday":"Closed"}'::jsonb,
    'Khoa tâm lý dành cho trẻ em và thanh thiếu niên'
),

-- 5. Trung tâm Tư vấn Tâm lý Sức khỏe Học đường (TPHCM)
(
    'Trung tâm Hỗ trợ Sức khỏe Tâm thần HCDC',
    '59 Nguyễn Thị Minh Khai, Phường Bến Thành, Quận 1, TP. Hồ Chí Minh',
    10.7769, 106.6920,
    '028.3930.0351', 'info@hcdc.vn', 'https://hcdc.vn',
    ARRAY['Tư vấn Tâm lý', 'Sức khỏe Học đường', 'Phòng chống Tự tử', 'Hỗ trợ Khủng hoảng'],
    '{"monday":"07:30-17:00","tuesday":"07:30-17:00","wednesday":"07:30-17:00","thursday":"07:30-17:00","friday":"07:30-17:00","saturday":"Closed","sunday":"Closed"}'::jsonb,
    'Trung tâm kiểm soát bệnh tật TP.HCM - bộ phận sức khỏe tâm thần'
)

ON CONFLICT DO NOTHING;


-- ============================================================
-- 16. ROW LEVEL SECURITY (RLS) - tùy chọn, có thể bỏ qua
-- ============================================================
-- Nếu muốn bật RLS, uncomment các dòng bên dưới
-- Lưu ý: Service role key của Supabase sẽ bypass RLS tự động

-- ALTER TABLE students         ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE assessments      ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE voice_analyses   ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ai_messages      ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- VERIFY - Kiểm tra kết quả
-- ============================================================

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

SELECT
    u.email,
    u.full_name,
    u.role,
    u.is_active
FROM users u
ORDER BY u.role, u.id;
