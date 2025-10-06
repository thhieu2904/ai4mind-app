# KẾ HOẠCH TRIỂN KHAI "COUNSELOR CHAT" - PHASE 2

**Ngày tạo:** October 5, 2025  
**Status:** Planning → Ready to implement  
**Complexity:** ⭐⭐⭐⭐ (4/5 - Khó nhất trong 3 phases)

---

## 📊 PHÂN TÍCH HIỆN TRẠNG

### ✅ ĐÃ CÓ (Có thể tái sử dụng)

#### Backend:

1. **✅ AI Chat System** (hoàn chỉnh)

   - Models: `AIConversation`, `AIMessage` (`ai_chat.py`)
   - Services: `AIChatService`, `GeminiService`
   - Endpoints: `/api/v1/ai-chat/*`
   - **Có thể dùng làm template!**

2. **✅ Counselor Model** (`counselor.py`)

   - Table: `counselors` (đã có)
   - Fields: license_number, specialization, years_of_experience, bio, phone_number, office_location, `is_available`
   - Relationship với `User`

3. **✅ Authentication & Authorization**

   - JWT tokens
   - Role-based access (students, counselors)
   - Protected routes

4. **✅ Database (PostgreSQL/Supabase)**
   - Schema đã có students, users, counselors
   - Foreign key relationships

#### Frontend:

1. **✅ AI Chat UI** (`AIChatPage.tsx`)

   - Messenger-like interface
   - Real-time message display
   - Loading states, error handling
   - **Có thể clone và modify!**

2. **✅ Services Layer**

   - `aiChatService.ts` - API calls với axios
   - Authentication headers
   - Error handling

3. **✅ Components**

   - Material-UI components
   - Responsive design
   - TypeScript types

4. **✅ Routing & Navigation**
   - React Router
   - Protected routes
   - Dashboard with feature buttons

---

## ❌ CẦN TẠO MỚI

### Backend (6 files):

1. **Models** (`ai-service/app/models/counselor_chat.py`)

   - `CounselorConversation` table
   - `CounselorMessage` table
   - Relationships với Student & Counselor

2. **Schemas** (`ai-service/app/schemas/counselor_chat.py`)

   - `ConversationCreate`, `ConversationResponse`
   - `MessageCreate`, `MessageResponse`
   - Pydantic validation

3. **Service** (`ai-service/app/services/counselor_chat_service.py`)

   - Business logic: create conversation, send message
   - Permission checks (student chỉ chat với counselor của mình)
   - Mark messages as read

4. **Endpoints** (`ai-service/app/api/v1/endpoints/counselor_chat.py`)

   - GET `/api/v1/counselor-chat/counselors` - List available counselors
   - POST `/api/v1/counselor-chat/conversations` - Create conversation
   - GET `/api/v1/counselor-chat/conversations/{id}/messages` - Get messages
   - POST `/api/v1/counselor-chat/conversations/{id}/messages` - Send message
   - PATCH `/api/v1/counselor-chat/messages/{id}/read` - Mark as read

5. **Router Registration** (`ai-service/app/api/v1/api.py`)

   - Include counselor_chat router

6. **Database Migration** (`alembic/versions/`)
   - Create `counselor_conversations` table
   - Create `counselor_messages` table
   - Indexes for performance

### Frontend (8 files):

1. **Types** (`frontend/src/types/counselorChat.ts`)

   - `Counselor`, `Conversation`, `Message` interfaces

2. **Service** (`frontend/src/services/counselorChatService.ts`)

   - API calls: getAvailableCounselors, createConversation, getMessages, sendMessage

3. **Components:**

   - `CounselorListPage.tsx` - Danh sách counselors có sẵn
   - `CounselorChatPage.tsx` - Chat interface (clone từ AIChatPage)
   - `CounselorCard.tsx` - Hiển thị thông tin counselor
   - `ConversationList.tsx` (optional) - Danh sách conversations

4. **Routing** (`frontend/src/App.tsx`)

   - Route `/counselors` - List counselors
   - Route `/counselor-chat/:counselorId` - Chat với counselor

5. **Dashboard Button** (`DashboardPage.tsx`)
   - Nút "Tư vấn trực tiếp" để navigate đến `/counselors`

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Database Schema:

```sql
-- Table 1: counselor_conversations
CREATE TABLE counselor_conversations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    counselor_id INTEGER NOT NULL REFERENCES counselors(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active', -- active, closed, archived
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, counselor_id) -- Mỗi student chỉ có 1 conversation với 1 counselor
);

-- Table 2: counselor_messages
CREATE TABLE counselor_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES counselor_conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('student', 'counselor')),
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_student ON counselor_conversations(student_id);
CREATE INDEX idx_conversations_counselor ON counselor_conversations(counselor_id);
CREATE INDEX idx_messages_conversation ON counselor_messages(conversation_id, created_at);
```

### API Flow:

```
Student → Frontend → Backend API → Database
   ↓
1. GET /counselors → List available counselors (is_available=true)
2. POST /conversations {counselor_id} → Create/get conversation
3. GET /conversations/{id}/messages → Load chat history
4. POST /conversations/{id}/messages → Send message
5. WebSocket (optional Phase 2.5) → Real-time updates
```

---

## 📅 LỘ TRÌNH TRIỂN KHAI (3 NGÀY)

### **Day 1: Backend Foundation** (6-8 hours)

#### Morning (3-4h):

- ✅ Create database schema (SQL)
- ✅ Create models (`counselor_chat.py`)
- ✅ Create schemas (`counselor_chat.py`)
- ✅ Create migration (`alembic`)
- ✅ Run migration on Supabase

#### Afternoon (3-4h):

- ✅ Create service (`counselor_chat_service.py`)
  - `get_available_counselors()`
  - `create_or_get_conversation(student_id, counselor_id)`
  - `get_messages(conversation_id, user_id)`
  - `send_message(conversation_id, sender_type, content, user_id)`
  - `mark_as_read(message_id, user_id)`
- ✅ Create endpoints (`counselor_chat.py`)
- ✅ Register router (`api.py`)
- ✅ Test với Postman/cURL

### **Day 2: Frontend Core** (6-8 hours)

#### Morning (3-4h):

- ✅ Create types (`types/counselorChat.ts`)
- ✅ Create service (`services/counselorChatService.ts`)
- ✅ Create CounselorListPage:
  - Fetch available counselors
  - Display cards với thông tin: name, specialization, experience, bio
  - "Bắt đầu chat" button → navigate to chat page

#### Afternoon (3-4h):

- ✅ Create CounselorChatPage (clone từ AIChatPage):
  - Load messages
  - Send/receive messages
  - Display sender (student vs counselor) với different colors/alignment
  - Loading & error states
- ✅ Add routes to App.tsx
- ✅ Add dashboard button

### **Day 3: Testing & Polish** (4-6 hours)

#### Morning (2-3h):

- ✅ End-to-end testing:
  - Create counselor accounts (SQL insert)
  - Test student → counselor chat
  - Test permission: student A không thể xem chat của student B
- ✅ Bug fixes

#### Afternoon (2-3h):

- ✅ UI/UX improvements:
  - Typing indicator (optional)
  - Message timestamps
  - Unread count badge
  - Better error messages
- ✅ Code review & cleanup
- ✅ Documentation

---

## 🎯 FEATURES CHÍNH

### MVP (Must Have):

1. ✅ **Danh sách Counselors** - Students xem counselors có sẵn
2. ✅ **Start Conversation** - Click vào counselor → tạo conversation
3. ✅ **Send/Receive Messages** - Real-time messaging
4. ✅ **Chat History** - Load previous messages
5. ✅ **Permission Check** - Student chỉ chat với counselor đã chọn

### Nice to Have (Optional):

1. ⚠️ **WebSocket** - Real-time updates (không cần reload)
2. ⚠️ **Typing Indicator** - "Counselor is typing..."
3. ⚠️ **Unread Count** - Badge hiển thị số tin nhắn chưa đọc
4. ⚠️ **File Upload** - Gửi hình ảnh, file đính kèm
5. ⚠️ **Video Call** - Tích hợp Zoom/Google Meet

---

## 🔐 SECURITY & PERMISSIONS

### Rules:

1. **Students:**

   - Chỉ xem được counselors có `is_available=true`
   - Chỉ chat với counselor đã chọn
   - Không thể xem conversations của students khác

2. **Counselors:**

   - Xem tất cả conversations của students chat với mình
   - Không thể xem conversations với counselors khác

3. **Authentication:**
   - Tất cả endpoints cần JWT token
   - Backend verify `current_user` role

---

## 🚀 DEPLOYMENT CHECKLIST

### Database:

- [ ] Run Alembic migration trên Supabase production
- [ ] Verify tables created: `counselor_conversations`, `counselor_messages`
- [ ] Create sample counselor accounts

### Backend:

- [ ] Deploy ai-service với code mới
- [ ] Test endpoints với production database
- [ ] Monitor logs for errors

### Frontend:

- [ ] Deploy frontend với new pages/routes
- [ ] Test UI trên production
- [ ] Verify API calls work

---

## 📝 NOTES

### Khác biệt so với AI Chat:

| Feature           | AI Chat                | Counselor Chat                 |
| ----------------- | ---------------------- | ------------------------------ |
| **Sender**        | AI Assistant (1 chiều) | Human counselor (2 chiều)      |
| **Response Time** | Instant (< 1s)         | Manual (phụ thuộc counselor)   |
| **Context**       | Assessment data        | Student profile + history      |
| **UI**            | Single conversation    | Multiple conversations (list)  |
| **Real-time**     | Not needed             | Highly recommended (WebSocket) |

### Technical Decisions:

1. **REST vs WebSocket:**

   - **Phase 2.0:** REST only (polling every 5s)
   - **Phase 2.5 (optional):** Add WebSocket for real-time

2. **Database Design:**

   - Separate tables (`counselor_*`) instead of reusing `conversations/messages`
   - Reason: Different schema, permissions, queries

3. **Frontend State:**
   - useState for messages (simple)
   - Later: Zustand/Redux if need global state

---

## 🎓 LEARNING POINTS

Tính năng này sẽ dạy bạn:

1. ✅ **Many-to-many relationships** (students ↔ counselors)
2. ✅ **Role-based permissions** (student vs counselor)
3. ✅ **Real-time messaging patterns** (polling → WebSocket)
4. ✅ **Chat UI best practices** (alignment, timestamps, loading states)
5. ✅ **Scalability** (indexes, pagination cho chat history)

---

## ✅ NEXT STEPS

1. **Review plan này** với team/mentor
2. **Confirm database schema** (bảng nào, field nào)
3. **Start Day 1:** Create database schema + models
4. **Test incrementally** (mỗi file xong test ngay)
5. **Commit thường xuyên** (mỗi feature commit 1 lần)

---

**Sẵn sàng bắt đầu chưa?** 🚀

Nếu OK, mình sẽ bắt đầu từ Day 1 - Backend Foundation!
