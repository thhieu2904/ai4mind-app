# AI4Mind - Database Design Rationale

## 🎯 TẠI SAO CẦN 9 TABLES?

### Nguyên tắc thiết kế:

1. **Separation of Concerns** - Tách authentication khỏi business logic
2. **Normalization** - Tránh data duplication
3. **Scalability** - Dễ mở rộng thêm features
4. **Privacy by Design** - Consent-based access control

---

## 📊 DATABASE RELATIONSHIPS

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYER                      │
└─────────────────────────────────────────────────────────────┘
                             │
                      ┌──────┴──────┐
                      │    USERS    │ ← Central auth table
                      │  (id, email, │
                      │   password,  │
                      │    role)     │
                      └──────┬──────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐    ┌──────────────┐
│   STUDENTS   │     │   PARENTS    │    │  COUNSELORS  │
│ (student_id, │     │  (phone,     │    │  (license,   │
│  university, │     │  occupation) │    │  specialty)  │
│    major)    │     └──────┬───────┘    └──────────────┘
└──────┬───────┘            │
       │                    │
       │    ┌───────────────┘
       │    │
       │    ▼
       │ ┌──────────────────┐
       │ │ PARENT_CONSENTS  │ ← Privacy control
       │ │  (student_id,    │
       │ │   parent_id,     │
       │ │  is_approved)    │
       │ └──────────────────┘
       │
       │
       ├─────────────┬─────────────┬──────────────┐
       │             │             │              │
       ▼             ▼             ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│ ASSESSMENTS │ │CONVERSA- │ │ VOICE_   │ │  (future)  │
│ (answers,   │ │ TIONS    │ │ ANALYSES │ │  SESSIONS  │
│  score,     │ │ (title,  │ │(audio,   │ │  NOTES     │
│  analysis)  │ │ active)  │ │ emotion) │ │  REPORTS   │
└─────────────┘ └────┬─────┘ └──────────┘ └────────────┘
                     │
                     ▼
               ┌──────────┐
               │ MESSAGES │
               │ (role,   │
               │ content, │
               │ voice_id)│
               └──────────┘
```

---

## 🔐 ACCESS CONTROL MATRIX

| Table               | Student | Parent  | Counselor | Admin |
| ------------------- | ------- | ------- | --------- | ----- |
| **users**           | Own     | Own     | Own       | All   |
| **students**        | Own     | Child\* | All       | All   |
| **parents**         | View    | Own     | View      | All   |
| **parent_consents** | Approve | Request | View      | All   |
| **counselors**      | List    | List    | Own       | All   |
| **assessments**     | Own     | Child\* | All       | Stats |
| **conversations**   | Own     | ❌      | All       | ❌    |
| **messages**        | Own     | ❌      | All       | ❌    |
| **voice_analyses**  | Own     | ❌      | All       | Stats |

**Legend:**

- `Own`: Chỉ xem/sửa data của mình
- `Child*`: Chỉ nếu có consent approval
- `All`: Xem tất cả (read-only for counselors)
- `Stats`: Chỉ xem statistics, không xem raw data
- ❌: Không được phép truy cập

---

## 💡 WHY THIS DESIGN?

### ❓ Tại sao không dùng 1 table duy nhất?

```sql
-- ❌ BAD: Single table approach
users (id, email, password, role, student_code, parent_phone,
       counselor_license, university, major, occupation, ...)
```

**Vấn đề:**

1. **Null Hell**: Parent không có `student_code`, Student không có `counselor_license`
2. **Hard to Query**: `SELECT * FROM users WHERE student_code IS NOT NULL` - ugly!
3. **Hard to Extend**: Thêm field mới cho Student → affect ALL users
4. **Poor Performance**: Nhiều null columns, index không hiệu quả

---

### ❓ Tại sao không merge `conversations` + `messages`?

```sql
-- ❌ BAD: Single table
messages (id, student_id, role, content, created_at)
```

**Vấn đề:**

1. **No Grouping**: Không biết message nào thuộc conversation nào
2. **No Context**: Không track conversation title, active status
3. **Poor UX**: Student không thể organize/search conversations
4. **Hard to Archive**: Không thể archive old conversations

**✅ GOOD: Separate tables**

```
conversations (id, title, created_at, last_message_at)
  └─── messages (conversation_id, role, content)
```

**Lợi ích:**

- Group messages by conversation
- Track conversation metadata (title, status)
- Efficient queries: `GET /conversations` loads metadata only
- Lazy load messages: `GET /conversations/{id}/messages`

---

### ❓ Tại sao cần `voice_analyses` table riêng?

```sql
-- ❌ Alternative: Store in messages
messages (id, content, audio_file_path, transcription, emotion)
```

**Vấn đề:**

1. **Not all messages have voice**: Nhiều null columns
2. **Hard to Query**: "Find all voice messages with high anxiety emotion"
3. **Poor for Research**: Researchers muốn analyze voice data riêng

**✅ GOOD: Separate table**

```
voice_analyses (id, student_id, audio_path, transcription, emotions)
  ↑
messages (id, voice_analysis_id) -- optional link
```

**Lợi ích:**

- Clean separation: text messages vs voice messages
- Easy research queries: `SELECT * FROM voice_analyses WHERE dominant_emotion = 'anxious'`
- Optional relationship: Message có thể có hoặc không có voice

---

### ❓ Tại sao cần `parent_consents` table?

**Scenario 1: Không có consent table**

```sql
-- ❌ BAD: Direct relationship
parents (id, student_id) -- parent trực tiếp access student
```

**Vấn đề:** Student KHÔNG có control, parent tự động thấy mọi thứ

**Scenario 2: Boolean flag**

```sql
-- ❌ BAD: Simple flag
students (id, allow_parent_access BOOLEAN)
```

**Vấn đề:**

- Chỉ 1 parent được access
- Không track WHO is the parent
- Không track WHEN consent was given

**✅ GOOD: Separate consent table**

```sql
parent_consents (id, student_id, parent_id, is_approved, created_at)
```

**Lợi ích:**

- Multiple parents (divorced parents case)
- Track approval history
- Audit trail: "Parent X requested access on 2025-01-15"
- Revokable: Student có thể reject sau khi approve

---

## 🔍 QUERY EXAMPLES

### 1. Get student with all assessments

```sql
SELECT
  s.*,
  u.email, u.full_name,
  json_agg(a.*) as assessments
FROM students s
JOIN users u ON s.user_id = u.id
LEFT JOIN assessments a ON a.student_id = s.id
WHERE s.id = 1
GROUP BY s.id, u.id;
```

### 2. Get students with severe anxiety (counselor view)

```sql
SELECT
  s.*,
  u.full_name,
  a.total_score,
  a.completed_at
FROM students s
JOIN users u ON s.user_id = u.id
JOIN assessments a ON a.student_id = s.id
WHERE a.severity_level = 'severe'
  AND a.completed_at = (
    SELECT MAX(completed_at)
    FROM assessments
    WHERE student_id = s.id
  )
ORDER BY a.completed_at DESC;
```

### 3. Parent access check

```sql
SELECT
  s.*,
  a.*
FROM students s
JOIN parent_consents pc ON pc.student_id = s.id
JOIN assessments a ON a.student_id = s.id
WHERE pc.parent_id = ?
  AND pc.is_approved = 1;
```

### 4. Get conversation with messages and voice

```sql
SELECT
  c.*,
  json_agg(
    json_build_object(
      'id', m.id,
      'role', m.role,
      'content', m.content,
      'voice', v.transcription,
      'created_at', m.created_at
    ) ORDER BY m.created_at
  ) as messages
FROM conversations c
JOIN messages m ON m.conversation_id = c.id
LEFT JOIN voice_analyses v ON v.id = m.voice_analysis_id
WHERE c.id = ?
GROUP BY c.id;
```

---

## 📈 SCALABILITY CONSIDERATIONS

### Future Extensions (Easy to add):

#### 1. **Appointments Table**

```sql
appointments (
  id, student_id, counselor_id,
  scheduled_at, status, meeting_link
)
```

→ Student book appointments with counselor

#### 2. **Resources Table**

```sql
resources (
  id, title, type, content,
  severity_level, created_by
)
```

→ Counselors share helpful articles/videos

#### 3. **Notifications Table**

```sql
notifications (
  id, user_id, type, content,
  is_read, created_at
)
```

→ Alert student when assessment score is high

#### 4. **Mood Tracking Table**

```sql
mood_entries (
  id, student_id, mood_level,
  note, created_at
)
```

→ Daily mood journal (complement GAD-7)

#### 5. **Peer Support Groups**

```sql
support_groups (
  id, name, description, created_by
)
group_members (
  group_id, student_id, joined_at
)
```

→ Student support communities

---

## 🎓 DATABASE BEST PRACTICES USED

### ✅ 1. Primary Keys

- All tables have `id` as auto-increment primary key
- Consistent naming: always `id`, not `user_id` for primary key

### ✅ 2. Foreign Keys

- Clear naming: `user_id`, `student_id`, `conversation_id`
- Cascade deletes: `ON DELETE CASCADE` for dependent data
- Prevent orphans: `ON DELETE SET NULL` for optional relationships

### ✅ 3. Indexes

```sql
-- For fast lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_students_code ON students(student_code);
CREATE INDEX idx_assessments_student ON assessments(student_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

### ✅ 4. Timestamps

- All tables have `created_at` with `server_default=func.now()`
- Update tracking: `updated_at` with `onupdate=func.now()`

### ✅ 5. Soft Deletes (optional)

```sql
-- Instead of DELETE, mark as inactive
users (is_active BOOLEAN DEFAULT true)
conversations (is_active BOOLEAN DEFAULT true)
```

### ✅ 6. Data Types

- Enums for fixed values: `role`, `severity_level`
- JSON for flexible data: `answers`, `detected_emotions`
- Text for unlimited content: `content`, `analysis`

---

## 🚨 COMMON PITFALLS AVOIDED

### ❌ Storing sensitive data

```sql
-- ❌ BAD
users (password VARCHAR(255)) -- plain text!
```

✅ **Solution**: Use `hashed_password` with bcrypt

### ❌ Missing constraints

```sql
-- ❌ BAD
users (email VARCHAR(255)) -- duplicates allowed!
```

✅ **Solution**: `email UNIQUE NOT NULL`

### ❌ No audit trail

```sql
-- ❌ BAD: Can't track when consent was given
parent_consents (student_id, parent_id, is_approved)
```

✅ **Solution**: Add `created_at`, `updated_at`

### ❌ Hardcoded values

```sql
-- ❌ BAD
SELECT * FROM users WHERE role = 'student'; -- typo risk!
```

✅ **Solution**: Use Enum in code

```python
class UserRole(str, enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
```

---

## 📊 PERFORMANCE TIPS

### 1. Use Pagination

```python
# Don't load all messages at once
GET /conversations/1/messages?page=1&limit=20
```

### 2. Use Joins Wisely

```sql
-- ✅ GOOD: Single query
SELECT s.*, u.full_name
FROM students s
JOIN users u ON s.user_id = u.id;

-- ❌ BAD: N+1 queries
SELECT * FROM students;  -- 100 rows
for each student:
  SELECT * FROM users WHERE id = student.user_id;  -- 100 queries!
```

### 3. Use Indexes

```sql
-- Slow without index
SELECT * FROM assessments WHERE student_id = 1;  -- full table scan

-- Fast with index
CREATE INDEX idx_assessments_student ON assessments(student_id);
```

### 4. Cache Frequently Used Data

```python
# Cache user profile in Redis (5 min TTL)
cache.set(f"user:{user_id}", user_data, expire=300)
```

---

## 🎯 CONCLUSION

**9 tables = Right amount of normalization**

- Not too few (avoid null hell)
- Not too many (avoid over-engineering)
- Easy to understand
- Easy to extend
- Secure by design

**This database supports:**

- ✅ Multiple user roles with proper access control
- ✅ Privacy-first design (consent-based access)
- ✅ Scalable for 1000+ students
- ✅ Rich mental health tracking
- ✅ AI integration ready
- ✅ Research-friendly data structure

**Next step:** Implement API endpoints to use this database! 🚀
