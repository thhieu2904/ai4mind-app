# 🔧 HƯỚNG DẪN CẬP NHẬT CODE SAU KHI MIGRATE DATABASE

**Tài liệu này:** Hướng dẫn chi tiết các thay đổi code cần thiết sau migration database  
**Áp dụng cho:** Backend (Python/SQLAlchemy) và Frontend (TypeScript/React)

---

## 📋 MỤC LỤC

1. [Migration 001: Add Indices](#migration-001-add-indices)
2. [Migration 002: Add Timestamps](#migration-002-add-timestamps)
3. [Migration 003: Migrate IDs to BIGINT](#migration-003-migrate-ids-to-bigint)
4. [Migration 004: Add CHECK Constraints](#migration-004-add-check-constraints)
5. [Testing Checklist](#testing-checklist)

---

## Migration 001: Add Indices

### ✅ Code Changes Required: **NONE**

Indices là database optimization, không ảnh hưởng code.

**Action:** Không cần làm gì! 🎉

---

## Migration 002: Add Timestamps

### 📝 Backend Changes (Python)

#### Files cần cập nhật:

1. **`ai-service/app/models/counselor.py`**

```python
# Thêm imports nếu chưa có
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.sql import func

class Counselor(Base):
    # ... existing fields ...

    # ✅ THÊM 2 dòng này
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

2. **`ai-service/app/models/parent.py`**

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func

class Parent(Base):
    # ... existing fields ...

    # ✅ THÊM 2 dòng này
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

3. **`ai-service/app/models/counselor_chat.py`** (nếu có ParentConsent model)

```python
class ParentConsent(Base):
    # ... existing fields ...

    # ✅ THÊM 2 dòng này
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CounselorConversation(Base):
    # ... existing fields ...

    # ✅ THÊM 1 dòng này (created_at đã có)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### Schemas (Pydantic)

**File:** `ai-service/app/schemas/*.py`

```python
from datetime import datetime
from typing import Optional

class CounselorBase(BaseModel):
    # ... existing fields ...

    # ✅ THÊM vào response schemas
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

#### Alembic Migration (Optional)

Nếu dùng Alembic:

```bash
cd ai-service
alembic revision -m "Add timestamps to counselor, parent, parent_consents"
```

Sau đó edit file migration:

```python
def upgrade():
    op.add_column('counselors', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('counselors', sa.Column('updated_at', sa.DateTime(timezone=True)))
    # ... tương tự cho các bảng khác

def downgrade():
    op.drop_column('counselors', 'updated_at')
    op.drop_column('counselors', 'created_at')
    # ...
```

### 📝 Frontend Changes (TypeScript)

#### Files cần cập nhật:

**Nếu có types cho Counselor, Parent:**

```typescript
// frontend/src/types/auth.ts hoặc counselor.ts
export interface Counselor {
  // ... existing fields ...

  // ✅ THÊM 2 field này (optional vì legacy data không có)
  created_at?: string;
  updated_at?: string;
}

export interface Parent {
  // ... existing fields ...
  created_at?: string;
  updated_at?: string;
}
```

### ✅ Testing

```bash
# 1. Restart backend
cd ai-service
python -m app.main

# 2. Test create counselor
curl -X POST http://localhost:8000/api/counselors \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "license_number": "TEST123", ...}'

# 3. Verify timestamps are populated
# Check response có created_at và updated_at

# 4. Test update counselor
curl -X PUT http://localhost:8000/api/counselors/1 \
  -H "Content-Type: application/json" \
  -d '{"bio": "Updated bio"}'

# 5. Verify updated_at changed
```

---

## Migration 003: Migrate IDs to BIGINT

### 🔴 **CRITICAL:** Đây là breaking change lớn nhất

### 📝 Backend Changes (Python/SQLAlchemy)

#### Cập nhật TẤT CẢ models:

**Files cần sửa:** `ai-service/app/models/*.py` (9 files)

```python
# ❌ TRƯỚC (sai)
from sqlalchemy import Column, Integer, String, ForeignKey

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # ❌

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)  # ❌
    user_id = Column(Integer, ForeignKey("users.id"))  # ❌

# ✅ SAU (đúng)
from sqlalchemy import Column, BigInteger, String, ForeignKey

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)  # ✅

class Student(Base):
    __tablename__ = "students"
    id = Column(BigInteger, primary_key=True)  # ✅
    user_id = Column(BigInteger, ForeignKey("users.id"))  # ✅
```

#### Chi tiết từng file:

1. **`ai-service/app/models/user.py`**

```python
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Enum

class User(Base):
    id = Column(BigInteger, primary_key=True, index=True)  # Integer → BigInteger
```

2. **`ai-service/app/models/student.py`**

```python
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, Text

class Student(Base):
    id = Column(BigInteger, primary_key=True, index=True)  # Integer → BigInteger
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))  # Integer → BigInteger
    emergency_contact_parent_id = Column(BigInteger, ForeignKey("parents.id"))  # Integer → BigInteger
```

3. **`ai-service/app/models/parent.py`**

```python
class Parent(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    user_id = Column(BigInteger, ForeignKey("users.id"))  # Integer → BigInteger
```

4. **`ai-service/app/models/counselor.py`**

```python
class Counselor(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    user_id = Column(BigInteger, ForeignKey("users.id"))  # Integer → BigInteger
```

5. **`ai-service/app/models/assessment.py`**

```python
class Assessment(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    student_id = Column(BigInteger, ForeignKey("students.id"))  # Integer → BigInteger
```

6. **`ai-service/app/models/voice_analysis.py`**

```python
class VoiceAnalysis(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    student_id = Column(BigInteger, ForeignKey("students.id"))  # Integer → BigInteger
    assessment_id = Column(BigInteger, ForeignKey("assessments.id"))  # Integer → BigInteger
```

7. **`ai-service/app/models/conversation.py`**

```python
class Conversation(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    student_id = Column(BigInteger, ForeignKey("students.id"))  # Integer → BigInteger

class Message(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    conversation_id = Column(BigInteger, ForeignKey("conversations.id"))  # Integer → BigInteger
    voice_analysis_id = Column(BigInteger, ForeignKey("voice_analyses.id"))  # Integer → BigInteger
```

8. **`ai-service/app/models/ai_chat.py`**

```python
# AI Conversations đã là BigInteger, chỉ cần update FKs
class AIConversation(Base):
    # id đã là BigInteger (không cần sửa)
    student_id = Column(BigInteger, ForeignKey("students.id"))  # Integer → BigInteger
    latest_assessment_id = Column(BigInteger, ForeignKey("assessments.id"))  # Integer → BigInteger

class AIMessage(Base):
    # id đã là BigInteger (không cần sửa)
    conversation_id = Column(BigInteger, ForeignKey("ai_conversations.id"))  # KHÔNG SỬA (đã đúng)
    related_assessment_id = Column(BigInteger, ForeignKey("assessments.id"))  # Integer → BigInteger
```

9. **`ai-service/app/models/counselor_chat.py`**

```python
class CounselorConversation(Base):
    # id đã là BigInteger
    student_id = Column(BigInteger, ForeignKey("students.id"))  # Integer → BigInteger
    counselor_id = Column(BigInteger, ForeignKey("counselors.id"))  # Integer → BigInteger

class CounselorMessage(Base):
    # id đã là BigInteger
    conversation_id = Column(BigInteger, ForeignKey("counselor_conversations.id"))  # KHÔNG SỬA

class ParentConsent(Base):
    id = Column(BigInteger, primary_key=True)  # Integer → BigInteger
    student_id = Column(BigInteger, ForeignKey("students.id"))  # Integer → BigInteger
    parent_id = Column(BigInteger, ForeignKey("parents.id"))  # Integer → BigInteger
```

### 📝 Frontend Changes (TypeScript)

#### ✅ **KHÔNG CẦN SỬA GÌ!** (JavaScript handles this automatically)

```typescript
// ✅ TypeScript/JavaScript xử lý number tự động
// KHÔNG CẦN SỬA
interface User {
  id: number; // ✅ Works for both INTEGER and BIGINT
}

// ⚠️ CHÚ Ý: JavaScript Number an toàn đến 2^53 (9 quadrillion)
// Nếu có ID > 9007199254740991, cần dùng BigInt hoặc string
// Nhưng với BIGINT trong Postgres, cực kỳ hiếm gặp
```

**Nếu lo lắng về số lớn (không cần thiết hiện tại):**

```typescript
// Option 1: Dùng string cho IDs cực lớn
interface User {
  id: string; // Convert BIGINT to string
}

// Option 2: Dùng BigInt (ES2020+)
interface User {
  id: bigint;
}
```

### 📝 API Serialization

**FastAPI/Pydantic tự động handle!**

```python
# ✅ Pydantic schema KHÔNG CẦN SỬA
class UserResponse(BaseModel):
    id: int  # ✅ Works for both Integer and BigInteger in SQLAlchemy

    class Config:
        from_attributes = True
```

### ✅ Testing

```bash
# 1. Restart backend sau khi update models
cd ai-service
python -m app.main

# 2. Test CRUD operations
# Create
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "student_code": "SV001", ...}'

# Read
curl http://localhost:8000/api/students/1

# Update
curl -X PUT http://localhost:8000/api/students/1 \
  -H "Content-Type: application/json" \
  -d '{"major": "Computer Science"}'

# Delete
curl -X DELETE http://localhost:8000/api/students/1

# 3. Verify JOIN queries work
curl http://localhost:8000/api/students/1/assessments

# 4. Verify foreign keys work
curl -X POST http://localhost:8000/api/assessments \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "answers": [...], ...}'
```

---

## Migration 004: Add CHECK Constraints

### 📝 Backend Changes (Python)

#### 1. Update Error Handling

**File:** `ai-service/app/api/*.py` (all API routers)

```python
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

@router.post("/assessments")
async def create_assessment(data: AssessmentCreate, db: Session = Depends(get_db)):
    try:
        # ... existing code ...
        db.add(assessment)
        db.commit()
        return assessment

    # ✅ THÊM xử lý constraint violations
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)

        # Parse constraint name và trả về user-friendly error
        if 'check_total_score_range' in error_message:
            raise HTTPException(
                status_code=400,
                detail="Invalid score: Total score must be between 0 and 21"
            )
        elif 'check_severity_level' in error_message:
            raise HTTPException(
                status_code=400,
                detail="Invalid severity level: Must be minimal, mild, moderate, or severe"
            )
        elif 'check_answers_structure' in error_message:
            raise HTTPException(
                status_code=400,
                detail="Invalid answers: Must be an array of exactly 7 numbers"
            )
        else:
            # Generic constraint violation
            raise HTTPException(
                status_code=400,
                detail=f"Data validation failed: {error_message}"
            )
```

#### 2. Update Validation Services

**File:** `ai-service/app/services/assessment_service.py`

```python
class AssessmentService:
    def create_assessment(self, db: Session, data: AssessmentCreate):
        # ✅ Có thể giảm validation ở service layer
        # Database constraints là safety net

        # Vẫn nên validate ở app layer để trả error tốt hơn
        if not (0 <= data.total_score <= 21):
            raise ValueError("Total score must be between 0 and 21")

        if len(data.answers) != 7:
            raise ValueError("GAD-7 requires exactly 7 answers")

        # ... rest of logic ...
```

**File:** `ai-service/app/services/voice_analysis_service.py`

```python
class VoiceAnalysisService:
    def save_analysis(self, db: Session, analysis_data: dict):
        # ✅ Validate trước khi save
        if analysis_data.get('sentiment_score'):
            score = analysis_data['sentiment_score']
            if not (-1 <= score <= 1):
                raise ValueError("Sentiment score must be between -1 and 1")

        if analysis_data.get('audio_duration'):
            duration = analysis_data['audio_duration']
            if duration <= 0:
                raise ValueError("Audio duration must be positive")

        # ... rest of logic ...
```

#### 3. Update Pydantic Schemas với Validators

**File:** `ai-service/app/schemas/assessment.py`

```python
from pydantic import BaseModel, field_validator, Field
from typing import List

class AssessmentCreate(BaseModel):
    student_id: int
    answers: List[int] = Field(..., min_length=7, max_length=7)
    total_score: int = Field(..., ge=0, le=21)
    severity_level: str
    functional_impairment: int | None = Field(None, ge=0, le=3)

    @field_validator('answers')
    def validate_answers(cls, v):
        if len(v) != 7:
            raise ValueError('Must have exactly 7 answers')
        if not all(0 <= ans <= 3 for ans in v):
            raise ValueError('Each answer must be 0-3')
        return v

    @field_validator('severity_level')
    def validate_severity(cls, v):
        if v not in ['minimal', 'mild', 'moderate', 'severe']:
            raise ValueError('Invalid severity level')
        return v
```

**File:** `ai-service/app/schemas/voice_analysis.py`

```python
from pydantic import BaseModel, field_validator, Field

class VoiceAnalysisCreate(BaseModel):
    sentiment_score: float | None = Field(None, ge=-1, le=1)
    emotion_confidence: float | None = Field(None, ge=0, le=1)
    audio_duration: float | None = Field(None, gt=0)
    processing_status: str = Field(default='pending')

    @field_validator('processing_status')
    def validate_status(cls, v):
        if v not in ['pending', 'processing', 'completed', 'failed']:
            raise ValueError('Invalid processing status')
        return v
```

### 📝 Frontend Changes (TypeScript)

#### Update Form Validation

**File:** `frontend/src/pages/AssessmentPage.tsx` (hoặc tương tự)

```typescript
// ✅ Frontend validation to match backend constraints
const validateAssessment = (data: AssessmentData): string[] => {
  const errors: string[] = [];

  // Total score validation
  if (data.totalScore < 0 || data.totalScore > 21) {
    errors.push("Tổng điểm phải từ 0 đến 21");
  }

  // Answers validation
  if (data.answers.length !== 7) {
    errors.push("Phải có đúng 7 câu trả lời");
  }

  if (!data.answers.every((ans) => ans >= 0 && ans <= 3)) {
    errors.push("Mỗi câu trả lời phải từ 0 đến 3");
  }

  // Severity level validation
  const validSeverities = ["minimal", "mild", "moderate", "severe"];
  if (!validSeverities.includes(data.severityLevel)) {
    errors.push("Mức độ nghiêm trọng không hợp lệ");
  }

  return errors;
};
```

#### Update API Error Handling

**File:** `frontend/src/services/api.ts` (hoặc axios interceptor)

```typescript
import axios from "axios";

// ✅ Better error messages từ backend constraints
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 400) {
      // Backend constraint violation
      const detail = error.response.data?.detail;

      if (detail?.includes("check_total_score_range")) {
        return Promise.reject(new Error("Tổng điểm không hợp lệ (0-21)"));
      } else if (detail?.includes("check_email_format")) {
        return Promise.reject(new Error("Định dạng email không hợp lệ"));
      } else {
        return Promise.reject(new Error(detail || "Dữ liệu không hợp lệ"));
      }
    }

    return Promise.reject(error);
  }
);
```

### ✅ Testing

```bash
# 1. Test constraint violations return proper errors

# Invalid score
curl -X POST http://localhost:8000/api/assessments \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "answers": [1,2,3,0,1,2,3], "total_score": 99, "severity_level": "severe"}'
# Expected: 400 error with message about score range

# Invalid email
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "password": "pass123", "full_name": "Test", "role": "STUDENT"}'
# Expected: 400 error with message about email format

# Invalid sentiment score
curl -X POST http://localhost:8000/api/voice-analyses \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "assessment_id": 1, "sentiment_score": 5.0, ...}'
# Expected: 400 error with message about sentiment range
```

---

## Testing Checklist

### ✅ Backend Testing

```bash
# 1. Database connection
python -c "from app.core.database import engine; print('DB OK' if engine.connect() else 'DB FAIL')"

# 2. Run pytest
cd ai-service
pytest tests/ -v

# 3. Manual API testing
# Test all CRUD endpoints với Postman/curl

# 4. Load testing (optional)
# Use locust or k6 for load testing
```

### ✅ Frontend Testing

```bash
# 1. Build check
cd frontend
npm run build

# 2. Type check
npm run type-check

# 3. Run tests
npm test

# 4. Manual testing
# - Create user → Create student → Create assessment
# - Verify IDs display correctly
# - Verify validation errors show properly
```

### ✅ Integration Testing

1. **Tạo user mới** → Verify ID là BIGINT
2. **Tạo assessment với invalid score** → Verify error message
3. **Tạo voice analysis** → Verify foreign keys work
4. **Query relationships** → Verify JOINs work correctly
5. **Update records** → Verify updated_at changes
6. **Search queries** → Verify indices improve performance

---

## 🚨 Common Issues & Solutions

### Issue 1: "Integer out of range" error

**Lỗi:**

```
sqlalchemy.exc.DataError: (psycopg2.errors.NumericValueOutOfRange)
integer out of range
```

**Nguyên nhân:** Chưa update model từ Integer → BigInteger

**Giải pháp:**

```python
# Sửa trong model
id = Column(BigInteger, primary_key=True)  # Không phải Integer
```

### Issue 2: Constraint violation không có error message rõ ràng

**Lỗi:**

```
IntegrityError: (psycopg2.errors.CheckViolation)
new row for relation "assessments" violates check constraint "check_total_score_range"
```

**Giải pháp:** Thêm proper error handling (xem section Migration 004)

### Issue 3: Frontend hiển thị ID sai

**Lỗi:** ID hiển thị là `[object Object]` hoặc undefined

**Nguyên nhân:** Response từ API không đúng format

**Giải pháp:**

```typescript
// Verify API response structure
console.log("User ID:", user.id, typeof user.id); // Should be 'number'
```

### Issue 4: Alembic detect không ra changes

**Lỗi:** `alembic revision --autogenerate` không tạo migration

**Giải pháp:**

```bash
# Force create migration
alembic revision -m "migrate to bigint"

# Manually edit migration file với content từ migration scripts
```

---

## 📚 Additional Resources

- **SQLAlchemy BigInteger docs:** https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.BigInteger
- **PostgreSQL BIGINT:** https://www.postgresql.org/docs/current/datatype-numeric.html
- **Pydantic Field validation:** https://docs.pydantic.dev/latest/concepts/fields/
- **FastAPI Error Handling:** https://fastapi.tiangolo.com/tutorial/handling-errors/

---

## ✅ Final Checklist

- [ ] Backup database trước khi migrate
- [ ] Test migration scripts trên staging
- [ ] Update all model files (Integer → BigInteger)
- [ ] Update error handling for constraints
- [ ] Update Pydantic schemas với validators
- [ ] Generate Alembic migrations
- [ ] Test all CRUD operations
- [ ] Test all JOIN queries
- [ ] Test error cases (invalid data)
- [ ] Deploy backend
- [ ] Monitor production 48h
- [ ] Update documentation

---

**Last updated:** 2025-10-07  
**Version:** 1.0
