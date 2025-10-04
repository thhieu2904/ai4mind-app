# 🧪 HƯỚNG DẪN TEST AI CHAT

## ✅ Chuẩn bị

### 1. Backend đã chạy

```bash
cd ai-service
conda activate ai4mind  # hoặc tên env của bạn
uvicorn app.main:app --reload
```

### 2. Cập nhật test credentials

Mở file `scripts/test-ai-chat-api.py` và sửa dòng 15-17:

```python
# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "your-email@example.com"  # ← Sửa email của bạn
TEST_PASSWORD = "your-password"         # ← Sửa password của bạn
```

**Lưu ý:** Dùng account **student** (không phải parent/counselor)

---

## 🚀 Chạy Test

### Option 1: Test API (Recommended)

```bash
cd scripts
python test-ai-chat-api.py
```

**Test này sẽ:**

- ✓ Login và lấy JWT token
- ✓ Tạo/lấy conversation
- ✓ Load messages hiện có
- ✓ Gửi message test: "Xin chào! Tôi muốn được tư vấn về sức khỏe tinh thần."
- ✓ Nhận AI response
- ✓ Hiển thị assessment context (nếu có)
- ✓ List conversation history

### Option 2: Test Multiple Messages (Uncomment trong script)

Để test conversation flow với nhiều messages, mở `test-ai-chat-api.py` và uncomment dòng 205:

```python
# Step 5: Test conversation flow with multiple messages
# Uncomment if you want to test multiple messages
test_multiple_messages(token)  # ← Uncomment dòng này
```

Sẽ gửi 3 messages:

1. "Xin chào, tôi là sinh viên đang học đại học"
2. "Gần đây tôi hay lo lắng về kết quả học tập"
3. "Bạn có lời khuyên gì giúp tôi giảm stress không?"

---

## 📊 Kết quả mong đợi

### ✅ Success Output:

```
============================================================
  AI CHAT API TEST SUITE
============================================================

Testing API at: http://localhost:8000/api/v1
Using credentials: your-email@example.com

============================================================
 1. LOGIN
============================================================
✓ Login successful
  Token: eyJhbGciOiJIUzI1NiI...

============================================================
 2. GET/CREATE CONVERSATION
============================================================
✓ Conversation retrieved/created
  ID: 1
  Title: Chat 05/10/2025
  Messages: 1
  Active: True

============================================================
 3. GET MESSAGES
============================================================
✓ Retrieved 1 messages
  🤖 assistant: Xin chào! 👋 Tôi là AI4Mind Assistant...

============================================================
 4. SEND MESSAGE
============================================================
User: Xin chào! Tôi muốn được tư vấn về sức khỏe tinh thần.

✓ Message sent and AI responded

AI Response:
------------------------------------------------------------
[AI response về mental health support sẽ hiện ở đây]
------------------------------------------------------------

📊 Assessment Context:
  Score: 12/21
  Severity: moderate
  Date: 04/10/2025

============================================================
  ✓ ALL TESTS COMPLETED SUCCESSFULLY
============================================================
```

---

## 🔍 Verify trong Database

### Check messages trong Supabase:

```sql
-- Xem conversations
SELECT * FROM ai_conversations
ORDER BY last_message_at DESC
LIMIT 5;

-- Xem messages
SELECT
  id,
  role,
  LEFT(content, 50) as content_preview,
  created_at
FROM ai_messages
WHERE conversation_id = 1  -- Thay bằng ID conversation của bạn
ORDER BY created_at;
```

---

## ❌ Troubleshooting

### Lỗi: "Login failed: 401"

→ Sai email/password. Kiểm tra credentials trong script.

### Lỗi: "Student profile not found"

→ Account không phải student role. Tạo hoặc dùng account student khác.

### Lỗi: "Connection refused"

→ Backend chưa chạy. Start lại backend:

```bash
cd ai-service
uvicorn app.main:app --reload
```

### Lỗi: "Table ai_conversations does not exist"

→ Chưa tạo tables trên Supabase. Xem file `docs/SUPABASE_SETUP_GUIDE.md`

---

## 🎯 Test Checklist

- [ ] Backend chạy tại http://localhost:8000
- [ ] Test credentials đã cập nhật trong script
- [ ] Account là student role (có student profile)
- [ ] Tables `ai_conversations` và `ai_messages` đã tạo trên Supabase
- [ ] Test API chạy thành công
- [ ] AI response có nội dung hợp lý
- [ ] Assessment context hiển thị đúng (nếu có GAD-7 assessment)
- [ ] Conversation history lưu đúng vào DB

---

## 📝 Notes

- Script sẽ **KHÔNG XÓA** data sau khi test
- Mỗi lần chạy sẽ thêm messages vào conversation hiện tại
- Muốn start conversation mới, uncomment dòng `end_conversation(token)` ở cuối script
- Check logs trong terminal backend để debug nếu có lỗi

---

**Next Steps sau khi test pass:**

1. ✅ Test frontend UI (npm run dev)
2. ✅ Test end-to-end flow qua browser
3. ✅ Test với nhiều assessment contexts khác nhau
4. ✅ Test conversation history persistence
