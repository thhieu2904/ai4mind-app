# HƯỚNG DẪN SETUP SUPABASE CHO AI CHAT

## 📋 BƯỚC 1: TẠO BẢNG TRÊN SUPABASE

### Cách 1: Dùng Supabase Dashboard (Recommended - Dễ nhất)

1. **Truy cập Supabase Dashboard**

   - Vào: https://supabase.com/dashboard
   - Chọn project của bạn
   - Click vào **Table Editor** (sidebar bên trái)

2. **Tạo bảng `ai_conversations`**
   - Click **New Table**
   - Điền thông tin:

```
Table Name: ai_conversations

Columns:
┌─────────────────────────┬──────────────┬────────────┬─────────────────┬──────────────┐
│ Name                    │ Type         │ Default    │ Primary/Unique  │ Nullable     │
├─────────────────────────┼──────────────┼────────────┼─────────────────┼──────────────┤
│ id                      │ int8         │ auto       │ PRIMARY KEY     │ NOT NULL     │
│ student_id              │ int8         │            │                 │ NOT NULL     │
│ latest_assessment_id    │ int8         │            │                 │ NULL         │
│ title                   │ varchar(255) │ 'Chat AI'  │                 │ NOT NULL     │
│ is_active               │ bool         │ true       │                 │ NOT NULL     │
│ created_at              │ timestamptz  │ now()      │                 │ NOT NULL     │
│ last_message_at         │ timestamptz  │ now()      │                 │ NOT NULL     │
└─────────────────────────┴──────────────┴────────────┴─────────────────┴──────────────┘

Foreign Keys:
- student_id → students.id (ON DELETE CASCADE)
- latest_assessment_id → assessments.id (ON DELETE SET NULL)

Indexes:
- idx_ai_conversations_student ON (student_id, last_message_at DESC)
```

- Click **Save**

3. **Tạo bảng `ai_messages`**
   - Click **New Table** lần nữa
   - Điền thông tin:

```
Table Name: ai_messages

Columns:
┌─────────────────────────┬──────────────┬────────────┬─────────────────┬──────────────┐
│ Name                    │ Type         │ Default    │ Primary/Unique  │ Nullable     │
├─────────────────────────┼──────────────┼────────────┼─────────────────┼──────────────┤
│ id                      │ int8         │ auto       │ PRIMARY KEY     │ NOT NULL     │
│ conversation_id         │ int8         │            │                 │ NOT NULL     │
│ role                    │ varchar(20)  │            │                 │ NOT NULL     │
│ content                 │ text         │            │                 │ NOT NULL     │
│ related_assessment_id   │ int8         │            │                 │ NULL         │
│ created_at              │ timestamptz  │ now()      │                 │ NOT NULL     │
└─────────────────────────┴──────────────┴────────────┴─────────────────┴──────────────┘

Foreign Keys:
- conversation_id → ai_conversations.id (ON DELETE CASCADE)
- related_assessment_id → assessments.id (ON DELETE SET NULL)

Indexes:
- idx_ai_messages_conversation ON (conversation_id, created_at DESC)

Constraints:
- CHECK (role IN ('user', 'assistant'))
```

- Click **Save**

---

### Cách 2: Dùng SQL Editor (Nhanh hơn nếu quen SQL)

1. **Truy cập SQL Editor**

   - Trong Supabase Dashboard
   - Click **SQL Editor** (sidebar)
   - Click **New Query**

2. **Copy & Paste SQL này:**

```sql
-- ============================================
-- AI CHAT TABLES FOR AI4MIND
-- Created: October 5, 2025
-- ============================================

-- Table 1: AI Conversations
CREATE TABLE IF NOT EXISTS ai_conversations (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    latest_assessment_id BIGINT REFERENCES assessments(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL DEFAULT 'Chat với AI',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table 2: AI Messages
CREATE TABLE IF NOT EXISTS ai_messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    related_assessment_id BIGINT REFERENCES assessments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_conversations_student
    ON ai_conversations(student_id, last_message_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_conversations_active
    ON ai_conversations(student_id, is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation
    ON ai_messages(conversation_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_messages_created
    ON ai_messages(created_at DESC);

-- Comments for documentation
COMMENT ON TABLE ai_conversations IS 'AI chat conversations between students and AI assistant';
COMMENT ON TABLE ai_messages IS 'Individual messages within AI chat conversations';
COMMENT ON COLUMN ai_conversations.latest_assessment_id IS 'Link to most recent GAD-7 assessment for context';
COMMENT ON COLUMN ai_messages.role IS 'Message sender: user (student) or assistant (AI)';

-- ============================================
-- VERIFY TABLES CREATED
-- ============================================
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('ai_conversations', 'ai_messages');

-- ============================================
-- SAMPLE DATA FOR TESTING (Optional)
-- ============================================
-- Uncomment below to insert sample data

/*
-- Get first student
DO $$
DECLARE
    test_student_id BIGINT;
    test_conversation_id BIGINT;
BEGIN
    -- Get first student
    SELECT id INTO test_student_id FROM students LIMIT 1;

    IF test_student_id IS NOT NULL THEN
        -- Create test conversation
        INSERT INTO ai_conversations (student_id, title)
        VALUES (test_student_id, 'Test Chat')
        RETURNING id INTO test_conversation_id;

        -- Insert test messages
        INSERT INTO ai_messages (conversation_id, role, content) VALUES
        (test_conversation_id, 'assistant', 'Xin chào! 👋 Tôi là AI4Mind Assistant. Em có muốn chia sẻ gì không?'),
        (test_conversation_id, 'user', 'Chào bạn, em đang cảm thấy lo lắng về kỳ thi sắp tới'),
        (test_conversation_id, 'assistant', 'Em đang lo lắng về kỳ thi à? Điều đó hoàn toàn bình thường. Em có muốn chia sẻ cụ thể hơn không?');

        RAISE NOTICE 'Test data created successfully for student %', test_student_id;
    ELSE
        RAISE NOTICE 'No students found in database';
    END IF;
END $$;
*/
```

3. **Chạy query**
   - Click **Run** (hoặc Ctrl+Enter)
   - Kiểm tra output: Phải thấy 2 tables được tạo

---

## 📋 BƯỚC 2: SETUP ROW LEVEL SECURITY (RLS)

**Quan trọng:** Để bảo mật, students chỉ được xem chat của mình!

### Trong SQL Editor:

```sql
-- ============================================
-- ROW LEVEL SECURITY FOR AI CHAT
-- ============================================

-- Enable RLS
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages ENABLE ROW LEVEL SECURITY;

-- Policy 1: Students chỉ xem conversations của mình
CREATE POLICY "Students can view own conversations"
    ON ai_conversations
    FOR SELECT
    USING (
        student_id IN (
            SELECT id FROM students WHERE user_id = auth.uid()
        )
    );

-- Policy 2: Students chỉ tạo conversations cho mình
CREATE POLICY "Students can create own conversations"
    ON ai_conversations
    FOR INSERT
    WITH CHECK (
        student_id IN (
            SELECT id FROM students WHERE user_id = auth.uid()
        )
    );

-- Policy 3: Students chỉ update conversations của mình
CREATE POLICY "Students can update own conversations"
    ON ai_conversations
    FOR UPDATE
    USING (
        student_id IN (
            SELECT id FROM students WHERE user_id = auth.uid()
        )
    );

-- Policy 4: Students xem messages trong conversations của mình
CREATE POLICY "Students can view messages in own conversations"
    ON ai_messages
    FOR SELECT
    USING (
        conversation_id IN (
            SELECT id FROM ai_conversations WHERE student_id IN (
                SELECT id FROM students WHERE user_id = auth.uid()
            )
        )
    );

-- Policy 5: Students tạo messages trong conversations của mình
CREATE POLICY "Students can create messages in own conversations"
    ON ai_messages
    FOR INSERT
    WITH CHECK (
        conversation_id IN (
            SELECT id FROM ai_conversations WHERE student_id IN (
                SELECT id FROM students WHERE user_id = auth.uid()
            )
        )
    );

-- Policy 6: Service role có full access (cho backend API)
CREATE POLICY "Service role has full access to conversations"
    ON ai_conversations
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has full access to messages"
    ON ai_messages
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- ============================================
-- VERIFY RLS POLICIES
-- ============================================
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('ai_conversations', 'ai_messages')
ORDER BY tablename, policyname;
```

---

## 📋 BƯỚC 3: TẠO HELPER FUNCTIONS (Optional - Recommended)

### Function để get active conversation:

```sql
-- ============================================
-- HELPER FUNCTION: Get or Create Active Conversation
-- ============================================

CREATE OR REPLACE FUNCTION get_or_create_active_conversation(
    p_student_id BIGINT,
    p_latest_assessment_id BIGINT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_conversation_id BIGINT;
BEGIN
    -- Try to find active conversation
    SELECT id INTO v_conversation_id
    FROM ai_conversations
    WHERE student_id = p_student_id
      AND is_active = TRUE
    LIMIT 1;

    -- If not found, create new
    IF v_conversation_id IS NULL THEN
        INSERT INTO ai_conversations (
            student_id,
            latest_assessment_id,
            title,
            is_active
        )
        VALUES (
            p_student_id,
            p_latest_assessment_id,
            'Chat ' || TO_CHAR(NOW(), 'DD/MM/YYYY'),
            TRUE
        )
        RETURNING id INTO v_conversation_id;
    END IF;

    RETURN v_conversation_id;
END;
$$;

-- Test function
-- SELECT get_or_create_active_conversation(1, NULL);
```

---

## 📋 BƯỚC 4: VERIFY SETUP

### 1. Kiểm tra tables đã tạo:

```sql
-- List all AI chat tables
SELECT
    t.table_name,
    (SELECT COUNT(*) FROM information_schema.columns c
     WHERE c.table_name = t.table_name) as columns,
    (SELECT COUNT(*) FROM pg_indexes i
     WHERE i.tablename = t.table_name) as indexes,
    obj_description((t.table_schema||'.'||t.table_name)::regclass) as description
FROM information_schema.tables t
WHERE t.table_schema = 'public'
  AND t.table_name LIKE 'ai_%'
ORDER BY t.table_name;
```

Kết quả mong đợi:

```
table_name        | columns | indexes | description
──────────────────┼─────────┼─────────┼────────────────────
ai_conversations  |    7    |    3    | AI chat conversations...
ai_messages       |    6    |    2    | Individual messages...
```

### 2. Kiểm tra foreign keys:

```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name LIKE 'ai_%'
ORDER BY tc.table_name, kcu.column_name;
```

### 3. Kiểm tra RLS policies:

```sql
SELECT
    tablename,
    policyname,
    cmd,
    CASE
        WHEN roles = '{public}' THEN 'Public'
        ELSE array_to_string(roles, ', ')
    END as roles
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename LIKE 'ai_%'
ORDER BY tablename, policyname;
```

---

## 📋 BƯỚC 5: INSERT SAMPLE DATA (For Testing)

```sql
-- Insert sample conversation và messages
DO $$
DECLARE
    v_student_id BIGINT;
    v_conversation_id BIGINT;
    v_assessment_id BIGINT;
BEGIN
    -- Get first student
    SELECT id INTO v_student_id FROM students LIMIT 1;

    -- Get their latest assessment
    SELECT id INTO v_assessment_id
    FROM assessments
    WHERE student_id = v_student_id
    ORDER BY created_at DESC
    LIMIT 1;

    -- Create conversation
    INSERT INTO ai_conversations (student_id, latest_assessment_id, title)
    VALUES (v_student_id, v_assessment_id, 'Test Chat - ' || NOW()::date)
    RETURNING id INTO v_conversation_id;

    -- Insert messages
    INSERT INTO ai_messages (conversation_id, role, content) VALUES
    (v_conversation_id, 'assistant',
     'Xin chào! 👋 Tôi là AI4Mind Assistant.

Tôi thấy em vừa hoàn thành bài đánh giá GAD-7. Em có muốn chia sẻ về cảm xúc của mình không?'),

    (v_conversation_id, 'user',
     'Chào bạn, em đang cảm thấy lo lắng về kỳ thi cuối kỳ sắp tới'),

    (v_conversation_id, 'assistant',
     'Em đang lo lắng về kỳ thi à? Điều đó hoàn toàn bình thường trước kỳ thi quan trọng.

Em có thể chia sẻ cụ thể hơn là em lo lắng về điểm gì không?');

    RAISE NOTICE 'Sample data created: conversation_id = %', v_conversation_id;
    RAISE NOTICE 'Student ID: %, Assessment ID: %', v_student_id, v_assessment_id;
END $$;
```

### Verify sample data:

```sql
-- Check conversations
SELECT
    c.id,
    s.student_code,
    c.title,
    c.created_at,
    (SELECT COUNT(*) FROM ai_messages WHERE conversation_id = c.id) as message_count
FROM ai_conversations c
JOIN students s ON c.student_id = s.id
ORDER BY c.created_at DESC
LIMIT 5;

-- Check messages
SELECT
    m.id,
    m.role,
    LEFT(m.content, 50) || '...' as content_preview,
    m.created_at
FROM ai_messages m
ORDER BY m.created_at DESC
LIMIT 10;
```

---

## 📋 BƯỚC 6: EXPORT TO EXCEL TEST

### Trong SQL Editor:

```sql
-- Query để export (copy result này vào Excel)
SELECT
    c.id as conversation_id,
    s.student_code,
    u.full_name as student_name,
    c.title as conversation_title,
    m.role as message_role,
    m.content as message_content,
    m.created_at as message_time,
    a.total_score as assessment_score,
    a.severity_level
FROM ai_messages m
JOIN ai_conversations c ON m.conversation_id = c.id
JOIN students s ON c.student_id = s.id
JOIN users u ON s.user_id = u.id
LEFT JOIN assessments a ON c.latest_assessment_id = a.id
ORDER BY m.created_at DESC;
```

**Test export:**

1. Chạy query trên
2. Click **Results** → **Download CSV**
3. Mở CSV trong Excel
4. ✅ Check: Dữ liệu đẹp, đầy đủ columns

---

## 🎯 CHECKLIST - XÁC NHẬN HOÀN THÀNH

- [ ] ✅ Bảng `ai_conversations` đã tạo với 7 columns
- [ ] ✅ Bảng `ai_messages` đã tạo với 6 columns
- [ ] ✅ Foreign keys đã setup (student_id, assessment_id)
- [ ] ✅ Indexes đã tạo (performance)
- [ ] ✅ RLS policies đã enable (security)
- [ ] ✅ Sample data insert thành công
- [ ] ✅ Export Excel test OK
- [ ] ✅ Query performance < 100ms

---

## 🚨 TROUBLESHOOTING

### Lỗi: "relation already exists"

```sql
-- Drop và tạo lại
DROP TABLE IF EXISTS ai_messages CASCADE;
DROP TABLE IF EXISTS ai_conversations CASCADE;
-- Rồi chạy lại CREATE TABLE
```

### Lỗi: "foreign key constraint"

```sql
-- Check students table exists
SELECT COUNT(*) FROM students;
-- Check assessments table exists
SELECT COUNT(*) FROM assessments;
```

### Lỗi: RLS blocking queries

```sql
-- Tạm thời disable RLS để test
ALTER TABLE ai_conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages DISABLE ROW LEVEL SECURITY;
-- Remember to re-enable sau khi fix!
```

---

## 📚 TÀI LIỆU THAM KHẢO

- Supabase Table Editor: https://supabase.com/docs/guides/database/tables
- Supabase RLS: https://supabase.com/docs/guides/auth/row-level-security
- PostgreSQL Foreign Keys: https://www.postgresql.org/docs/current/ddl-constraints.html

---

_Setup guide created: October 5, 2025_
_Ready to implement! 🚀_
