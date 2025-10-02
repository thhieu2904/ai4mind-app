# 🧪 SECURITY TESTING GUIDE

**Date**: October 2, 2025  
**Status**: Ready to test!

---

## ✅ SERVICES RUNNING:

```
✅ ai-service:    http://127.0.0.1:8000
✅ voice-service: http://127.0.0.1:8001
```

---

## 🎯 TEST SCENARIO:

Chúng ta sẽ test xem **Student A** có thể access data của **Student B** không!

**Expected result**: ❌ **KHÔNG ĐƯỢC!** (Security working!)

---

## 📋 STEP-BY-STEP TESTING:

### **STEP 1: Health Check**

Mở **PowerShell mới** (không đóng 2 terminals đang chạy services):

```powershell
# Test ai-service
curl http://localhost:8000/health

# Test voice-service
curl http://localhost:8001/health
```

**Expected**:

```json
{"status":"healthy","service":"ai-service"}
{"status":"healthy","service":"voice-service"}
```

---

### **STEP 2: Register Student A**

```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "student_a@test.com",
    "password": "TestPass123!",
    "full_name": "Student A",
    "role": "student"
  }'
```

**Expected output**:

```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student_a@test.com",
    "full_name": "Student A",
    "role": "student"
  }
}
```

**💾 LƯU TOKEN:**

```powershell
$STUDENT_A_TOKEN = "eyJhbGci..."  # Copy access_token từ response
```

---

### **STEP 3: Register Student B**

```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "student_b@test.com",
    "password": "TestPass123!",
    "full_name": "Student B",
    "role": "student"
  }'
```

**💾 LƯU TOKEN:**

```powershell
$STUDENT_B_TOKEN = "eyJhbGci..."  # Copy access_token từ response
```

---

### **STEP 4: Create Student Profile for Student A**

```powershell
curl -X POST http://localhost:8000/api/v1/students `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $STUDENT_A_TOKEN" `
  -d '{
    "student_code": "SV001",
    "date_of_birth": "2000-01-01",
    "phone_number": "0123456789",
    "gender": "male",
    "university": "UIT",
    "major": "Computer Science",
    "year_of_study": 3
  }'
```

**Expected**: Student profile created (student_id = 1)

---

### **STEP 5: Create Student Profile for Student B**

```powershell
curl -X POST http://localhost:8000/api/v1/students `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $STUDENT_B_TOKEN" `
  -d '{
    "student_code": "SV002",
    "date_of_birth": "2000-02-02",
    "phone_number": "0987654321",
    "gender": "female",
    "university": "UIT",
    "major": "Information Systems",
    "year_of_study": 2
  }'
```

**Expected**: Student profile created (student_id = 2)

---

### **STEP 6: Download Test Audio File**

```powershell
# Download sample audio (Vietnamese speech)
curl -o test_audio.wav https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav

# Hoặc tạo file audio đơn giản
# (Nếu link trên không work, dùng bất kỳ file .wav nào bạn có)
```

---

### **STEP 7: Upload Voice Analysis (Student A)**

```powershell
curl -X POST http://localhost:8000/api/v1/voice-analysis/analyze `
  -H "Authorization: Bearer $STUDENT_A_TOKEN" `
  -F "audio_file=@test_audio.wav"
```

**Expected output**:

```json
{
  "id": 1,
  "student_id": 1,
  "audio_file_url": "https://...signed_url...",
  "transcription": "...",
  "emotions": {...},
  "status": "completed",
  "created_at": "2025-10-02T..."
}
```

**💾 LƯU ANALYSIS ID:**

```powershell
$ANALYSIS_ID = 1  # Copy id từ response
```

---

### **STEP 8: 🔒 TEST SECURITY - Student A can access own data**

```powershell
curl -X GET "http://localhost:8000/api/v1/voice-analysis/$ANALYSIS_ID" `
  -H "Authorization: Bearer $STUDENT_A_TOKEN"
```

**Expected**: ✅ `200 OK` - Student A xem được data của mình!

---

### **STEP 9: 🔒 TEST SECURITY - Student B CANNOT access Student A's data**

```powershell
curl -X GET "http://localhost:8000/api/v1/voice-analysis/$ANALYSIS_ID" `
  -H "Authorization: Bearer $STUDENT_B_TOKEN"
```

**Expected**: ❌ `404 Not Found` - **SECURITY WORKING!**

```json
{
  "detail": "Voice analysis not found"
}
```

**🎉 NẾU THẤY 404 → SECURITY ĐÃ HOẠT ĐỘNG ĐÚNG!**

---

### **STEP 10: 🔒 TEST SECURITY - Unauthenticated access blocked**

```powershell
curl -X GET "http://localhost:8000/api/v1/voice-analysis/$ANALYSIS_ID"
```

**Expected**: ❌ `401 Unauthorized`

```json
{
  "detail": "Not authenticated"
}
```

---

## ✅ SUCCESS CRITERIA:

```
✅ Student A can register & login
✅ Student B can register & login
✅ Student A can create profile
✅ Student B can create profile
✅ Student A can upload voice analysis
✅ Student A can access own data (200 OK)
❌ Student B CANNOT access Student A's data (404)
❌ Unauthenticated users blocked (401)
```

---

## 🎯 NẾU TẤT CẢ TEST PASS:

**Congratulations! 🎉**

Your security implementation is **PRODUCTION-READY**!

- ✅ Row Level Security (RLS) working
- ✅ Storage access control working
- ✅ Ownership verification working
- ✅ Authentication working
- ✅ Authorization working

---

## 🐛 NẾU CÓ LỖI:

### **Error 1: Cannot register user**

```
Lỗi: Email already exists
→ Đổi email khác hoặc delete user cũ trong database
```

### **Error 2: 500 Internal Server Error**

```
→ Check terminal logs của ai-service
→ Có thể là lỗi kết nối database hoặc Supabase keys sai
```

### **Error 3: Student B can see Student A's data (200 OK)**

```
→ RLS policies chưa hoạt động!
→ Kiểm tra lại Supabase SQL:
   SELECT tablename, rowsecurity FROM pg_tables
   WHERE tablename IN ('students', 'voice_analyses');
→ Phải thấy rowsecurity = t (true)
```

---

## 📊 TESTING CHECKLIST:

- [ ] Health check both services
- [ ] Register Student A
- [ ] Register Student B
- [ ] Create profile for Student A
- [ ] Create profile for Student B
- [ ] Upload voice analysis (Student A)
- [ ] Student A access own data (200 ✅)
- [ ] Student B access Student A's data (404 ❌)
- [ ] Unauthenticated access (401 ❌)

---

**Ready to test! Run commands và báo mình kết quả nhé! 🚀**
