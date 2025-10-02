# 🔍 DATABASE-SERVICE: PHÂN TÍCH & ROADMAP

**Date**: October 1, 2025  
**Analyzed by**: AI Assistant  
**Purpose**: Xác định nỗ lực cần thiết để implement database-service

---

## 📊 1. PHÂN TÍCH HIỆN TRẠNG

### ✅ **Đã có sẵn trong ai-service:**

#### **Models** (app/models/)
```python
✅ User                 # Base authentication
✅ Student              # With gender field!
✅ Parent
✅ Counselor
✅ Assessment           # Psychological assessment
✅ VoiceAnalysis        # ⭐ ĐÃ CÓ FULL MODEL!
✅ Conversation         # Chat messages
✅ ParentConsent
✅ Base (SQLAlchemy declarative base)
```

#### **Schemas** (app/schemas/)
```python
✅ VoiceAnalysisCreate
✅ VoiceAnalysisResponse
✅ VoiceAnalysisDetail
✅ VoiceAnalysisSummary
✅ AudioFeatures
✅ EmotionScores
✅ PsychologicalMarkers
✅ Keyword
```

#### **Database** (app/db/)
```python
✅ database.py          # DB connection, SessionLocal, get_db()
✅ Alembic migrations   # Already configured
```

---

### ❌ **CHƯA CÓ:**

#### **API Endpoints**
```python
❌ POST /api/voice-analysis/analyze
❌ GET /api/voice-analysis/{id}
❌ GET /api/voice-analysis/student/{student_id}
❌ GET /api/voice-analysis/stats
```

#### **Business Logic**
```python
❌ Gọi voice-service
❌ Lưu kết quả vào VoiceAnalysis table
❌ File storage management
❌ Gender extraction từ Student
```

#### **Reporting/Analytics**
```python
❌ Statistics API
❌ Excel export
❌ PDF reports
❌ Dashboard data
```

---

## 🎯 2. KIẾN TRÚC MỤC TIÊU

```
┌─────────────────────────────────────────────────────────┐
│                    FINAL ARCHITECTURE                    │
└─────────────────────────────────────────────────────────┘

Frontend (React/Next.js)
    │
    ├────────────────────┬────────────────────┐
    ▼                    ▼                    ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ AI-SERVICE  │   │VOICE-SERVICE │   │DATABASE-     │
│ (Port 8000) │   │ (Port 8001)  │   │SERVICE       │
│             │   │              │   │(Port 8002)   │
│ Business    │───│ Processing   │   │ Analytics    │
│ CRUD        │   │ Whisper      │   │ Reports      │
│ Auth        │   │ Emotion      │   │ Excel        │
│ Main API    │   │ Stateless    │   │ Read-Only DB │
└─────────────┘   └──────────────┘   └──────────────┘
    │                                       │
    └───────────────┬───────────────────────┘
                    ▼
              ┌──────────┐
              │ SUPABASE │
              │PostgreSQL│
              └──────────┘
```

---

## 📋 3. CÔNG VIỆC CẦN LÀM

### **PHASE 1: Hoàn thiện AI-Service** ⭐ PRIORITY 1

#### 1.1. Tạo Voice Analysis Endpoint (ai-service)
**File**: `ai-service/app/api/v1/endpoints/voice_analysis.py` (NEW)
**Lines**: ~300 lines
**Time**: 2-3 hours

```python
# Key features:
✅ POST /api/voice-analysis/analyze
   - Upload audio file
   - Lấy student gender từ DB
   - Gọi voice-service
   - Lưu kết quả vào VoiceAnalysis table
   - Return response

✅ GET /api/voice-analysis/{id}
   - Get single analysis

✅ GET /api/voice-analysis/student/{student_id}
   - Get all analyses for student
   - Pagination support

✅ DELETE /api/voice-analysis/{id}
   - Soft delete or hard delete
```

**Dependencies**:
```python
import httpx              # ✅ Already in requirements
from sqlalchemy.orm       # ✅ Already in use
from app.models.voice_analysis import VoiceAnalysis  # ✅ Exists
from app.schemas.voice_analysis import VoiceAnalysisResponse  # ✅ Exists
```

**Effort**: 🟡 MEDIUM (model đã có, chỉ cần business logic)

---

#### 1.2. Update API Router
**File**: `ai-service/app/api/v1/api.py` (EDIT)
**Lines**: +2 lines
**Time**: 5 minutes

```python
# Add voice analysis router
from app.api.v1.endpoints import voice_analysis

api_router.include_router(
    voice_analysis.router, 
    prefix="/voice-analysis", 
    tags=["Voice Analysis"]
)
```

**Effort**: 🟢 EASY

---

#### 1.3. File Storage Management
**File**: `ai-service/app/utils/file_storage.py` (NEW)
**Lines**: ~150 lines
**Time**: 1 hour

```python
# Functions:
✅ save_audio_file(file, student_id) → file_path
✅ delete_audio_file(file_path)
✅ get_audio_file_url(file_path)
✅ cleanup_old_files(days=30)
```

**Storage Options**:
1. **Local disk** (development) - EASY
2. **Supabase Storage** (production) - MEDIUM
3. **AWS S3** (alternative) - MEDIUM

**Effort**: 🟡 MEDIUM

---

### **PHASE 2: Voice-Service Cleanup** ⭐ PRIORITY 2

#### 2.1. Remove Database Code
**Files to DELETE**:
```
❌ voice-service/app/db/database.py    (DELETE)
❌ voice-service/app/db/models.py      (DELETE)
❌ voice-service/app/db/__init__.py    (DELETE - if created)
```

**File to UPDATE**:
```python
# voice-service/app/api/v1/endpoints/analyze.py
✅ Remove database imports
✅ Keep gender as required parameter
✅ Focus on pure processing
```

**Effort**: 🟢 EASY (10 minutes)

---

#### 2.2. Update Documentation
**Files to UPDATE**:
```
✅ voice-service/README.md
✅ voice-service/DEPLOYMENT.md
✅ voice-service/API_DOCS.md
```

**Changes**:
- Remove database setup instructions
- Clarify: "Stateless processing service"
- Update: "Gender must be provided by caller"

**Effort**: 🟢 EASY (15 minutes)

---

### **PHASE 3: Database-Service** ⭐ PRIORITY 3 (OPTIONAL - có thể làm sau)

#### 3.1. Create Service Structure
**Time**: 1 hour

```
database-service/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py         # Read-only connection
│   ├── api/
│   │   └── v1/
│   │       ├── reports.py      # 📊 Statistics
│   │       ├── exports.py      # 📥 Excel/PDF
│   │       └── analytics.py    # 📈 Trends
│   ├── services/
│   │   ├── stats_service.py
│   │   ├── excel_service.py
│   │   └── pdf_service.py
│   └── models/
│       └── readonly.py         # Import from ai-service
├── requirements.txt
└── README.md
```

**Effort**: 🟡 MEDIUM

---

#### 3.2. Key Features
**Time**: 4-6 hours total

**Reports API** (~2 hours):
```python
GET /api/reports/student/{id}/summary
GET /api/reports/assessment/{id}/detailed
GET /api/reports/counselor/{id}/dashboard
```

**Statistics API** (~1 hour):
```python
GET /api/stats/emotion-distribution?period=month
GET /api/stats/assessment-trends?student_id=123
GET /api/stats/voice-analysis-summary
```

**Export API** (~2 hours):
```python
GET /api/exports/excel/assessment/{id}
GET /api/exports/pdf/student/{id}/report
GET /api/exports/csv/voice-analyses?student_id=123
```

**Analytics API** (~1 hour):
```python
GET /api/analytics/emotion-trends?days=30
GET /api/analytics/risk-levels
GET /api/analytics/counselor-workload
```

**Effort**: 🔴 HIGH (but can be done incrementally)

---

## ⏱️ 4. TỔNG THỜI GIAN ƯỚC TÍNH

### **Minimum Viable Product (MVP):**

| Phase | Task | Time | Priority |
|-------|------|------|----------|
| **PHASE 1** | **AI-Service Integration** | | |
| 1.1 | Voice Analysis Endpoint | 2-3h | ⭐⭐⭐ |
| 1.2 | Update Router | 5m | ⭐⭐⭐ |
| 1.3 | File Storage | 1h | ⭐⭐⭐ |
| **PHASE 2** | **Voice-Service Cleanup** | | |
| 2.1 | Remove DB Code | 10m | ⭐⭐ |
| 2.2 | Update Docs | 15m | ⭐⭐ |
| **PHASE 3** | **Database-Service** | | |
| 3.1 | Service Structure | 1h | ⭐ (optional) |
| 3.2 | Basic Reports | 2h | ⭐ (optional) |
| 3.2 | Excel Export | 2h | ⭐ (optional) |
| | | | |
| **TOTAL (MVP)** | **Without Database-Service** | **~4-5 hours** | ✅ |
| **TOTAL (Full)** | **With Database-Service** | **~9-11 hours** | 🎯 |

---

## 🎯 5. KHUYẾN NGHỊ TRIỂN KHAI

### **Option A: Fast Track** (Recommended)
```
Day 1: PHASE 1 - AI-Service Integration (4-5 hours)
       ✅ Voice analysis endpoint
       ✅ File storage
       ✅ Integration with voice-service
       ✅ Test end-to-end

Day 2: PHASE 2 - Voice-Service Cleanup (30 mins)
       ✅ Remove database code
       ✅ Update documentation

Day 3: Testing & Deployment
       ✅ Integration testing
       ✅ Frontend integration
       ✅ Deploy to production

Later: PHASE 3 - Database-Service (when needed)
       📊 Add when reporting requirements are clear
```

**Total Time**: **1-2 days for MVP**

---

### **Option B: Complete Implementation**
```
Week 1:
- Day 1-2: PHASE 1 (AI-Service)
- Day 3: PHASE 2 (Voice-Service cleanup)
- Day 4-5: PHASE 3 (Database-Service structure + basic reports)

Week 2:
- Day 1-2: Advanced reporting
- Day 3: Excel/PDF export
- Day 4: Analytics API
- Day 5: Testing & documentation
```

**Total Time**: **2 weeks for full stack**

---

## 📊 6. ĐÁNH GIÁ MỨC ĐỘ PHỨC TẠP

### **Các thành phần theo độ khó:**

| Component | Complexity | Reason |
|-----------|------------|--------|
| Voice Analysis Endpoint | 🟡 MEDIUM | Models có sẵn, chỉ cần logic |
| File Storage | 🟡 MEDIUM | Supabase Storage có SDK |
| Voice-Service Cleanup | 🟢 EASY | Chỉ xóa code dư |
| Database-Service Structure | 🟡 MEDIUM | Standard FastAPI setup |
| Excel Export | 🟡 MEDIUM | openpyxl có sẵn |
| PDF Reports | 🔴 HIGH | Layout design phức tạp |
| Advanced Analytics | 🔴 HIGH | Complex SQL queries |

---

## ✅ 7. CHECKLIST TRIỂN KHAI

### **PHASE 1: AI-Service (PRIORITY 1)**
- [ ] 1.1. Create `voice_analysis.py` endpoint file
  - [ ] POST /analyze endpoint
  - [ ] GET /{id} endpoint
  - [ ] GET /student/{student_id} endpoint
  - [ ] Error handling
  - [ ] Request validation
  
- [ ] 1.2. Implement file storage
  - [ ] Create `file_storage.py` utility
  - [ ] Save audio files
  - [ ] Delete audio files
  - [ ] Get file URLs
  
- [ ] 1.3. Integrate with voice-service
  - [ ] HTTP client setup (httpx)
  - [ ] Gender extraction from Student
  - [ ] Call voice-service API
  - [ ] Handle voice-service errors
  
- [ ] 1.4. Database operations
  - [ ] Save VoiceAnalysis record
  - [ ] Update processing status
  - [ ] Handle transactions
  
- [ ] 1.5. Testing
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] End-to-end test with real audio

### **PHASE 2: Voice-Service Cleanup**
- [ ] 2.1. Remove database code
  - [ ] Delete db/ folder
  - [ ] Remove DB imports
  - [ ] Update requirements.txt
  
- [ ] 2.2. Update documentation
  - [ ] Update README.md
  - [ ] Update API_DOCS.md
  - [ ] Update DEPLOYMENT.md

### **PHASE 3: Database-Service (OPTIONAL)**
- [ ] 3.1. Service setup
  - [ ] Create folder structure
  - [ ] Setup FastAPI app
  - [ ] Configure read-only DB
  - [ ] Health check endpoint
  
- [ ] 3.2. Reports API
  - [ ] Student summary
  - [ ] Assessment detailed
  - [ ] Counselor dashboard
  
- [ ] 3.3. Export API
  - [ ] Excel export
  - [ ] CSV export
  - [ ] PDF export (optional)
  
- [ ] 3.4. Analytics API
  - [ ] Emotion trends
  - [ ] Risk distribution
  - [ ] Workload analytics

---

## 💡 8. QUYẾT ĐỊNH CẦN LẤY

### **Câu hỏi cho bạn:**

1. **Scope**: Làm MVP (4-5 hours) hay Full (9-11 hours)?
2. **File Storage**: Local disk hay Supabase Storage?
3. **Database-Service**: Làm ngay hay để phase sau?
4. **Excel/PDF**: Cần format gì? Có template mẫu không?
5. **Analytics**: Cần charts gì? Realtime hay cached?

---

## 🎯 9. KẾT LUẬN & KHUYẾN NGHỊ

### **✅ Khuyến nghị: BẮT ĐẦU VỚI PHASE 1 & 2**

**Lý do:**
1. **Models đã có sẵn** → Ít code cần viết
2. **Voice-service đã hoàn thành** → Chỉ cần integrate
3. **MVP có thể làm trong 1 ngày** → Fast iteration
4. **Database-service có thể làm sau** → When reporting needs clear

### **Roadmap đề xuất:**

```
🚀 IMMEDIATE (This week):
   ✅ PHASE 1: AI-Service Integration (4-5 hours)
   ✅ PHASE 2: Voice-Service Cleanup (30 mins)
   ✅ End-to-end testing
   ✅ Frontend integration

📊 NEXT (When needed):
   ⏳ PHASE 3: Database-Service
   ⏳ Basic reports (2 hours)
   ⏳ Excel export (2 hours)
   ⏳ Advanced analytics (optional)
```

---

## 📝 10. HÀNH ĐỘNG TIẾP THEO

**Bạn muốn:**
1. **Bắt đầu PHASE 1 ngay** (implement voice analysis endpoint) ⭐
2. **Review code structure trước** (check hiện tại cần sửa gì)
3. **Plan chi tiết hơn** (breakdown tasks nhỏ hơn)
4. **Tạo database-service structure trước** (prepare for future)

---

**Prepared by**: AI Assistant  
**Date**: October 1, 2025  
**Status**: Ready for implementation 🚀
