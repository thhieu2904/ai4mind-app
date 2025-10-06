# 🗄️ DỮ LIỆU AI CHAT - NGUỒN & FLOW

## ✅ CÓ, AI dựa vào dữ liệu PostgreSQL của bạn!

### 📊 FLOW DỮ LIỆU

```
┌─────────────────────────────────────────────────────────┐
│  USER ACTION: Gửi message "Tôi đang lo âu"             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 1: AIChatService - Load Context từ PostgreSQL    │
├─────────────────────────────────────────────────────────┤
│  1. Query Student Profile:                              │
│     SELECT * FROM students WHERE id = ?                 │
│     → Lấy: full_name, education_level, year_of_study   │
│                                                          │
│  2. Query Latest Assessment (GAD-7):                    │
│     SELECT * FROM assessments                           │
│     WHERE student_id = ? ORDER BY created_at DESC       │
│     LIMIT 1                                             │
│     → Lấy: score, severity, analysis, recommendations   │
│                                                          │
│  3. Query Recent Messages:                              │
│     SELECT * FROM ai_messages                           │
│     WHERE conversation_id = ?                           │
│     ORDER BY created_at DESC LIMIT 6                    │
│     → Lấy: 6 messages gần nhất để AI nhớ context       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Build Context Object                           │
├─────────────────────────────────────────────────────────┤
│  context = {                                            │
│    "assessment": {                                      │
│      "score": 12,              # Từ assessments table  │
│      "severity": "moderate",   # Từ assessments table  │
│      "date": "04/10/2025"      # Từ assessments table  │
│    },                                                   │
│    "recent_messages": [                                 │
│      {"role": "assistant", "content": "Xin chào..."},  │
│      {"role": "user", "content": "Tôi lo âu"},        │
│      ...                        # Từ ai_messages table │
│    ]                                                    │
│  }                                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 3: GeminiService - Gửi context tới Gemini AI     │
├─────────────────────────────────────────────────────────┤
│  Prompt được build:                                     │
│                                                          │
│  System: "Bạn là AI4Mind Assistant..."                 │
│                                                          │
│  Context: "Sinh viên này có kết quả GAD-7:             │
│            - Điểm: 12/21                                │
│            - Mức độ: Lo âu trung bình                   │
│            - Ngày làm: 04/10/2025"                      │
│                                                          │
│  History: [6 messages gần nhất]                         │
│                                                          │
│  New User Message: "Tôi đang lo âu"                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 4: Gemini AI xử lý & trả response                │
├─────────────────────────────────────────────────────────┤
│  AI biết:                                               │
│  ✓ User có assessment score 12 (moderate)              │
│  ✓ Conversation history (6 messages)                   │
│  ✓ Context về mental health                            │
│                                                          │
│  → Generate response phù hợp với tình trạng user       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 5: Save vào PostgreSQL                            │
├─────────────────────────────────────────────────────────┤
│  INSERT INTO ai_messages (conversation_id, role,        │
│                           content, created_at)          │
│  VALUES (?, 'user', 'Tôi đang lo âu', NOW())           │
│                                                          │
│  INSERT INTO ai_messages (conversation_id, role,        │
│                           content, created_at,          │
│                           related_assessment_id)        │
│  VALUES (?, 'assistant', '[AI response]', NOW(), ?)    │
│                                                          │
│  UPDATE ai_conversations                                │
│  SET last_message_at = NOW()                           │
│  WHERE id = ?                                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
                  SUCCESS ✅
```

---

## 🗂️ CÁC BẢNG POSTGRESQL ĐƯỢC SỬ DỤNG

### 1. **students** - Thông tin sinh viên

```sql
SELECT
  id,
  full_name,          -- Tên sinh viên
  education_level,    -- Đại học / THPT
  year_of_study,      -- Năm 1, 2, 3...
  user_id             -- Link to users table
FROM students
WHERE id = ?
```

**Được dùng để:** Hiểu background của user (sinh viên năm mấy, học trường nào)

---

### 2. **assessments** - Kết quả GAD-7

```sql
SELECT
  id,
  student_id,
  total_score,        -- 0-21 điểm
  severity_level,     -- minimal/mild/moderate/severe
  analysis,           -- Phân tích từ Gemini
  recommendations,    -- Lời khuyên
  created_at          -- Thời điểm làm test
FROM assessments
WHERE student_id = ?
ORDER BY created_at DESC
LIMIT 1
```

**Được dùng để:**

- AI biết mức độ lo âu hiện tại
- Adjust tone (nghiêm trọng → cẩn thận hơn)
- Đề xuất phù hợp

---

### 3. **ai_conversations** - Quản lý cuộc trò chuyện

```sql
SELECT
  id,
  student_id,
  latest_assessment_id,  -- Link to latest GAD-7
  title,
  is_active,             -- Conversation còn active không
  created_at,
  last_message_at
FROM ai_conversations
WHERE student_id = ? AND is_active = true
```

**Được dùng để:**

- Track conversation hiện tại
- Link assessment với conversation

---

### 4. **ai_messages** - Lưu toàn bộ chat history

```sql
SELECT
  id,
  conversation_id,
  role,                    -- 'user' hoặc 'assistant'
  content,                 -- Nội dung tin nhắn
  related_assessment_id,   -- Link to assessment (nếu có)
  created_at
FROM ai_messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 6                   -- Chỉ lấy 6 gần nhất (tối ưu chi phí)
```

**Được dùng để:**

- AI nhớ context conversation
- User xem lại history
- Export data sau này

---

## 🔗 QUAN HỆ GIỮA CÁC BẢNG

```
users (id)
  ↓
students (user_id) ────────┐
  ↓                        │
assessments (student_id)   │
  ↓                        │
ai_conversations ──────────┘
  (student_id, latest_assessment_id)
  ↓
ai_messages (conversation_id, related_assessment_id)
```

---

## ✅ XÁC NHẬN: AI DỰA VÀO DỮ LIỆU CỦA BẠN

### ✓ Students table

- Biết user là sinh viên năm mấy, trường nào
- Context về background học tập

### ✓ Assessments table (GAD-7)

- **QUAN TRỌNG NHẤT** - Biết mức độ lo âu
- Điểm số: 0-21
- Severity: minimal → severe
- Recommendations từ assessment trước

### ✓ AI Messages table

- History 6 messages gần nhất
- Nhớ những gì đã nói trước đó
- Không lặp lại câu hỏi

### ✓ Conversation table

- Track conversation state
- Link assessment context

---

## 💡 VÍ DỤ THỰC TẾ

**Scenario:** User có GAD-7 score = 15 (severe)

```python
# Code trong ai_chat_service.py - _generate_welcome_message()
if assessment.severity_level == "severe":
    return f"""Xin chào! 👋 Tôi là AI4Mind Assistant.

Tôi thấy em vừa hoàn thành bài đánh giá GAD-7 vào ngày {assessment.created_at.strftime('%d/%m/%Y')}.
Kết quả cho thấy em đang có mức độ lo âu khá cao ({score}/21 điểm).

Tôi ở đây để lắng nghe em. Em có muốn chia sẻ về những gì đang khiến em cảm thấy lo lắng không? 💙"""
```

➡️ AI **TỰ ĐỘNG** adjust message dựa trên `severity_level` từ database!

---

## 🎯 KẾT LUẬN

**CÓ**, AI chat **HOÀN TOÀN** dựa vào dữ liệu PostgreSQL:

| Dữ liệu            | Nguồn                    | Mục đích                        |
| ------------------ | ------------------------ | ------------------------------- |
| Student info       | `students` table         | Context về user                 |
| GAD-7 results      | `assessments` table      | **Core context** - mức độ lo âu |
| Chat history       | `ai_messages` table      | Nhớ conversation                |
| Conversation state | `ai_conversations` table | Quản lý session                 |

**Không có data từ DB = AI không có context = Responses generic!**

---

**📌 Điều này ĐÚNG với thiết kế của bạn từ đầu:**

> "người dùng bắt đầu chat --> gửi nội dung và thông tin của user (về thông tin GAD-7...)"

✅ **Confirmed: AI sử dụng PostgreSQL data để personalize responses!**
