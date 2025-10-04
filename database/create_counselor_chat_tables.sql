-- ============================================
-- COUNSELOR CHAT TABLES - MIGRATION SCRIPT
-- Created: October 5, 2025
-- Purpose: Enable real-time messaging between students and counselors
-- ============================================

-- ============================================
-- TABLE 1: COUNSELOR_CONVERSATIONS
-- Manage conversation threads between students and counselors
-- ============================================

CREATE TABLE IF NOT EXISTS public.counselor_conversations (
    id BIGSERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    counselor_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign keys
    CONSTRAINT fk_counselor_conversations_student 
        FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE,
    CONSTRAINT fk_counselor_conversations_counselor 
        FOREIGN KEY (counselor_id) REFERENCES public.counselors(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_counselor_conversations_status 
        CHECK (status IN ('active', 'closed', 'archived')),
    
    -- Unique: Mỗi student chỉ có 1 conversation active với 1 counselor
    CONSTRAINT uq_counselor_conversations_student_counselor 
        UNIQUE (student_id, counselor_id)
);

-- Comments
COMMENT ON TABLE public.counselor_conversations IS 'Conversation threads between students and counselors for direct messaging';
COMMENT ON COLUMN public.counselor_conversations.status IS 'Conversation status: active (ongoing), closed (ended), archived (historical)';
COMMENT ON COLUMN public.counselor_conversations.last_message_at IS 'Timestamp of last message for sorting';

-- ============================================
-- TABLE 2: COUNSELOR_MESSAGES
-- Store individual messages in conversations
-- ============================================

CREATE TABLE IF NOT EXISTS public.counselor_messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign keys
    CONSTRAINT fk_counselor_messages_conversation 
        FOREIGN KEY (conversation_id) REFERENCES public.counselor_conversations(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_counselor_messages_sender_type 
        CHECK (sender_type IN ('student', 'counselor'))
);

-- Comments
COMMENT ON TABLE public.counselor_messages IS 'Individual messages exchanged between students and counselors';
COMMENT ON COLUMN public.counselor_messages.sender_type IS 'Message sender: student or counselor';
COMMENT ON COLUMN public.counselor_messages.is_read IS 'Whether the recipient has read this message';

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Index for fetching conversations by student
CREATE INDEX IF NOT EXISTS idx_counselor_conversations_student 
    ON public.counselor_conversations(student_id, last_message_at DESC);

-- Index for fetching conversations by counselor
CREATE INDEX IF NOT EXISTS idx_counselor_conversations_counselor 
    ON public.counselor_conversations(counselor_id, last_message_at DESC);

-- Index for fetching messages in a conversation (most common query)
CREATE INDEX IF NOT EXISTS idx_counselor_messages_conversation 
    ON public.counselor_messages(conversation_id, created_at ASC);

-- Index for unread messages count
CREATE INDEX IF NOT EXISTS idx_counselor_messages_unread 
    ON public.counselor_messages(conversation_id, is_read) 
    WHERE is_read = FALSE;

-- Index for recent messages (for notifications)
CREATE INDEX IF NOT EXISTS idx_counselor_messages_recent 
    ON public.counselor_messages(created_at DESC) 
    WHERE is_read = FALSE;

-- ============================================
-- TRIGGERS FOR AUTO-UPDATE
-- ============================================

-- Trigger function: Update last_message_at when new message is sent
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.counselor_conversations
    SET last_message_at = NEW.created_at
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update last_message_at
DROP TRIGGER IF EXISTS trigger_update_last_message ON public.counselor_messages;
CREATE TRIGGER trigger_update_last_message
    AFTER INSERT ON public.counselor_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_last_message();

-- ============================================
-- ROW LEVEL SECURITY (RLS) - OPTIONAL
-- Enable if using Supabase Auth
-- ============================================

-- Enable RLS on conversations
-- ALTER TABLE public.counselor_conversations ENABLE ROW LEVEL SECURITY;

-- Policy: Students can only see their own conversations
-- CREATE POLICY "Students can view own conversations"
--     ON public.counselor_conversations
--     FOR SELECT
--     USING (student_id = auth.uid()::INTEGER);

-- Policy: Counselors can see conversations they're part of
-- CREATE POLICY "Counselors can view assigned conversations"
--     ON public.counselor_conversations
--     FOR SELECT
--     USING (counselor_id IN (
--         SELECT id FROM public.counselors WHERE user_id = auth.uid()::INTEGER
--     ));

-- Enable RLS on messages
-- ALTER TABLE public.counselor_messages ENABLE ROW LEVEL SECURITY;

-- Policy: View messages only in accessible conversations
-- CREATE POLICY "View messages in accessible conversations"
--     ON public.counselor_messages
--     FOR SELECT
--     USING (conversation_id IN (
--         SELECT id FROM public.counselor_conversations
--         WHERE student_id = auth.uid()::INTEGER
--            OR counselor_id IN (
--                SELECT id FROM public.counselors WHERE user_id = auth.uid()::INTEGER
--            )
--     ));

-- ============================================
-- VERIFY TABLES CREATED
-- ============================================

SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('counselor_conversations', 'counselor_messages');

-- ============================================
-- SAMPLE DATA FOR TESTING (Optional)
-- Uncomment to insert test data
-- ============================================

/*
-- Get first student and first counselor
DO $$
DECLARE
    test_student_id INTEGER;
    test_counselor_id INTEGER;
    test_conversation_id BIGINT;
BEGIN
    -- Get first student
    SELECT id INTO test_student_id FROM public.students LIMIT 1;
    
    -- Get first counselor
    SELECT id INTO test_counselor_id FROM public.counselors LIMIT 1;
    
    IF test_student_id IS NOT NULL AND test_counselor_id IS NOT NULL THEN
        -- Create test conversation
        INSERT INTO public.counselor_conversations (student_id, counselor_id)
        VALUES (test_student_id, test_counselor_id)
        RETURNING id INTO test_conversation_id;
        
        -- Insert test messages
        INSERT INTO public.counselor_messages (conversation_id, sender_type, content, is_read) VALUES
        (test_conversation_id, 'counselor', 'Xin chào! Tôi là chuyên gia tâm lý. Em có thể chia sẻ với tôi những gì em đang trải qua không?', TRUE),
        (test_conversation_id, 'student', 'Chào cô. Em đang cảm thấy rất lo lắng về kỳ thi sắp tới.', TRUE),
        (test_conversation_id, 'counselor', 'Tôi hiểu em đang lo lắng. Hãy kể cho tôi nghe cụ thể hơn về những gì làm em lo nhé?', TRUE),
        (test_conversation_id, 'student', 'Em sợ không đủ thời gian ôn tập và kết quả không như mong đợi.', FALSE);
        
        RAISE NOTICE 'Test data created: conversation_id = %', test_conversation_id;
    ELSE
        RAISE NOTICE 'No students or counselors found in database';
    END IF;
END $$;
*/

-- ============================================
-- CLEANUP (If needed to rollback)
-- ============================================

-- Uncomment below to drop tables and rollback migration
/*
DROP TRIGGER IF EXISTS trigger_update_last_message ON public.counselor_messages;
DROP FUNCTION IF EXISTS update_conversation_last_message();
DROP INDEX IF EXISTS idx_counselor_messages_recent;
DROP INDEX IF EXISTS idx_counselor_messages_unread;
DROP INDEX IF EXISTS idx_counselor_messages_conversation;
DROP INDEX IF EXISTS idx_counselor_conversations_counselor;
DROP INDEX IF EXISTS idx_counselor_conversations_student;
DROP TABLE IF EXISTS public.counselor_messages;
DROP TABLE IF EXISTS public.counselor_conversations;
*/

-- ============================================
-- DONE! ✅
-- ============================================

SELECT 'Counselor Chat tables created successfully! 🎉' AS status;
