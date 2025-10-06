# KẾ HOẠCH TRIỂN KHAI COUNSELOR CHAT - CHI TIẾT

**Ngày bắt đầu:** October 5, 2025  
**Thời gian:** 3 ngày (18-22 giờ)  
**Database:** Supabase PostgreSQL (đã verify schema)

---

## ✅ ĐÃ KIỂM TRA DATABASE

### Schema hiện tại trên Supabase:

```
✅ users (id, email, role, full_name, ...)
✅ students (id, user_id, student_code, ...)
✅ counselors (id, user_id, license_number, specialization, is_available, ...)
✅ ai_conversations + ai_messages (AI chat - hoàn chỉnh)
✅ assessments (GAD-7 results)
✅ Foreign keys đã setup đúng
```

### Cần tạo mới:

```
❌ counselor_conversations (student ↔ counselor threads)
❌ counselor_messages (chat messages)
```

---

## 📅 TIMELINE CHI TIẾT - 3 NGÀY

---

## 🗓️ DAY 1: BACKEND FOUNDATION (6-8 giờ)

### ⏰ MORNING SESSION (3-4 giờ) - Database Setup

#### ✅ **Task 1.1: Run Database Migration** (30 phút)

**File:** `database/create_counselor_chat_tables.sql` (ĐÃ TẠO)

**Steps:**

1. Mở Supabase Dashboard
2. Vào **SQL Editor** → **New Query**
3. Copy toàn bộ nội dung từ `create_counselor_chat_tables.sql`
4. Nhấn **Run** (Ctrl+Enter)
5. Verify output:
   ```
   ✅ 2 tables created
   ✅ 5 indexes created
   ✅ 1 trigger created
   ```

**Verify:**

```sql
-- Check tables
SELECT * FROM information_schema.tables
WHERE table_name IN ('counselor_conversations', 'counselor_messages');

-- Check indexes
SELECT indexname FROM pg_indexes
WHERE tablename IN ('counselor_conversations', 'counselor_messages');
```

**Output:** 2 tables + 5 indexes + 1 trigger function ✅

---

#### ✅ **Task 1.2: Create Sample Counselor Accounts** (30 phút)

**SQL to run:**

```sql
-- Tạo 3 counselors test
DO $$
DECLARE
    user1_id INTEGER;
    user2_id INTEGER;
    user3_id INTEGER;
BEGIN
    -- User 1: Dr. Nguyễn Văn A
    INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
    VALUES ('counselor1@ai4mind.com', '$2b$12$...', 'TS. Nguyễn Văn A', 'counselor', TRUE, TRUE)
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
    VALUES ('counselor2@ai4mind.com', '$2b$12$...', 'ThS. Trần Thị B', 'counselor', TRUE, TRUE)
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
    VALUES ('counselor3@ai4mind.com', '$2b$12$...', 'ThS. Lê Văn C', 'counselor', TRUE, TRUE)
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

    RAISE NOTICE 'Created 3 counselor accounts';
END $$;
```

**Note:** Hash password bằng bcrypt trước khi insert (hoặc dùng default password 'Test@123')

**Output:** 3 counselor accounts (2 available, 1 unavailable) ✅

---

### ⏰ AFTERNOON SESSION (3-4 giờ) - Backend Code

#### ✅ **Task 1.3: Create Models** (45 phút)

**File:** `ai-service/app/models/counselor_chat.py`

**Code:**

```python
"""
Counselor Chat models - Direct messaging between students and counselors
"""
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base

class CounselorConversation(Base):
    """Conversation thread between student and counselor"""
    __tablename__ = "counselor_conversations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    counselor_id = Column(Integer, ForeignKey("counselors.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    last_message_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    student = relationship("Student", foreign_keys=[student_id])
    counselor = relationship("Counselor", foreign_keys=[counselor_id])
    messages = relationship("CounselorMessage", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CounselorConversation(id={self.id}, student={self.student_id}, counselor={self.counselor_id})>"


class CounselorMessage(Base):
    """Individual message in counselor conversation"""
    __tablename__ = "counselor_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, ForeignKey("counselor_conversations.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'student' or 'counselor'
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    conversation = relationship("CounselorConversation", back_populates="messages")

    def __repr__(self):
        return f"<CounselorMessage(id={self.id}, sender={self.sender_type})>"
```

**Import vào `app/models/__init__.py`:**

```python
from app.models.counselor_chat import CounselorConversation, CounselorMessage
```

**Test:**

```python
python
>>> from app.models.counselor_chat import CounselorConversation
>>> print(CounselorConversation.__tablename__)  # Should print: counselor_conversations
```

---

#### ✅ **Task 1.4: Create Schemas** (45 phút)

**File:** `ai-service/app/schemas/counselor_chat.py`

**Code:**

```python
"""
Counselor Chat schemas for API validation and serialization
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# REQUEST SCHEMAS (Input)
# ============================================

class MessageCreate(BaseModel):
    """Request schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Em cảm thấy lo lắng về kỳ thi sắp tới"
            }
        }


class ConversationCreate(BaseModel):
    """Request schema for creating a conversation"""
    counselor_id: int = Field(..., description="ID of the counselor to chat with")

    class Config:
        json_schema_extra = {
            "example": {
                "counselor_id": 1
            }
        }


# ============================================
# RESPONSE SCHEMAS (Output)
# ============================================

class MessageResponse(BaseModel):
    """Response schema for a message"""
    id: int
    conversation_id: int
    sender_type: str = Field(..., description="'student' or 'counselor'")
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "sender_type": "counselor",
                "content": "Xin chào! Tôi là chuyên gia tâm lý...",
                "is_read": True,
                "created_at": "2025-10-05T10:30:00Z"
            }
        }


class ConversationResponse(BaseModel):
    """Response schema for a conversation"""
    id: int
    student_id: int
    counselor_id: int
    status: str
    last_message_at: datetime
    created_at: datetime
    unread_count: Optional[int] = 0  # Computed field

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": 5,
                "counselor_id": 1,
                "status": "active",
                "last_message_at": "2025-10-05T10:30:00Z",
                "created_at": "2025-10-05T10:00:00Z",
                "unread_count": 2
            }
        }


class CounselorInfo(BaseModel):
    """Basic counselor information"""
    id: int
    full_name: str
    specialization: Optional[str]
    years_of_experience: Optional[int]
    bio: Optional[str]
    is_available: bool

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Detailed conversation with counselor info and messages"""
    conversation: ConversationResponse
    counselor: CounselorInfo
    messages: List[MessageResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "conversation": {"id": 1, "student_id": 5, "counselor_id": 1, "status": "active"},
                "counselor": {"id": 1, "full_name": "TS. Nguyễn Văn A", "specialization": "Tâm lý lâm sàng"},
                "messages": [
                    {"id": 1, "sender_type": "counselor", "content": "Xin chào!"},
                    {"id": 2, "sender_type": "student", "content": "Chào cô ạ"}
                ]
            }
        }
```

---

#### ✅ **Task 1.5: Create Service** (1 giờ)

**File:** `ai-service/app/services/counselor_chat_service.py`

(Code quá dài - sẽ cung cấp trong file riêng)

**Key methods:**

- `get_available_counselors()` - List counselors với `is_available=True`
- `create_or_get_conversation(student_id, counselor_id)` - Create/get conversation
- `get_conversation_messages(conversation_id, user_id)` - Load messages
- `send_message(conversation_id, sender_type, content, user_id)` - Send message
- `mark_message_as_read(message_id)` - Mark read

---

#### ✅ **Task 1.6: Create API Endpoints** (1 giờ)

**File:** `ai-service/app/api/v1/endpoints/counselor_chat.py`

**Endpoints:**

```
GET    /api/v1/counselor-chat/counselors          # List available counselors
POST   /api/v1/counselor-chat/conversations       # Create conversation
GET    /api/v1/counselor-chat/conversations/{id}  # Get conversation detail
POST   /api/v1/counselor-chat/conversations/{id}/messages  # Send message
PATCH  /api/v1/counselor-chat/messages/{id}/read  # Mark as read
```

---

#### ✅ **Task 1.7: Register Router** (15 phút)

**File:** `ai-service/app/api/v1/api.py`

```python
from app.api.v1.endpoints import counselor_chat

api_router.include_router(
    counselor_chat.router,
    prefix="/counselor-chat",
    tags=["counselor-chat"]
)
```

---

#### ✅ **Task 1.8: Test với Postman/cURL** (30 phút)

**Test cases:**

```bash
# 1. List counselors
curl -X GET http://localhost:8000/api/v1/counselor-chat/counselors \
  -H "Authorization: Bearer <student_token>"

# 2. Create conversation
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"counselor_id": 1}'

# 3. Send message
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations/1/messages \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Xin chào cô!"}'

# 4. Get messages
curl -X GET http://localhost:8000/api/v1/counselor-chat/conversations/1 \
  -H "Authorization: Bearer <student_token>"
```

---

## 🗓️ DAY 2: FRONTEND IMPLEMENTATION (6-8 giờ)

(Chi tiết trong file riêng - rất dài)

**Summary:**

- Morning: Types + Service + CounselorListPage
- Afternoon: CounselorChatPage + Routing + Dashboard button

---

## 🗓️ DAY 3: TESTING & POLISH (4-6 giờ)

**Morning:** E2E testing, bug fixes
**Afternoon:** UI polish, documentation

---

## 📋 CHECKLIST TỔNG

### Database ✅

- [ ] Run `create_counselor_chat_tables.sql` trên Supabase
- [ ] Verify 2 tables created
- [ ] Verify 5 indexes created
- [ ] Create 3 sample counselor accounts
- [ ] Test với sample conversation

### Backend ✅

- [ ] Create `counselor_chat.py` models
- [ ] Create `counselor_chat.py` schemas
- [ ] Create `counselor_chat_service.py` service
- [ ] Create `counselor_chat.py` endpoints
- [ ] Register router in `api.py`
- [ ] Test all endpoints với Postman

### Frontend ✅

- [ ] Create `types/counselorChat.ts`
- [ ] Create `services/counselorChatService.ts`
- [ ] Create `CounselorListPage.tsx`
- [ ] Create `CounselorChatPage.tsx`
- [ ] Add routes to `App.tsx`
- [ ] Add dashboard button
- [ ] Test UI end-to-end

### Testing ✅

- [ ] Test student → counselor chat
- [ ] Test permissions (student A không xem chat của student B)
- [ ] Test real-time update (manual refresh)
- [ ] Test error handling
- [ ] Test responsive UI (mobile/desktop)

---

## 🚀 READY TO START?

**Bước đầu tiên:**

1. Mở Supabase Dashboard
2. Copy SQL từ `database/create_counselor_chat_tables.sql`
3. Run trong SQL Editor
4. Nhấn nút để bắt đầu! 🎯
