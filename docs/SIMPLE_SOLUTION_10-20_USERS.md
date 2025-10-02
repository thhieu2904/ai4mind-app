# 🎯 GIẢI PHÁP ĐơN GIẢN CHO PROJECT 10-20 USERS

**Date**: October 1, 2025  
**Scope**: Personal project, 10-20 users  
**Philosophy**: Keep it simple, use what you have!

---

## ❓ CÂU HỎI CỦA BẠN

> "Mình có cloud rồi nên bạn không xây dựng database service hả?"

### **✅ TRẢ LỜI: KHÔNG CẦN DATABASE-SERVICE!**

**Lý do:**

1. ✅ **Bạn đã có Supabase** → Cloud database sẵn sàng
2. ✅ **10-20 users** → Không cần microservices phức tạp
3. ✅ **Supabase Storage** → Lưu audio WAV miễn phí
4. ✅ **Đơn giản hơn = Ít bug hơn**

---

## 🏗️ KIẾN TRÚC ĐƠN GIẢN (RECOMMENDED)

```
┌─────────────────────────────────────────────┐
│           USER (10-20 people)               │
└───────────────────┬─────────────────────────┘
                    │
         ┌──────────▼──────────┐
         │     FRONTEND        │
         │  (React/Next.js)    │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │   AI-SERVICE        │
         │   (Port 8000)       │
         │                     │
         │ • Auth              │
         │ • Business Logic    │
         │ • CRUD Operations   │
         │ • Call Voice Svc    │
         └──────┬──────────────┘
                │
                ├───────────────────┐
                │                   │
    ┌───────────▼─────┐    ┌───────▼────────┐
    │ VOICE-SERVICE   │    │   SUPABASE     │
    │  (Port 8001)    │    │   (CLOUD)      │
    │                 │    │                │
    │ • Whisper STT   │    │ ✅ PostgreSQL  │
    │ • Emotion AI    │    │ ✅ Storage     │
    │ • Processing    │    │ ✅ Auth        │
    │ • NO DATABASE   │    │ ✅ Real-time   │
    └─────────────────┘    └────────────────┘

KEY POINTS:
✅ ai-service → Kết nối Supabase (DB + Storage)
✅ voice-service → Xử lý thuần túy, không DB
✅ database-service → KHÔNG CẦN (folder trống)
```

---

## 📦 SUPABASE CÓ SẴN 2 THỨ BẠN CẦN

### **1️⃣ Supabase PostgreSQL Database**

```
✅ Đã có sẵn: Users, Students, VoiceAnalysis tables
✅ Free tier: Unlimited requests
✅ 500MB database (đủ cho 10-20 users)
✅ Connection pooling built-in
✅ Row Level Security (data isolation)
```

**Current Setup:**

```python
# ai-service/app/core/config.py
DATABASE_URL: str = "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"
```

**✅ Đã hoạt động tốt!**

---

### **2️⃣ Supabase Storage** (CHưa SETUP)

```
✅ Lưu audio WAV files
✅ Free tier: 1GB storage
✅ CDN built-in (fast access)
✅ Public/Private buckets
✅ Access control per user
```

**Setup cần làm:**

1. Create bucket "audio-files" trên Supabase
2. Add Python client code
3. Upload/download files

---

## 🚀 IMPLEMENTATION (SIMPLE VERSION)

### **STEP 1: Setup Supabase Storage (5 phút)**

#### **1.1. Tạo Bucket trên Supabase Dashboard:**

```
1. Vào https://app.supabase.com/project/[YOUR_PROJECT]/storage
2. Click "New bucket"
3. Name: "audio-files"
4. Public: No (private for security)
5. Create
```

#### **1.2. Install Supabase Python Client:**

```bash
cd ai-service
pip install supabase
```

#### **1.3. Update Requirements:**

```txt
# ai-service/requirements.txt
supabase==2.0.3  # Add this line
```

---

### **STEP 2: Create Simple File Storage Utility**

```python
# ai-service/app/utils/storage.py (NEW FILE)

"""
Simple Supabase Storage for audio files
For 10-20 users - keep it simple!
"""

import os
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client
from app.core.config import settings

class SimpleStorage:
    """
    Simple file storage using Supabase
    Perfect for small projects (10-20 users)
    """

    def __init__(self):
        # Supabase client
        self.supabase: Client = create_client(
            settings.SUPABASE_PROJECT_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY  # Server-side key
        )
        self.bucket = "audio-files"

    def save_audio(self, file_content: bytes, student_id: int, filename: str) -> dict:
        """
        Save audio file to Supabase Storage

        Simple folder structure:
        audio-files/
          └── {student_id}/
              └── {filename}

        Args:
            file_content: Audio file bytes
            student_id: Student ID (for folder organization)
            filename: Original filename (e.g., "recording_2025_10_01.wav")

        Returns:
            {
                "path": "123/recording_2025_10_01.wav",
                "url": "https://...supabase.co/storage/v1/object/...",
                "size": 1024000
            }
        """
        # Simple path: {student_id}/{filename}
        file_path = f"{student_id}/{filename}"

        # Upload to Supabase
        self.supabase.storage.from_(self.bucket).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": "audio/wav"}
        )

        # Get signed URL (valid for 1 hour)
        signed_url = self.supabase.storage.from_(self.bucket).create_signed_url(
            path=file_path,
            expires_in=3600  # 1 hour
        )

        return {
            "path": file_path,
            "url": signed_url['signedURL'],
            "size": len(file_content)
        }

    def get_audio(self, file_path: str) -> bytes:
        """
        Download audio file from Supabase Storage

        Args:
            file_path: Path trong storage (e.g., "123/recording.wav")

        Returns:
            Audio file bytes
        """
        response = self.supabase.storage.from_(self.bucket).download(file_path)
        return response

    def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get temporary URL to access file

        Args:
            file_path: Path trong storage
            expires_in: Seconds (default 1 hour)

        Returns:
            Signed URL string
        """
        signed_url = self.supabase.storage.from_(self.bucket).create_signed_url(
            path=file_path,
            expires_in=expires_in
        )
        return signed_url['signedURL']

    def delete_audio(self, file_path: str) -> bool:
        """
        Delete audio file from Supabase Storage

        Args:
            file_path: Path trong storage

        Returns:
            True if success
        """
        try:
            self.supabase.storage.from_(self.bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

# Singleton instance
storage = SimpleStorage()
```

---

### **STEP 3: Update Config**

```python
# ai-service/app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # Supabase (ADD THESE)
    SUPABASE_PROJECT_URL: str = ""
    SUPABASE_ANON_KEY: str = ""           # For client-side
    SUPABASE_SERVICE_ROLE_KEY: str = ""   # For server-side (admin)

    # Database (already exists)
    DATABASE_URL: str = "postgresql://localhost/ai4mind"
```

---

### **STEP 4: Update .env**

```bash
# .env

# Supabase (ADD THESE)
SUPABASE_PROJECT_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database (already exists)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**Lấy keys ở đâu?**

1. Vào: https://app.supabase.com/project/[YOUR_PROJECT]/settings/api
2. Copy:
   - `Project URL` → SUPABASE_PROJECT_URL
   - `anon public` → SUPABASE_ANON_KEY
   - `service_role secret` → SUPABASE_SERVICE_ROLE_KEY

---

### **STEP 5: Use in Voice Analysis Endpoint**

```python
# ai-service/app/api/v1/endpoints/voice_analysis.py (NEW FILE)

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.core.database import get_db
from app.models.student import Student
from app.models.voice_analysis import VoiceAnalysis
from app.schemas.voice_analysis import VoiceAnalysisResponse
from app.utils.storage import storage  # Our simple storage!
from app.core.config import settings

router = APIRouter()

@router.post("/analyze", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    file: UploadFile = File(...),
    student_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Analyze voice - SIMPLE VERSION for 10-20 users

    Flow:
    1. Get student gender from DB
    2. Save audio to Supabase Storage
    3. Call voice-service for processing
    4. Save results to DB
    5. Return response
    """

    # 1. Get student
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    gender = student.gender or "prefer_not_to_say"

    # 2. Read audio file
    audio_bytes = await file.read()

    # 3. Save to Supabase Storage (SIMPLE!)
    file_info = storage.save_audio(
        file_content=audio_bytes,
        student_id=student_id,
        filename=file.filename
    )

    # 4. Call voice-service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VOICE_SERVICE_URL}/api/v1/voice/analyze",
            files={"file": (file.filename, audio_bytes, "audio/wav")},
            data={
                "user_id": str(student_id),
                "gender": gender
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Voice service error"
            )

        voice_result = response.json()

    # 5. Save to database
    voice_analysis = VoiceAnalysis(
        student_id=student_id,
        audio_file_path=file_info["path"],  # Path in Supabase
        file_size_bytes=file_info["size"],
        transcription=voice_result["transcription"],
        audio_features=voice_result["audio_features"],
        detected_emotions=voice_result["detected_emotions"],
        sentiment_score=voice_result["sentiment_score"],
        gender_used=gender,
        normalized_features=voice_result["normalized_features"],
        processing_status="completed"
    )

    db.add(voice_analysis)
    db.commit()
    db.refresh(voice_analysis)

    # 6. Return response
    return VoiceAnalysisResponse(
        id=voice_analysis.id,
        student_id=voice_analysis.student_id,
        audio_file_url=file_info["url"],  # Signed URL to download
        transcription=voice_analysis.transcription,
        detected_emotions=voice_analysis.detected_emotions,
        sentiment_score=voice_analysis.sentiment_score,
        created_at=voice_analysis.created_at
    )

@router.get("/{analysis_id}", response_model=VoiceAnalysisResponse)
async def get_voice_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get voice analysis by ID"""

    analysis = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Not found")

    # Get fresh signed URL (valid for 1 hour)
    audio_url = storage.get_url(analysis.audio_file_path)

    return VoiceAnalysisResponse(
        id=analysis.id,
        student_id=analysis.student_id,
        audio_file_url=audio_url,
        transcription=analysis.transcription,
        detected_emotions=analysis.detected_emotions,
        sentiment_score=analysis.sentiment_score,
        created_at=analysis.created_at
    )
```

---

## ✅ TÓM TẮT GIẢI PHÁP

### **Bạn CẦN:**

1. ✅ **Supabase PostgreSQL** → Đã có sẵn (lưu user data, voice analysis records)
2. ✅ **Supabase Storage** → Cần setup (lưu audio WAV files)

### **Bạn KHÔNG CẦN:**

1. ❌ **Database-service** → Không cần (dùng trực tiếp Supabase)
2. ❌ **AWS S3** → Không cần (Supabase Storage đủ)
3. ❌ **Redis Cache** → Không cần (10-20 users không cần cache)
4. ❌ **Complex microservices** → Không cần (keep it simple!)

---

## 📊 KIẾN TRÚC CUỐI CÙNG

```
┌──────────────┐
│   FRONTEND   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ AI-SERVICE   │──────┐
│              │      │
│ • Auth       │      ▼
│ • CRUD       │  ┌─────────────┐
│ • Upload     │  │  SUPABASE   │
│ • Download   │  │             │
└──────┬───────┘  │ ✅ Database │
       │          │ ✅ Storage  │
       ▼          └─────────────┘
┌──────────────┐
│VOICE-SERVICE │
│              │
│ • Whisper    │
│ • Emotion    │
│ • NO DB!     │
└──────────────┘
```

**Đơn giản, rõ ràng, dễ maintain!**

---

## 💰 CHI PHÍ (FREE!)

### **Supabase Free Tier:**

```
✅ Database: 500MB (đủ cho 10-20 users)
✅ Storage: 1GB (đủ cho hàng trăm audio files)
✅ Bandwidth: 2GB/month
✅ API requests: Unlimited
✅ Auth: Unlimited users
✅ Row Level Security: Yes
```

**→ Hoàn toàn MIỄN PHÍ cho project của bạn!**

---

## 🎯 HÀNH ĐỘNG TIẾP THEO

### **Option A: Setup ngay (30 phút)** ⭐⭐⭐

```
1. ✅ Tạo bucket "audio-files" trên Supabase (5 phút)
2. ✅ pip install supabase (1 phút)
3. ✅ Copy storage.py vào ai-service (2 phút)
4. ✅ Update .env với Supabase keys (2 phút)
5. ✅ Test upload/download (10 phút)
6. ✅ Create voice analysis endpoint (10 phút)
```

### **Option B: Mình implement giúp (1 giờ)** ⭐⭐

```
Mình sẽ:
1. Create file storage.py
2. Create voice_analysis.py endpoint
3. Update config.py
4. Test everything
5. Provide setup guide
```

---

## 📝 KẾT LUẬN

### **CÂU TRẢ LỜI CHO BẠN:**

> "Mình có cloud rồi nên bạn không xây dựng database service hả?"

**✅ ĐÚNG RỒI! Không cần database-service vì:**

1. Supabase = Cloud database + Cloud storage (2 in 1)
2. 10-20 users = Simple architecture is better
3. Database-service chỉ cần khi có hàng nghìn users
4. Keep it simple = Less bugs, easier maintenance

### **SUPABASE ĐÃ CÓ SẴN:**

- ✅ PostgreSQL database (user data)
- ✅ Storage (audio WAV files)
- ✅ Authentication
- ✅ Real-time subscriptions
- ✅ Row-level security

**→ Dùng Supabase trực tiếp, không cần thêm service!**

---

**Bạn muốn:**

1. **Mình hướng dẫn setup Supabase Storage** (30 phút) ⭐
2. **Mình code sẵn file storage.py** (implement ngay)
3. **Review lại architecture trước** (discuss more)

Chọn option nào? 😊
