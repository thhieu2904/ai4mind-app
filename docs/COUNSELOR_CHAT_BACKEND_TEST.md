# COUNSELOR CHAT BACKEND TEST - POSTMAN/cURL COMMANDS

## Prerequisites

- Backend running: `cd ai-service && uvicorn app.main:app --reload --port 8000`
- Get student token: Login với student account
- Get counselor token: Login với counselor account (sau khi tạo)

---

## 1. LOGIN TO GET TOKENS

### Login as Student (example: existing student)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student1@example.com",
    "password": "your_password"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student1@example.com",
    "role": "student"
  }
}
```

**Save token:** `STUDENT_TOKEN=eyJhbGc...`

---

### Login as Counselor (if created in Task 1.2)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "counselor1@ai4mind.com",
    "password": "Test@123"
  }'
```

**Save token:** `COUNSELOR_TOKEN=eyJhbGc...`

---

## 2. LIST AVAILABLE COUNSELORS

**Endpoint:** `GET /api/v1/counselor-chat/counselors`

### cURL:

```bash
curl -X GET http://localhost:8000/api/v1/counselor-chat/counselors \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### PowerShell:

```powershell
$STUDENT_TOKEN = "your_token_here"

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/counselors" `
  -Method GET `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
  }
```

**Expected Response:**

```json
[
  {
    "id": 1,
    "user_id": 10,
    "full_name": "TS. Nguyễn Văn A",
    "specialization": "Tâm lý lâm sàng, Lo âu, Trầm cảm",
    "years_of_experience": 8,
    "bio": "Chuyên gia tâm lý lâm sàng với 8 năm kinh nghiệm hỗ trợ sinh viên",
    "is_available": true
  },
  {
    "id": 2,
    "user_id": 11,
    "full_name": "ThS. Trần Thị B",
    "specialization": "Tâm lý học tích cực, Stress management",
    "years_of_experience": 5,
    "bio": "Tư vấn viên chuyên về stress và cân bằng cuộc sống",
    "is_available": true
  }
]
```

---

## 3. CREATE CONVERSATION

**Endpoint:** `POST /api/v1/counselor-chat/conversations`

### cURL:

```bash
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "counselor_id": 1
  }'
```

### PowerShell:

```powershell
$body = @{
  counselor_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
    "Content-Type" = "application/json"
  } `
  -Body $body
```

**Expected Response:**

```json
{
  "id": 1,
  "student_id": 5,
  "counselor_id": 1,
  "status": "active",
  "last_message_at": "2025-10-05T10:00:00Z",
  "created_at": "2025-10-05T10:00:00Z",
  "unread_count": 0
}
```

**Save conversation ID:** `CONVERSATION_ID=1`

---

## 4. SEND MESSAGE (Student)

**Endpoint:** `POST /api/v1/counselor-chat/conversations/{conversation_id}/messages`

### cURL:

```bash
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations/1/messages \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Chào cô ạ! Em cảm thấy lo lắng về kỳ thi sắp tới, cô có thể tư vấn giúp em được không?"
  }'
```

### PowerShell:

```powershell
$body = @{
  content = "Chào cô ạ! Em cảm thấy lo lắng về kỳ thi sắp tới, cô có thể tư vấn giúp em được không?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations/1/messages" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
    "Content-Type" = "application/json"
  } `
  -Body $body
```

**Expected Response:**

```json
{
  "id": 1,
  "conversation_id": 1,
  "sender_type": "student",
  "content": "Chào cô ạ! Em cảm thấy lo lắng về kỳ thi sắp tới, cô có thể tư vấn giúp em được không?",
  "is_read": false,
  "created_at": "2025-10-05T10:05:00Z"
}
```

---

## 5. GET CONVERSATION DETAIL

**Endpoint:** `GET /api/v1/counselor-chat/conversations/{conversation_id}`

### cURL:

```bash
curl -X GET http://localhost:8000/api/v1/counselor-chat/conversations/1 \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations/1" `
  -Method GET `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
  }
```

**Expected Response:**

```json
{
  "conversation": {
    "id": 1,
    "student_id": 5,
    "counselor_id": 1,
    "status": "active",
    "last_message_at": "2025-10-05T10:05:00Z",
    "created_at": "2025-10-05T10:00:00Z",
    "unread_count": 0
  },
  "counselor": {
    "id": 1,
    "user_id": 10,
    "full_name": "TS. Nguyễn Văn A",
    "specialization": "Tâm lý lâm sàng, Lo âu, Trầm cảm",
    "years_of_experience": 8,
    "bio": "Chuyên gia tâm lý lâm sàng với 8 năm kinh nghiệm hỗ trợ sinh viên",
    "is_available": true
  },
  "messages": [
    {
      "id": 1,
      "conversation_id": 1,
      "sender_type": "student",
      "content": "Chào cô ạ! Em cảm thấy lo lắng về kỳ thi sắp tới...",
      "is_read": false,
      "created_at": "2025-10-05T10:05:00Z"
    }
  ]
}
```

---

## 6. SEND MESSAGE (Counselor Reply)

### cURL:

```bash
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations/1/messages \
  -H "Authorization: Bearer $COUNSELOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Xin chào em! Cô hiểu em đang lo lắng. Đây là cảm giác rất bình thường trước kỳ thi. Em có thể chia sẻ cụ thể hơn về những gì khiến em lo lắng không?"
  }'
```

### PowerShell:

```powershell
$COUNSELOR_TOKEN = "counselor_token_here"

$body = @{
  content = "Xin chào em! Cô hiểu em đang lo lắng. Đây là cảm giác rất bình thường trước kỳ thi. Em có thể chia sẻ cụ thể hơn về những gì khiến em lo lắng không?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations/1/messages" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $COUNSELOR_TOKEN"
    "Content-Type" = "application/json"
  } `
  -Body $body
```

---

## 7. MARK MESSAGE AS READ

**Endpoint:** `PATCH /api/v1/counselor-chat/messages/{message_id}/read`

### cURL:

```bash
curl -X PATCH http://localhost:8000/api/v1/counselor-chat/messages/2/read \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/messages/2/read" `
  -Method PATCH `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
  }
```

**Expected Response:**

```json
{
  "id": 2,
  "conversation_id": 1,
  "sender_type": "counselor",
  "content": "Xin chào em! Cô hiểu em đang lo lắng...",
  "is_read": true,
  "created_at": "2025-10-05T10:10:00Z"
}
```

---

## 8. MARK ALL MESSAGES AS READ

**Endpoint:** `POST /api/v1/counselor-chat/conversations/{conversation_id}/mark-all-read`

### cURL:

```bash
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations/1/mark-all-read \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations/1/mark-all-read" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
  }
```

**Expected Response:**

```json
{
  "success": true,
  "conversation_id": 1,
  "marked_count": 3,
  "message": "Marked 3 messages as read"
}
```

---

## 9. LIST MY CONVERSATIONS

**Endpoint:** `GET /api/v1/counselor-chat/conversations`

### cURL:

```bash
curl -X GET http://localhost:8000/api/v1/counselor-chat/conversations \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations" `
  -Method GET `
  -Headers @{
    "Authorization" = "Bearer $STUDENT_TOKEN"
  }
```

**Expected Response:**

```json
[
  {
    "id": 1,
    "student_id": 5,
    "counselor_id": 1,
    "status": "active",
    "last_message_at": "2025-10-05T10:10:00Z",
    "created_at": "2025-10-05T10:00:00Z",
    "unread_count": 0
  }
]
```

---

## TEST SEQUENCE (Full Flow)

```bash
# 1. Start server
cd ai-service
uvicorn app.main:app --reload --port 8000

# 2. Open new terminal and run tests
# Get student token
$STUDENT_TOKEN = (Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email":"student1@example.com","password":"your_password"}').access_token

# 3. List counselors
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/counselors" -Method GET -Headers @{"Authorization"="Bearer $STUDENT_TOKEN"}

# 4. Create conversation
$conv = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations" -Method POST -Headers @{"Authorization"="Bearer $STUDENT_TOKEN";"Content-Type"="application/json"} -Body '{"counselor_id":1}'

# 5. Send message
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations/$($conv.id)/messages" -Method POST -Headers @{"Authorization"="Bearer $STUDENT_TOKEN";"Content-Type"="application/json"} -Body '{"content":"Chào cô ạ!"}'

# 6. Get conversation detail
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/counselor-chat/conversations/$($conv.id)" -Method GET -Headers @{"Authorization"="Bearer $STUDENT_TOKEN"}
```

---

## EXPECTED ERRORS TO TEST

### 1. Student tries to send as counselor (should fail)

```bash
# Should return 403 Forbidden
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations/1/messages \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"content":"Test","sender_type":"counselor"}'
```

### 2. Access other student's conversation (should fail)

```bash
# Student B tries to access Student A's conversation
# Should return 403 Forbidden
```

### 3. Create conversation with unavailable counselor (should fail)

```bash
# Should return 400 Bad Request
curl -X POST http://localhost:8000/api/v1/counselor-chat/conversations \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"counselor_id":3}'  # Counselor 3 is not available
```

---

## SUCCESS CRITERIA ✅

- [ ] List counselors: Returns 2 available counselors
- [ ] Create conversation: Returns conversation with ID
- [ ] Send student message: Returns message with sender_type='student'
- [ ] Get conversation: Returns counselor info + messages
- [ ] Send counselor reply: Returns message with sender_type='counselor'
- [ ] Mark as read: Updates is_read to true
- [ ] Mark all read: Updates multiple messages
- [ ] List conversations: Returns student's conversations
- [ ] Permission check: Student A cannot access Student B's chat
- [ ] Unavailable counselor: Returns 400 error

---

## NEXT STEPS AFTER TESTING

1. ✅ All endpoints working → Proceed to Day 2 (Frontend)
2. ❌ Bugs found → Fix service/endpoint logic
3. 🔍 Database issues → Check migration, foreign keys, indexes
