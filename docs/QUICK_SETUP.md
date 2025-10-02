# 🚀 QUICK SETUP GUIDE - 5 MINUTES

## ✅ STEP 1: Update .env (DONE!)
```bash
✅ SUPABASE_ANON_KEY - Added!
✅ SUPABASE_SERVICE_ROLE_KEY - Added!
```

---

## 📦 STEP 2: Install Supabase SDK

**Terminal 1** (ai-service):
```bash
cd d:\job\ai4mind-app\ai-service
pip install supabase==2.0.3
```

**Expected output:**
```
Successfully installed supabase-2.0.3 ...
```

---

## 🗄️ STEP 3: Run RLS SQL Policies

### **Option A: Via Supabase Dashboard (Recommended)**

1. **Vào**: https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt/sql

2. **Click**: "New query"

3. **Copy toàn bộ file**: `database/rls_policies.sql`

4. **Paste vào SQL Editor**

5. **Click**: "Run" (hoặc Ctrl+Enter)

6. **Expected output**:
   ```
   ✅ Success. No rows returned (or similar message)
   ```

### **Option B: Via Terminal (Advanced)**

```bash
# Install Supabase CLI (if not installed)
npm install -g supabase

# Login
supabase login

# Run SQL
supabase db execute --file database/rls_policies.sql
```

---

## 🔥 STEP 4: Start Services

**Terminal 1** (ai-service):
```bash
cd d:\job\ai4mind-app\ai-service
uvicorn app.main:app --reload --port 8000
```

**Terminal 2** (voice-service):
```bash
cd d:\job\ai4mind-app\voice-service
uvicorn app.main:app --reload --port 8001
```

**Expected output (ai-service)**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Expected output (voice-service)**:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

---

## 🧪 STEP 5: Test Security

### **5.1: Health Check**

**Terminal 3**:
```bash
# Test ai-service
curl http://localhost:8000/health

# Test voice-service
curl http://localhost:8001/health
```

**Expected**:
```json
{"status": "healthy", "service": "ai-service"}
{"status": "healthy", "service": "voice-service"}
```

---

### **5.2: Register 2 Test Users**

**User A (Student A)**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student_a@test.com",
    "password": "TestPass123!",
    "full_name": "Student A",
    "role": "student"
  }'
```

**User B (Student B)**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student_b@test.com",
    "password": "TestPass123!",
    "full_name": "Student B",
    "role": "student"
  }'
```

**Expected**:
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": { ... }
}
```

**💾 Save tokens:**
```bash
# Save Student A's access_token
STUDENT_A_TOKEN="eyJhbGci..."

# Save Student B's access_token
STUDENT_B_TOKEN="eyJhbGci..."
```

---

### **5.3: Upload Voice Analysis (Student A)**

**Create test audio file** (or use existing):
```bash
# Download sample audio
curl -o test_audio.wav https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav
```

**Upload as Student A**:
```bash
curl -X POST http://localhost:8000/api/v1/voice-analysis/analyze \
  -H "Authorization: Bearer $STUDENT_A_TOKEN" \
  -F "audio_file=@test_audio.wav"
```

**Expected**:
```json
{
  "id": 1,
  "student_id": 1,
  "audio_file_url": "https://...signed_url...",
  "transcription": "...",
  "emotions": { ... },
  "status": "completed",
  "created_at": "2025-10-01T..."
}
```

**💾 Save analysis ID:**
```bash
ANALYSIS_ID=1
```

---

### **5.4: Test Security (CRITICAL)**

#### **Test 1: Student A can access own data** ✅
```bash
curl -X GET http://localhost:8000/api/v1/voice-analysis/$ANALYSIS_ID \
  -H "Authorization: Bearer $STUDENT_A_TOKEN"
```

**Expected**: `200 OK` with data

---

#### **Test 2: Student B CANNOT access Student A's data** ✅
```bash
curl -X GET http://localhost:8000/api/v1/voice-analysis/$ANALYSIS_ID \
  -H "Authorization: Bearer $STUDENT_B_TOKEN"
```

**Expected**: `404 Not Found` (security working!)
```json
{
  "detail": "Voice analysis not found"
}
```

**🎯 IF YOU GET 404 → SECURITY WORKING! ✅**

---

#### **Test 3: Unauthenticated access blocked** ✅
```bash
curl -X GET http://localhost:8000/api/v1/voice-analysis/$ANALYSIS_ID
```

**Expected**: `401 Unauthorized`
```json
{
  "detail": "Not authenticated"
}
```

---

## ✅ SUCCESS CRITERIA

```
✅ ai-service starts without errors
✅ voice-service starts without errors
✅ Can register 2 users
✅ Student A can upload voice analysis
✅ Student A can access own data
✅ Student B CANNOT access Student A's data (404)
✅ Unauthenticated users blocked (401)
```

---

## 🐛 TROUBLESHOOTING

### **Issue 1: `ModuleNotFoundError: No module named 'supabase'`**
**Solution**:
```bash
cd ai-service
pip install supabase==2.0.3
```

---

### **Issue 2: `supabase.storage.StorageException: Bucket not found`**
**Solution**: Create bucket in Supabase Dashboard
1. Vào: https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt/storage
2. Click "New bucket"
3. Name: `audio-files`
4. Public: ❌ (Private)
5. Click "Create bucket"

---

### **Issue 3: RLS policies not working**
**Solution**: Verify policies enabled
```sql
-- Run in Supabase SQL Editor
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('students', 'voice_analyses', 'assessments');
```

**Expected**: All should show `rowsecurity = true`

---

### **Issue 4: `401 Unauthorized` when accessing own data**
**Solution**: Check JWT token
```bash
# Decode token to verify
echo $STUDENT_A_TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq
```

**Should contain**:
```json
{
  "sub": "user_id_here",
  "role": "student",
  ...
}
```

---

## 📊 ARCHITECTURE SUMMARY

```
Frontend (Future)
   │
   ▼
AI-Service (Port 8000)
   │
   ├──→ Voice-Service (Port 8001) [Audio Processing]
   │
   └──→ Supabase
        ├─ PostgreSQL (Data) ✅
        │  └─ Row Level Security (RLS) ✅
        │
        └─ Storage (Audio Files) ✅
           └─ Access Control Policies ✅
```

---

## 🎯 NEXT STEPS

After testing passes:

1. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: Add security implementation with Supabase Storage and RLS"
   git push
   ```

2. **Deploy to production**:
   - Railway / Render / Vercel
   - Update production `.env`
   - Run RLS SQL in production DB

3. **Build frontend**:
   - Connect to API endpoints
   - Implement authentication
   - Upload voice analysis

---

## 📝 CHECKLIST

- [ ] Install supabase==2.0.3
- [ ] Run RLS SQL policies
- [ ] Start ai-service (port 8000)
- [ ] Start voice-service (port 8001)
- [ ] Register Student A
- [ ] Register Student B
- [ ] Upload voice analysis (Student A)
- [ ] Test access (Student A → ✅)
- [ ] Test cross-access (Student B → ❌ 404)
- [ ] Test unauthenticated (→ ❌ 401)

---

**Status**: Ready to test! 🚀
**Time**: ~5 minutes
**Difficulty**: Easy

**Let's go!** 💪
