# 🔒 ĐÁNH GIÁ SCHEMA & PHÂN QUYỀN - AI4MIND

**Date**: October 1, 2025  
**Scope**: Database schema, authentication, authorization, data isolation  
**Verdict**: ⚠️ **CẦN CẢI THIỆN** (hiện tại chưa tốt lắm)

---

## 📊 TÓM TẮT ĐÁNH GIÁ

### **✅ ĐIỂM TỐT (Đã làm tốt):**

1. **Database Schema Design** ⭐⭐⭐⭐⭐

   ```
   ✅ Relationships rõ ràng (User → Student → VoiceAnalysis)
   ✅ Foreign Keys đúng (ondelete="CASCADE")
   ✅ Indexes hợp lý (email, student_id, etc.)
   ✅ Data types phù hợp (JSON cho features)
   ✅ Timestamps đầy đủ (created_at, updated_at)
   ```

2. **Authentication** ⭐⭐⭐⭐

   ```
   ✅ JWT tokens (access + refresh)
   ✅ Password hashing (bcrypt)
   ✅ Email-based login
   ✅ Role-based user types
   ✅ Token verification
   ```

3. **Role Management** ⭐⭐⭐⭐
   ```
   ✅ UserRole enum (student, parent, counselor, admin)
   ✅ Role stored in JWT token
   ✅ Role-specific profiles (Student, Parent, Counselor)
   ```

---

### **❌ VẤN ĐỀ NGHIÊM TRỌNG (Cần fix ngay!):**

#### **1. KHÔNG CÓ ROW-LEVEL SECURITY** 🔴 CRITICAL

**Vấn đề:**

```python
# ai-service/app/api/v1/endpoints/assessments.py
@router.get("/", response_model=AssessmentListResponse)
async def list_assessments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Assessment)  # ❌ QUERY TẤT CẢ!

    # Có filter theo role sau đó
    # NHƯNG không filter theo user_id ngay từ đầu!
```

**Hậu quả:**

- ❌ Student A có thể thấy data của Student B (nếu biết ID)
- ❌ API endpoint không kiểm tra ownership
- ❌ Dễ bị tấn công IDOR (Insecure Direct Object Reference)

**Ví dụ tấn công:**

```bash
# Student A (user_id=1) đăng nhập
curl -H "Authorization: Bearer TOKEN_OF_USER_1" \
  https://api.ai4mind.com/api/v1/voice-analysis/999

# Nếu không check ownership → Student A thấy được voice analysis của Student B!
```

---

#### **2. KHÔNG CÓ KIỂM TRA OWNERSHIP** 🔴 CRITICAL

**Code hiện tại:**

```python
# Khi get voice analysis by ID
voice_analysis = db.query(VoiceAnalysis).filter(
    VoiceAnalysis.id == analysis_id
).first()

# ❌ KHÔNG CHECK: voice_analysis.student.user_id == current_user.id
# → Bất kỳ user nào cũng access được!
```

**Cần phải:**

```python
# ✅ Check ownership
voice_analysis = db.query(VoiceAnalysis).join(Student).filter(
    VoiceAnalysis.id == analysis_id,
    Student.user_id == current_user.id  # ⭐ CRITICAL!
).first()

if not voice_analysis:
    raise HTTPException(status_code=403, detail="Access denied")
```

---

#### **3. SUPABASE STORAGE KHÔNG CÓ ACCESS CONTROL** 🔴 CRITICAL

**Vấn đề:**

```
Bucket: audio-files
Files:
  - 1/recording_001.wav
  - 2/recording_001.wav

Nếu public = True:
  → Ai cũng access được!
  → https://xxx.supabase.co/storage/v1/object/public/audio-files/1/recording_001.wav

Nếu public = False (như bạn đã setup):
  → Cần signed URL
  → NHƯNG phải check xem user có quyền không!
```

**Cần phải:**

```python
# ✅ Check ownership trước khi tạo signed URL
def get_audio_url(file_path: str, current_user: User, db: Session):
    # Parse file_path: "1/recording_001.wav"
    student_id = int(file_path.split('/')[0])

    # Check ownership
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.user_id == current_user.id  # ⭐ CRITICAL!
    ).first()

    if not student:
        raise HTTPException(status_code=403, detail="Access denied")

    # Only then create signed URL
    return storage.get_signed_url(file_path)
```

---

#### **4. KHÔNG CÓ SUPABASE ROW LEVEL SECURITY (RLS)** 🟡 HIGH

**Hiện tại:**

```sql
-- Tables: users, students, voice_analyses
-- RLS: KHÔNG BẬT!

-- Nghĩa là:
-- Nếu ai đó có SERVICE_ROLE_KEY → access toàn bộ database!
-- Nếu dùng Python client trực tiếp → không có security layer!
```

**Cần phải:**

```sql
-- Enable RLS
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_analyses ENABLE ROW LEVEL SECURITY;

-- Policy: Students chỉ thấy data của mình
CREATE POLICY "Students can view own data"
ON students FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY "Students can view own voice analyses"
ON voice_analyses FOR SELECT
USING (
    student_id IN (
        SELECT id FROM students WHERE user_id = auth.uid()
    )
);

-- Policy: Counselors thấy data của students được assigned
CREATE POLICY "Counselors can view assigned students"
ON students FOR SELECT
USING (
    id IN (
        SELECT student_id FROM student_counselor_assignments
        WHERE counselor_id IN (
            SELECT id FROM counselors WHERE user_id = auth.uid()
        )
    )
);
```

---

#### **5. KHÔNG CÓ AUDIT LOGGING** 🟡 MEDIUM

**Vấn đề:**

```
Không track:
- ❌ Ai access data của ai?
- ❌ Ai tải audio files?
- ❌ Ai xóa voice analysis?
- ❌ Ai sửa student profile?

→ Không detect được security breach!
```

---

## 🔧 GIẢI PHÁP CHI TIẾT

### **FIX 1: Thêm Ownership Check vào API Endpoints** ⭐⭐⭐

```python
# ai-service/app/api/v1/endpoints/voice_analysis.py

from app.api.dependencies import get_current_user_student

# Dependency để check ownership
async def get_current_user_student(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Student:
    """
    Get current user's student profile
    Raises 403 if user is not a student
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Only students can access this endpoint"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return student


@router.get("/{analysis_id}")
async def get_voice_analysis(
    analysis_id: int,
    current_student: Student = Depends(get_current_user_student),  # ⭐ Use dependency
    db: Session = Depends(get_db)
):
    """
    Get voice analysis by ID
    WITH OWNERSHIP CHECK
    """
    # ✅ Query with ownership filter
    voice_analysis = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.id == analysis_id,
        VoiceAnalysis.student_id == current_student.id  # ⭐ CRITICAL!
    ).first()

    if not voice_analysis:
        raise HTTPException(
            status_code=404,
            detail="Voice analysis not found or access denied"
        )

    # Get signed URL with security check
    audio_url = storage.get_url(voice_analysis.audio_file_path)

    return {
        "id": voice_analysis.id,
        "audio_url": audio_url,
        "transcription": voice_analysis.transcription,
        # ... other fields
    }


@router.get("/student/{student_id}")
async def list_student_analyses(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all voice analyses for a student
    WITH ROLE-BASED ACCESS CONTROL
    """
    # ✅ Check access permission
    if current_user.role == UserRole.STUDENT:
        # Students can only see their own data
        student = db.query(Student).filter(
            Student.id == student_id,
            Student.user_id == current_user.id  # ⭐ CRITICAL!
        ).first()

        if not student:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == UserRole.COUNSELOR:
        # Counselors can see assigned students only
        # TODO: Check student_counselor_assignments table
        pass

    elif current_user.role == UserRole.ADMIN:
        # Admins can see all
        pass

    else:
        raise HTTPException(status_code=403, detail="Access denied")

    # Query analyses
    analyses = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.student_id == student_id
    ).all()

    return analyses
```

---

### **FIX 2: Setup Supabase Row Level Security** ⭐⭐

```sql
-- Run these SQL commands in Supabase SQL Editor

-- 1. Enable RLS on tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

-- 2. Create policies for students table
CREATE POLICY "Students can view own profile"
ON students FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY "Students can update own profile"
ON students FOR UPDATE
USING (user_id = auth.uid());

-- 3. Create policies for voice_analyses
CREATE POLICY "Students can view own voice analyses"
ON voice_analyses FOR SELECT
USING (
    student_id IN (
        SELECT id FROM students WHERE user_id = auth.uid()
    )
);

CREATE POLICY "System can insert voice analyses"
ON voice_analyses FOR INSERT
WITH CHECK (true);  -- Only service_role key can insert

-- 4. Create policies for assessments
CREATE POLICY "Students can view own assessments"
ON assessments FOR SELECT
USING (
    student_id IN (
        SELECT id FROM students WHERE user_id = auth.uid()
    )
);

-- 5. Counselor access (if needed later)
CREATE POLICY "Counselors can view assigned students"
ON students FOR SELECT
USING (
    id IN (
        SELECT student_id FROM student_counselor_assignments
        WHERE counselor_id IN (
            SELECT id FROM counselors WHERE user_id = auth.uid()
        )
    )
);
```

---

### **FIX 3: Secure Supabase Storage Access** ⭐⭐⭐

```python
# ai-service/app/utils/storage.py

class SecureStorage:
    """
    Secure file storage with ownership verification
    """

    def get_audio_url(
        self,
        file_path: str,
        current_user: User,
        db: Session
    ) -> str:
        """
        Get signed URL for audio file
        WITH OWNERSHIP CHECK
        """
        # Parse file_path: "student_id/filename.wav"
        try:
            student_id = int(file_path.split('/')[0])
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid file path")

        # ✅ Check ownership
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(
                Student.id == student_id,
                Student.user_id == current_user.id  # ⭐ CRITICAL!
            ).first()

            if not student:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to this file"
                )

        elif current_user.role == UserRole.COUNSELOR:
            # Check if counselor has access to this student
            # TODO: Check assignments
            pass

        elif current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")

        # ✅ Only then create signed URL
        signed_url = self.supabase.storage.from_(self.bucket).create_signed_url(
            path=file_path,
            expires_in=3600  # 1 hour
        )

        return signed_url['signedURL']

    def save_audio(
        self,
        file_content: bytes,
        current_user: User,
        db: Session,
        filename: str
    ) -> dict:
        """
        Save audio file to Supabase Storage
        WITH USER ISOLATION
        """
        # ✅ Get student profile
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=403,
                detail="Only students can upload audio"
            )

        student = db.query(Student).filter(
            Student.user_id == current_user.id
        ).first()

        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        # ✅ Save to user's own folder
        file_path = f"{student.id}/{filename}"

        self.supabase.storage.from_(self.bucket).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": "audio/wav"}
        )

        return {
            "path": file_path,
            "student_id": student.id,
            "size": len(file_content)
        }
```

---

### **FIX 4: Setup Supabase Storage Policies** ⭐⭐

```sql
-- Supabase Storage RLS Policies
-- Run in Supabase SQL Editor

-- 1. Enable RLS on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 2. Policy: Users can only access their own files
CREATE POLICY "Users can view own audio files"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'audio-files'
    AND (storage.foldername(name))[1] IN (
        SELECT id::text FROM students WHERE user_id = auth.uid()
    )
);

-- 3. Policy: Users can only upload to their own folder
CREATE POLICY "Users can upload to own folder"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'audio-files'
    AND (storage.foldername(name))[1] IN (
        SELECT id::text FROM students WHERE user_id = auth.uid()
    )
);

-- 4. Policy: Service role can access all (for admin operations)
CREATE POLICY "Service role full access"
ON storage.objects FOR ALL
USING (auth.role() = 'service_role');
```

---

## 📋 CHECKLIST SECURITY

### **DATABASE (Supabase PostgreSQL):**

- [x] ✅ Schema design tốt
- [x] ✅ Foreign keys + indexes
- [ ] ❌ Row Level Security (RLS) - **CẦN ENABLE**
- [ ] ❌ RLS Policies - **CẦN TẠO**
- [x] ✅ Timestamps tracking

### **AUTHENTICATION:**

- [x] ✅ JWT tokens
- [x] ✅ Password hashing
- [x] ✅ Token refresh
- [x] ✅ Role-based auth
- [ ] ⚠️ Token blacklist (cho logout) - **NÊN CÓ**

### **AUTHORIZATION:**

- [x] ✅ Role enum (student/parent/counselor/admin)
- [ ] ❌ Ownership checks trong API - **CẦN THÊM**
- [ ] ❌ Resource-level permissions - **CẦN THÊM**
- [ ] ⚠️ Counselor-student assignments - **NÊN CÓ**

### **FILE STORAGE:**

- [x] ✅ Supabase Storage setup
- [ ] ❌ Storage RLS policies - **CẦN THÊM**
- [ ] ❌ Ownership checks trước signed URL - **CẦN THÊM**
- [x] ✅ Private bucket
- [ ] ⚠️ File size limits - **NÊN CÓ**
- [ ] ⚠️ File type validation - **NÊN CÓ**

### **API SECURITY:**

- [x] ✅ JWT authentication
- [ ] ❌ Ownership verification - **CẦN THÊM**
- [ ] ⚠️ Rate limiting - **NÊN CÓ**
- [ ] ⚠️ Input validation - **CẦN CẢI THIỆN**
- [ ] ⚠️ CORS configuration - **CẦN REVIEW**

### **MONITORING & AUDIT:**

- [ ] ❌ Audit logs - **NÊN CÓ**
- [ ] ❌ Access logs - **NÊN CÓ**
- [ ] ❌ Error tracking (Sentry) - **NÊN CÓ**
- [ ] ❌ Performance monitoring - **NÊN CÓ**

---

## 🎯 HÀNH ĐỘNG ƯU TIÊN

### **CRITICAL (Làm ngay - 2-3 giờ):** 🔴

1. **Thêm ownership checks vào API endpoints**

   - Create `get_current_user_student` dependency
   - Add ownership filter vào tất cả queries
   - Test với 2 users khác nhau

2. **Secure Supabase Storage**

   - Update `storage.py` với ownership checks
   - Test access control

3. **Enable Supabase RLS**
   - Run SQL scripts để enable RLS
   - Create basic policies

### **HIGH PRIORITY (Tuần sau - 4-5 giờ):** 🟡

4. **Setup Storage RLS policies**

   - Configure bucket policies
   - Test file access control

5. **Add input validation**

   - File size limits (50MB)
   - File type validation (only WAV/MP3)
   - Sanitize filenames

6. **Add audit logging**
   - Log file uploads
   - Log data access
   - Log failed auth attempts

### **MEDIUM PRIORITY (Sau 2 tuần):** 🟢

7. **Rate limiting**
8. **Error tracking (Sentry)**
9. **Counselor-student assignments table**
10. **Token blacklist for logout**

---

## 💡 KẾT LUẬN

### **CÂU TRẢ LỜI CHO BẠN:**

> "Mình xử lý schema và phân quyền rất tốt rồi hả?"

### **⚠️ TRẢ LỜI: CHƯA TỐT LẮM!**

**Điểm tốt:**

- ✅ Database schema design: Xuất sắc! (5/5 ⭐)
- ✅ Authentication: Tốt! (4/5 ⭐)
- ✅ Role management: Tốt! (4/5 ⭐)

**Điểm yếu (CRITICAL):**

- ❌ Row Level Security: Chưa có! (0/5 ⭐)
- ❌ Ownership checks: Chưa có! (0/5 ⭐)
- ❌ Storage access control: Chưa có! (0/5 ⭐)
- ❌ API authorization: Yếu! (2/5 ⭐)

**Tổng điểm: 6/10** ⚠️

### **Rủi ro hiện tại:**

```
🔴 CRITICAL: Student A có thể thấy voice analysis của Student B
🔴 CRITICAL: Ai cũng có thể download audio files nếu biết path
🟡 HIGH: Không track được ai access data của ai
🟡 HIGH: Không có rate limiting → dễ bị DDoS
```

---

## 🚀 KHUYẾN NGHỊ

### **Cho project 10-20 users:**

**Option A: Quick Fix (2-3 giờ)** ⭐⭐⭐

```
1. ✅ Add ownership checks vào API
2. ✅ Secure storage.py với ownership verification
3. ✅ Enable basic Supabase RLS
4. ✅ Test với 2 users

→ Đủ an toàn cho 10-20 users!
```

**Option B: Production-Ready (1 tuần)**

```
1. ✅ All of Option A
2. ✅ Complete RLS policies
3. ✅ Storage RLS
4. ✅ Audit logging
5. ✅ Rate limiting
6. ✅ Error tracking

→ Enterprise-grade security!
```

---

**Bạn muốn:**

1. **Mình implement Quick Fix ngay** (2-3 giờ, đủ dùng) ⭐⭐⭐
2. **Mình guide bạn làm từng bước** (bạn tự code)
3. **Skip security vì chỉ test** (KHÔNG KHUYẾN NGHỊ!)
4. **Discuss thêm về architecture**

**Khuyến nghị: Option 1** → Mình implement ownership checks và RLS cơ bản, đảm bảo an toàn cho 10-20 users! 😊

Bạn chọn nào?
