# 📊 PHÂN TÍCH SCHEMA VÀ KẾ HOẠCH CẢI THIỆN DATABASE

**Ngày phân tích:** 7 tháng 10, 2025  
**Hệ thống:** AI4Mind Application - Supabase PostgreSQL

---

## 📋 MỤC LỤC

1. [Tổng quan hiện trạng](#1-tổng-quan-hiện-trạng)
2. [Các vấn đề đã phát hiện](#2-các-vấn-đề-đã-phát-hiện)
3. [Đề xuất cải thiện](#3-đề-xuất-cải-thiện)
4. [Mức độ ảnh hưởng đến code](#4-mức-độ-ảnh-hưởng-đến-code)
5. [Kế hoạch triển khai](#5-kế-hoạch-triển-khai)
6. [Migration Scripts](#6-migration-scripts)

---

## 1. TỔNG QUAN HIỆN TRẠNG

### 1.1. Cấu trúc bảng hiện tại

```
users (10 bảng chính)
├── students
├── parents
├── counselors
│
assessments
├── voice_analyses
│
ai_conversations
├── ai_messages
│
conversations (legacy)
├── messages (legacy)
│
counselor_conversations
├── counselor_messages
│
parent_consents
medical_centers
```

### 1.2. Thống kê

- **Tổng số bảng:** 14 bảng
- **Quan hệ:** ~20 foreign keys
- **Indices:** Thiếu nhiều indices quan trọng
- **Constraints:** Thiếu check constraints và unique constraints

---

## 2. CÁC VẤN ĐỀ ĐÃ PHÁT HIỆN

### 🔴 **CẤP ĐỘ NGHIÊM TRỌNG CAO**

#### 2.1. **Kiểu dữ liệu không nhất quán**

| Bảng                                          | Cột        | Vấn đề                         | Ảnh hưởng                            |
| --------------------------------------------- | ---------- | ------------------------------ | ------------------------------------ |
| `users`, `students`, `assessments`            | `id`       | Trộn lẫn `integer` và `bigint` | Giới hạn số lượng records, khó scale |
| `ai_conversations`, `counselor_conversations` | `id`       | Dùng `bigint`                  | Không nhất quán với bảng khác        |
| `phone_number`, `phone`                       | Nhiều bảng | Không chuẩn hóa độ dài         | Validation khó khăn                  |

**Chi tiết:**

```sql
-- ❌ Không nhất quán
users.id              -> integer (max: 2.1 tỷ)
students.id           -> integer
assessments.id        -> integer
ai_conversations.id   -> bigint  (max: 9.2 quintillion)
counselor_conversations.id -> bigint

-- ⚠️ Vấn đề:
-- - Khi có > 2.1 tỷ users → overflow
-- - Không thể JOIN hiệu quả giữa integer và bigint
-- - Wasted storage cho bảng nhỏ dùng bigint
```

#### 2.2. **Thiếu indices quan trọng**

```sql
-- ❌ Các truy vấn thường xuyên KHÔNG có index:

-- 1. Tìm students theo user_id (đã có unique nhưng chưa rõ index)
SELECT * FROM students WHERE user_id = ?;

-- 2. Lọc assessments theo severity_level
SELECT * FROM assessments WHERE severity_level = 'severe';

-- 3. Tìm voice_analyses theo processing_status
SELECT * FROM voice_analyses WHERE processing_status = 'pending';

-- 4. Sắp xếp messages theo created_at
SELECT * FROM ai_messages ORDER BY created_at DESC;

-- 5. Tìm conversations active
SELECT * FROM ai_conversations WHERE is_active = true;
```

#### 2.3. **Thiếu constraints quan trọng**

```sql
-- ❌ Không có CHECK constraints cho:

-- 1. Email validation
users.email -- Không validate format email

-- 2. Score ranges
assessments.total_score -- Phải từ 0-21 (GAD-7)
assessments.functional_impairment -- Phải từ 0-3

-- 3. Enum values
students.gender -- Chỉ validate ở code, không ở DB
students.education_level
assessments.severity_level
voice_analyses.processing_status

-- 4. Numeric ranges
voice_analyses.sentiment_score -- Phải từ -1 đến 1
voice_analyses.emotion_confidence -- Phải từ 0 đến 1
voice_analyses.audio_duration -- Phải > 0
```

#### 2.4. **Thiếu soft delete mechanism**

```sql
-- ❌ Không có cơ chế soft delete
-- Khi xóa user → mất dữ liệu vĩnh viễn
-- Không thể khôi phục, không audit trail

-- ✅ Nên có:
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE students ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
-- ... tương tự cho các bảng quan trọng
```

### 🟡 **CẤP ĐỘ TRUNG BÌNH**

#### 2.5. **Thiếu timestamps đầy đủ**

```sql
-- Các bảng thiếu updated_at:
counselors          -- Không có updated_at
parents             -- Không có created_at, updated_at
parent_consents     -- Không có timestamps
counselor_conversations -- Không có updated_at
```

#### 2.6. **JSON columns không có validation**

```sql
-- ❌ Không validate cấu trúc JSON
assessments.answers             -- Phải là array 7 phần tử (0-3 mỗi phần tử)
assessments.recommendations     -- Phải là array of strings
voice_analyses.audio_features   -- Phải có keys: pitch_mean, energy_mean, etc.
voice_analyses.detected_emotions -- Phải có keys: anxiety, sadness, anger, neutral
```

#### 2.7. **Naming conventions không nhất quán**

```sql
-- Trộn lẫn snake_case và camelCase trong JSON
-- Một số cột dùng singular, một số dùng plural

users.phone          vs  students.phone_number
counselors.is_available  vs  users.is_active
conversations.is_active  vs  ai_conversations.is_active
```

#### 2.8. **Thiếu cascade rules rõ ràng**

```sql
-- Một số FK không có ON DELETE rules rõ ràng
parent_consents.parent_id   -- Không có ON DELETE
messages.voice_analysis_id  -- Không có ON DELETE
```

### 🟢 **CẤP ĐỘ THẤP (Tối ưu hóa)**

#### 2.9. **Không có partitioning cho bảng lớn**

```sql
-- Bảng có tiềm năng lớn nên partition:
voice_analyses      -- Partition by created_at (monthly)
ai_messages         -- Partition by created_at (monthly)
counselor_messages  -- Partition by created_at (monthly)
```

#### 2.10. **Thiếu computed/generated columns**

```sql
-- Có thể tự động tính:
assessments.severity_level  -- Tự động từ total_score
voice_analyses.has_error    -- Tự động từ error_message
```

---

## 3. ĐỀ XUẤT CẢI THIỆN

### 3.1. **Chuẩn hóa kiểu dữ liệu ID**

**Quyết định:** Dùng `BIGINT` cho TẤT CẢ primary keys và foreign keys

**Lý do:**

- ✅ Future-proof (9.2 quintillion records)
- ✅ Nhất quán toàn bộ hệ thống
- ✅ Không ảnh hưởng performance đáng kể
- ✅ Storage: chỉ tốn thêm 4 bytes/record

**Implementation:**

```sql
-- Sẽ migrate từ INTEGER → BIGINT cho:
ALTER TABLE users ALTER COLUMN id TYPE BIGINT;
ALTER TABLE students ALTER COLUMN id TYPE BIGINT;
ALTER TABLE students ALTER COLUMN user_id TYPE BIGINT;
ALTER TABLE parents ALTER COLUMN id TYPE BIGINT;
ALTER TABLE parents ALTER COLUMN user_id TYPE BIGINT;
ALTER TABLE counselors ALTER COLUMN id TYPE BIGINT;
ALTER TABLE counselors ALTER COLUMN user_id TYPE BIGINT;
ALTER TABLE assessments ALTER COLUMN id TYPE BIGINT;
ALTER TABLE assessments ALTER COLUMN student_id TYPE BIGINT;
-- ... (chi tiết trong migration script)
```

### 3.2. **Thêm indices chiến lược**

```sql
-- 📌 Query optimization indices
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_assessments_student_created ON assessments(student_id, created_at DESC);
CREATE INDEX idx_assessments_severity ON assessments(severity_level);
CREATE INDEX idx_voice_analyses_status ON voice_analyses(processing_status) WHERE processing_status != 'completed';
CREATE INDEX idx_voice_analyses_student_created ON voice_analyses(student_id, created_at DESC);
CREATE INDEX idx_ai_conversations_student_active ON ai_conversations(student_id, is_active) WHERE is_active = true;
CREATE INDEX idx_ai_messages_conversation_created ON ai_messages(conversation_id, created_at);
CREATE INDEX idx_counselor_messages_conversation_created ON counselor_messages(conversation_id, created_at);
CREATE INDEX idx_counselor_messages_unread ON counselor_messages(conversation_id, is_read) WHERE is_read = false;

-- 📌 Full-text search indices (cho tiếng Việt)
CREATE INDEX idx_users_email_gin ON users USING gin(email gin_trgm_ops);
CREATE INDEX idx_students_name_gin ON students USING gin(to_tsvector('vietnamese', (SELECT full_name FROM users WHERE id = students.user_id)));
CREATE INDEX idx_voice_analyses_transcription_fts ON voice_analyses USING gin(to_tsvector('vietnamese', transcription));
```

### 3.3. **Thêm CHECK constraints**

```sql
-- Email validation
ALTER TABLE users ADD CONSTRAINT check_email_format
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- GAD-7 score validation
ALTER TABLE assessments ADD CONSTRAINT check_total_score_range
    CHECK (total_score >= 0 AND total_score <= 21);
ALTER TABLE assessments ADD CONSTRAINT check_functional_impairment_range
    CHECK (functional_impairment IS NULL OR (functional_impairment >= 0 AND functional_impairment <= 3));

-- Severity level validation
ALTER TABLE assessments ADD CONSTRAINT check_severity_level
    CHECK (severity_level IN ('minimal', 'mild', 'moderate', 'severe'));

-- Voice analysis validations
ALTER TABLE voice_analyses ADD CONSTRAINT check_sentiment_score_range
    CHECK (sentiment_score IS NULL OR (sentiment_score >= -1 AND sentiment_score <= 1));
ALTER TABLE voice_analyses ADD CONSTRAINT check_emotion_confidence_range
    CHECK (emotion_confidence IS NULL OR (emotion_confidence >= 0 AND emotion_confidence <= 1));
ALTER TABLE voice_analyses ADD CONSTRAINT check_audio_duration_positive
    CHECK (audio_duration IS NULL OR audio_duration > 0);
ALTER TABLE voice_analyses ADD CONSTRAINT check_processing_status
    CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed'));

-- Phone number validation (simple)
ALTER TABLE users ADD CONSTRAINT check_phone_format
    CHECK (phone IS NULL OR phone ~ '^\+?[0-9]{8,15}$');
ALTER TABLE students ADD CONSTRAINT check_phone_format
    CHECK (phone_number IS NULL OR phone_number ~ '^\+?[0-9]{8,15}$');
```

### 3.4. **Thêm soft delete**

```sql
-- Add deleted_at column cho các bảng quan trọng
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE students ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE parents ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE counselors ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE assessments ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

-- Create indices for soft delete
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_students_deleted_at ON students(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_assessments_deleted_at ON assessments(deleted_at) WHERE deleted_at IS NULL;
```

### 3.5. **Bổ sung timestamps**

```sql
ALTER TABLE counselors ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE counselors ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE parents ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE parents ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE parent_consents ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE parent_consents ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE counselor_conversations ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
```

### 3.6. **JSON validation (PostgreSQL 14+)**

```sql
-- Validate GAD-7 answers structure
ALTER TABLE assessments ADD CONSTRAINT check_answers_structure
    CHECK (
        jsonb_typeof(answers::jsonb) = 'array' AND
        jsonb_array_length(answers::jsonb) = 7
    );

-- Validate voice_analyses.detected_emotions structure
ALTER TABLE voice_analyses ADD CONSTRAINT check_detected_emotions_structure
    CHECK (
        detected_emotions IS NULL OR (
            detected_emotions::jsonb ? 'anxiety' AND
            detected_emotions::jsonb ? 'sadness' AND
            detected_emotions::jsonb ? 'anger' AND
            detected_emotions::jsonb ? 'neutral'
        )
    );
```

### 3.7. **Cải thiện CASCADE rules**

```sql
-- Update FK constraints với ON DELETE rules rõ ràng
ALTER TABLE parent_consents
    DROP CONSTRAINT parent_consents_parent_id_fkey,
    ADD CONSTRAINT parent_consents_parent_id_fkey
        FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE;

ALTER TABLE messages
    DROP CONSTRAINT messages_voice_analysis_id_fkey,
    ADD CONSTRAINT messages_voice_analysis_id_fkey
        FOREIGN KEY (voice_analysis_id) REFERENCES voice_analyses(id) ON DELETE SET NULL;
```

### 3.8. **Partitioning cho bảng lớn** (Tùy chọn - Phase 2)

```sql
-- Partition voice_analyses by month
CREATE TABLE voice_analyses_partitioned (
    LIKE voice_analyses INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE voice_analyses_2025_10 PARTITION OF voice_analyses_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- ... tương tự cho các tháng khác
```

---

## 4. MỨC ĐỘ ẢNH HƯỞNG ĐÊN CODE

### 4.1. **Ảnh hưởng theo cấp độ**

| Thay đổi                | Mức độ ảnh hưởng   | Files cần sửa     | Công sức |
| ----------------------- | ------------------ | ----------------- | -------- |
| **ID integer → bigint** | 🟢 Thấp            | Models only       | 1-2 giờ  |
| **Thêm indices**        | 🟢 Không ảnh hưởng | Không             | 0 giờ    |
| **CHECK constraints**   | 🟡 Trung bình      | Validation logic  | 2-3 giờ  |
| **Soft delete**         | 🔴 Cao             | Services, queries | 4-6 giờ  |
| **Timestamps mới**      | 🟢 Thấp            | Models only       | 1 giờ    |
| **JSON validation**     | 🟡 Trung bình      | Serializers       | 2-3 giờ  |
| **Partitioning**        | 🟢 Không ảnh hưởng | Không             | 0 giờ    |

### 4.2. **Chi tiết ảnh hưởng**

#### 🟢 **THAY ĐỔI ID → BIGINT** (Ảnh hưởng thấp)

**Backend (Python/SQLAlchemy):**

```python
# ❌ Trước
class User(Base):
    id = Column(Integer, primary_key=True)

# ✅ Sau
class User(Base):
    id = Column(BigInteger, primary_key=True)
```

**Files cần sửa:**

- `ai-service/app/models/*.py` (9 files)
- Không cần sửa schemas (Pydantic tự động handle)
- Không cần sửa services
- Không cần sửa API routes

**Frontend (TypeScript):**

```typescript
// Không cần sửa gì! JavaScript/TypeScript xử lý number tự động
interface User {
  id: number; // ✅ Vẫn hoạt động bình thường
}
```

**Tổng files cần sửa:** ~9 files (chỉ models)

#### 🟢 **THÊM INDICES** (Không ảnh hưởng code)

- ✅ Chỉ là database optimization
- ✅ Code không cần thay đổi
- ✅ Queries tự động nhanh hơn

#### 🟡 **THÊM CHECK CONSTRAINTS** (Ảnh hưởng trung bình)

**Lợi ích:**

- ✅ Database tự validate
- ✅ Giảm validation code
- ⚠️ Cần handle DB errors mới

**Code changes:**

```python
# Backend: Cần catch constraint violations
from sqlalchemy.exc import IntegrityError

try:
    db.add(assessment)
    db.commit()
except IntegrityError as e:
    if 'check_total_score_range' in str(e):
        raise ValueError("Score must be between 0-21")
```

**Files cần sửa:**

- `ai-service/app/services/*.py` (~5 files)
- `ai-service/app/api/*.py` (~5 files)

**Tổng files cần sửa:** ~10 files

#### 🔴 **SOFT DELETE** (Ảnh hưởng cao)

**Thay đổi lớn:**

```python
# ❌ Trước: Hard delete
db.delete(user)
db.commit()

# ✅ Sau: Soft delete
user.deleted_at = datetime.now()
db.commit()

# ✅ Mọi query phải filter deleted_at IS NULL
query = db.query(User).filter(User.deleted_at.is_(None))
```

**Files cần sửa:**

- Models: thêm `deleted_at` column
- Services: đổi delete → soft delete
- Queries: thêm filter `deleted_at IS NULL` ở KHẮP NƠI
- API: thêm endpoint "restore"

**Tổng files cần sửa:** ~20-30 files

**⚠️ KHUYẾN NGHỊ:** Implement soft delete trong Phase 2, không phải ngay

#### 🟢 **TIMESTAMPS MỚI** (Ảnh hưởng thấp)

```python
# Chỉ cần thêm vào models
class Counselor(Base):
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

**Files cần sửa:** ~4 model files

---

## 5. KẾ HOẠCH TRIỂN KHAI

### 📅 **PHASE 1: CẢI THIỆN CƠ BẢN** (Tuần 1-2)

**Mục tiêu:** Cải thiện performance và data integrity mà không breaking changes lớn

#### **Bước 1.1: Backup và chuẩn bị** (1 ngày)

```bash
# 1. Full backup Supabase database
pg_dump -h db.xxxx.supabase.co -U postgres -d postgres > backup_before_migration.sql

# 2. Tạo migration branch
git checkout -b database-improvement-phase1

# 3. Test trên local/staging environment
# 4. Thông báo team về maintenance window
```

#### **Bước 1.2: Thêm indices** (1 ngày)

- ✅ Không breaking changes
- ✅ Chạy trong giờ thấp điểm
- ✅ Test performance trước/sau

```sql
-- File: database/migrations/001_add_indices.sql
-- Chạy CONCURRENTLY để không lock table
CREATE INDEX CONCURRENTLY idx_students_user_id ON students(user_id);
CREATE INDEX CONCURRENTLY idx_assessments_student_created ON assessments(student_id, created_at DESC);
-- ... (xem section 3.2)
```

**Checklist:**

- [ ] Chạy migration trên staging
- [ ] Verify indices được tạo: `\di+ table_name`
- [ ] Test query performance: `EXPLAIN ANALYZE`
- [ ] Chạy trên production
- [ ] Monitor performance 24h

#### **Bước 1.3: Thêm timestamps** (1 ngày)

```sql
-- File: database/migrations/002_add_timestamps.sql
ALTER TABLE counselors ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE counselors ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
-- ... (xem section 3.5)
```

**Code changes:**

- Update models: `ai-service/app/models/counselor.py`, etc.
- Alembic migration: `alembic revision -m "Add timestamps"`

**Checklist:**

- [ ] Update SQLAlchemy models
- [ ] Generate Alembic migration
- [ ] Test locally
- [ ] Deploy to staging → production

#### **Bước 1.4: Migrate ID → BIGINT** (2-3 ngày)

⚠️ **CRITICAL:** Đây là migration phức tạp nhất

**Chiến lược:**

1. Tạo columns mới (`id_new`, `user_id_new`, etc.)
2. Copy dữ liệu
3. Update FKs
4. Swap columns
5. Drop old columns

```sql
-- File: database/migrations/003_migrate_ids_to_bigint.sql
-- (Chi tiết trong section 6.1)
```

**Code changes:**

- Update ALL models: `Column(Integer) → Column(BigInteger)`
- Generate Alembic migration
- Test thoroughly!

**Checklist:**

- [ ] Write detailed migration script với rollback plan
- [ ] Test trên staging với production-like data
- [ ] Chạy trong maintenance window (2-3 giờ)
- [ ] Verify data integrity sau migration
- [ ] Update application code
- [ ] Deploy new code
- [ ] Monitor 48h

#### **Bước 1.5: Thêm CHECK constraints** (2 ngày)

⚠️ **Quan trọng:** Validate dữ liệu hiện tại trước khi thêm constraints

```sql
-- 1. Check data hiện tại có hợp lệ không
SELECT id, total_score FROM assessments
WHERE total_score < 0 OR total_score > 21;

-- 2. Fix data nếu cần
UPDATE assessments SET total_score = 21 WHERE total_score > 21;

-- 3. Thêm constraint
ALTER TABLE assessments ADD CONSTRAINT check_total_score_range
    CHECK (total_score >= 0 AND total_score <= 21);
```

**Code changes:**

- Update services để catch `IntegrityError`
- Add better error messages
- Update API error responses

**Files cần sửa:**

- `ai-service/app/services/assessment_service.py`
- `ai-service/app/services/voice_analysis_service.py`
- `ai-service/app/api/assessments.py`
- `ai-service/app/api/voice_analysis.py`

**Checklist:**

- [ ] Validate tất cả dữ liệu hiện tại
- [ ] Fix invalid data
- [ ] Add constraints từng cái một
- [ ] Test error handling trong code
- [ ] Update error messages

---

### 📅 **PHASE 2: ADVANCED FEATURES** (Tuần 3-4)

**Mục tiêu:** Thêm soft delete, JSON validation, partitioning

#### **Bước 2.1: Implement Soft Delete** (3-4 ngày)

**Database:**

```sql
-- File: database/migrations/004_add_soft_delete.sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
-- ... cho tất cả tables
```

**Backend refactor:**

```python
# 1. Update Base model
class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True)

    @classmethod
    def get_active(cls):
        return cls.query.filter(cls.deleted_at.is_(None))

# 2. Update all models
class User(Base, SoftDeleteMixin):
    ...

# 3. Update all services
class UserService:
    def delete(self, user_id):
        user = self.get(user_id)
        user.deleted_at = datetime.now()
        db.commit()

    def restore(self, user_id):
        user = User.query.get(user_id)
        user.deleted_at = None
        db.commit()

# 4. Update ALL queries
users = db.query(User).filter(User.deleted_at.is_(None)).all()
```

**Files cần sửa:** 20-30 files

**Checklist:**

- [ ] Add deleted_at columns
- [ ] Create SoftDeleteMixin
- [ ] Update all models
- [ ] Update all services (delete → soft_delete)
- [ ] Update ALL queries to filter deleted_at
- [ ] Add restore endpoints
- [ ] Add admin panel để view deleted records
- [ ] Test thoroughly
- [ ] Document breaking changes

#### **Bước 2.2: JSON Validation** (2 ngày)

```sql
-- File: database/migrations/005_add_json_validation.sql
ALTER TABLE assessments ADD CONSTRAINT check_answers_structure
    CHECK (
        jsonb_typeof(answers::jsonb) = 'array' AND
        jsonb_array_length(answers::jsonb) = 7
    );
-- ... (xem section 3.6)
```

**Code changes:**

- Update Pydantic schemas với detailed JSON structure
- Better error messages

**Checklist:**

- [ ] Validate existing JSON data
- [ ] Fix invalid JSON
- [ ] Add JSON schema constraints
- [ ] Update Pydantic models
- [ ] Test edge cases

#### **Bước 2.3: Partitioning** (2-3 ngày)

⚠️ **Chỉ cần nếu có > 1M records/table**

```sql
-- File: database/migrations/006_partition_large_tables.sql
-- (Chi tiết trong section 3.8)
```

**Checklist:**

- [ ] Analyze table sizes
- [ ] Create partition strategy (monthly/quarterly)
- [ ] Create parent table
- [ ] Migrate data to partitions
- [ ] Update queries if needed
- [ ] Setup automatic partition creation

---

### 📅 **PHASE 3: MONITORING & OPTIMIZATION** (Ongoing)

#### **Bước 3.1: Performance Monitoring**

```sql
-- Enable query logging
ALTER DATABASE postgres SET log_min_duration_statement = 1000; -- Log queries > 1s

-- Monitor slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 20;

-- Monitor index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

#### **Bước 3.2: Regular Maintenance**

```sql
-- Weekly vacuum
VACUUM ANALYZE;

-- Monthly reindex (trong low-traffic hours)
REINDEX DATABASE postgres;

-- Monitor bloat
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 6. MIGRATION SCRIPTS

### 6.1. **Script 001: Add Indices**

```sql
-- File: database/migrations/001_add_indices.sql
-- Description: Add performance indices for common queries
-- Estimated time: 5-10 minutes (depends on data size)
-- Rollback: Drop indices

BEGIN;

-- Students indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_students_user_id
    ON students(user_id);

-- Assessments indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assessments_student_created
    ON assessments(student_id, created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assessments_severity
    ON assessments(severity_level);

-- Voice analyses indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_status
    ON voice_analyses(processing_status)
    WHERE processing_status != 'completed';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_student_created
    ON voice_analyses(student_id, created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_assessment
    ON voice_analyses(assessment_id);

-- AI conversations indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_conversations_student_active
    ON ai_conversations(student_id, is_active)
    WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_conversations_last_message
    ON ai_conversations(last_message_at DESC);

-- AI messages indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_messages_conversation_created
    ON ai_messages(conversation_id, created_at);

-- Counselor conversations indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_conversations_student
    ON counselor_conversations(student_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_conversations_counselor
    ON counselor_conversations(counselor_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_conversations_last_message
    ON counselor_conversations(last_message_at DESC);

-- Counselor messages indices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_messages_conversation_created
    ON counselor_messages(conversation_id, created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_counselor_messages_unread
    ON counselor_messages(conversation_id, is_read)
    WHERE is_read = false;

-- Full-text search indices (requires pg_trgm extension)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_gin
    ON users USING gin(email gin_trgm_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_analyses_transcription_fts
    ON voice_analyses USING gin(to_tsvector('english', COALESCE(transcription, '')));

COMMIT;

-- Verify indices
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

**Rollback script:**

```sql
-- File: database/migrations/001_add_indices_rollback.sql
BEGIN;
DROP INDEX IF EXISTS idx_students_user_id;
DROP INDEX IF EXISTS idx_assessments_student_created;
DROP INDEX IF EXISTS idx_assessments_severity;
DROP INDEX IF EXISTS idx_voice_analyses_status;
DROP INDEX IF EXISTS idx_voice_analyses_student_created;
DROP INDEX IF EXISTS idx_voice_analyses_assessment;
DROP INDEX IF EXISTS idx_ai_conversations_student_active;
DROP INDEX IF EXISTS idx_ai_conversations_last_message;
DROP INDEX IF EXISTS idx_ai_messages_conversation_created;
DROP INDEX IF EXISTS idx_counselor_conversations_student;
DROP INDEX IF EXISTS idx_counselor_conversations_counselor;
DROP INDEX IF EXISTS idx_counselor_conversations_last_message;
DROP INDEX IF EXISTS idx_counselor_messages_conversation_created;
DROP INDEX IF EXISTS idx_counselor_messages_unread;
DROP INDEX IF EXISTS idx_users_email_gin;
DROP INDEX IF EXISTS idx_voice_analyses_transcription_fts;
COMMIT;
```

### 6.2. **Script 002: Add Timestamps**

```sql
-- File: database/migrations/002_add_timestamps.sql
BEGIN;

-- Add timestamps to counselors
ALTER TABLE counselors
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Add timestamps to parents
ALTER TABLE parents
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Add timestamps to parent_consents
ALTER TABLE parent_consents
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Add updated_at to counselor_conversations
ALTER TABLE counselor_conversations
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER update_counselors_updated_at
    BEFORE UPDATE ON counselors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parents_updated_at
    BEFORE UPDATE ON parents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parent_consents_updated_at
    BEFORE UPDATE ON parent_consents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_counselor_conversations_updated_at
    BEFORE UPDATE ON counselor_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
```

### 6.3. **Script 003: Migrate IDs to BIGINT**

⚠️ **CRITICAL MIGRATION - Requires downtime**

```sql
-- File: database/migrations/003_migrate_ids_to_bigint.sql
-- Description: Migrate all ID columns from INTEGER to BIGINT
-- Estimated time: 30-60 minutes (depends on data size)
-- ⚠️ REQUIRES MAINTENANCE WINDOW
-- ⚠️ BACKUP DATABASE BEFORE RUNNING

BEGIN;

-- Step 1: Users table (root of FK tree)
ALTER TABLE users ALTER COLUMN id TYPE BIGINT;

-- Step 2: Students, Parents, Counselors (1 level FK)
ALTER TABLE students ALTER COLUMN id TYPE BIGINT;
ALTER TABLE students ALTER COLUMN user_id TYPE BIGINT;
ALTER TABLE students ALTER COLUMN emergency_contact_parent_id TYPE BIGINT;

ALTER TABLE parents ALTER COLUMN id TYPE BIGINT;
ALTER TABLE parents ALTER COLUMN user_id TYPE BIGINT;

ALTER TABLE counselors ALTER COLUMN id TYPE BIGINT;
ALTER TABLE counselors ALTER COLUMN user_id TYPE BIGINT;

-- Step 3: Assessments (depends on students)
ALTER TABLE assessments ALTER COLUMN id TYPE BIGINT;
ALTER TABLE assessments ALTER COLUMN student_id TYPE BIGINT;

-- Step 4: Voice analyses (depends on students + assessments)
ALTER TABLE voice_analyses ALTER COLUMN id TYPE BIGINT;
ALTER TABLE voice_analyses ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE voice_analyses ALTER COLUMN assessment_id TYPE BIGINT;

-- Step 5: Conversations (depends on students)
ALTER TABLE conversations ALTER COLUMN id TYPE BIGINT;
ALTER TABLE conversations ALTER COLUMN student_id TYPE BIGINT;

-- Step 6: Messages (depends on conversations + voice_analyses)
ALTER TABLE messages ALTER COLUMN id TYPE BIGINT;
ALTER TABLE messages ALTER COLUMN conversation_id TYPE BIGINT;
ALTER TABLE messages ALTER COLUMN voice_analysis_id TYPE BIGINT;

-- Step 7: AI conversations (already BIGINT, just FKs)
ALTER TABLE ai_conversations ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE ai_conversations ALTER COLUMN latest_assessment_id TYPE BIGINT;

-- Step 8: AI messages (already BIGINT)
-- No changes needed

-- Step 9: Counselor conversations (already BIGINT, just FKs)
ALTER TABLE counselor_conversations ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE counselor_conversations ALTER COLUMN counselor_id TYPE BIGINT;

-- Step 10: Counselor messages (already BIGINT)
-- No changes needed

-- Step 11: Parent consents
ALTER TABLE parent_consents ALTER COLUMN id TYPE BIGINT;
ALTER TABLE parent_consents ALTER COLUMN student_id TYPE BIGINT;
ALTER TABLE parent_consents ALTER COLUMN parent_id TYPE BIGINT;

-- Step 12: Update sequences
ALTER SEQUENCE users_id_seq AS BIGINT;
ALTER SEQUENCE students_id_seq AS BIGINT;
ALTER SEQUENCE parents_id_seq AS BIGINT;
ALTER SEQUENCE counselors_id_seq AS BIGINT;
ALTER SEQUENCE assessments_id_seq AS BIGINT;
ALTER SEQUENCE voice_analyses_id_seq AS BIGINT;
ALTER SEQUENCE conversations_id_seq AS BIGINT;
ALTER SEQUENCE messages_id_seq AS BIGINT;
ALTER SEQUENCE parent_consents_id_seq AS BIGINT;

-- Verify
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND column_name LIKE '%id%'
        ORDER BY table_name, column_name
    ) LOOP
        RAISE NOTICE '%.%: %', r.table_name, r.column_name, r.data_type;
    END LOOP;
END $$;

COMMIT;
```

### 6.4. **Script 004: Add CHECK Constraints**

```sql
-- File: database/migrations/004_add_check_constraints.sql
-- Description: Add data validation constraints
-- ⚠️ Validate data before running!

BEGIN;

-- Step 1: Validate existing data
DO $$
BEGIN
    -- Check invalid emails
    IF EXISTS (SELECT 1 FROM users WHERE email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN
        RAISE EXCEPTION 'Invalid emails found. Fix before adding constraint.';
    END IF;

    -- Check invalid assessment scores
    IF EXISTS (SELECT 1 FROM assessments WHERE total_score < 0 OR total_score > 21) THEN
        RAISE EXCEPTION 'Invalid assessment scores found. Fix before adding constraint.';
    END IF;

    -- Check invalid sentiment scores
    IF EXISTS (SELECT 1 FROM voice_analyses WHERE sentiment_score IS NOT NULL AND (sentiment_score < -1 OR sentiment_score > 1)) THEN
        RAISE EXCEPTION 'Invalid sentiment scores found. Fix before adding constraint.';
    END IF;
END $$;

-- Step 2: Add constraints

-- Users constraints
ALTER TABLE users ADD CONSTRAINT check_email_format
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users ADD CONSTRAINT check_phone_format
    CHECK (phone IS NULL OR phone ~ '^\+?[0-9]{8,15}$');

-- Students constraints
ALTER TABLE students ADD CONSTRAINT check_phone_format
    CHECK (phone_number IS NULL OR phone_number ~ '^\+?[0-9]{8,15}$');

-- Assessments constraints
ALTER TABLE assessments ADD CONSTRAINT check_total_score_range
    CHECK (total_score >= 0 AND total_score <= 21);

ALTER TABLE assessments ADD CONSTRAINT check_functional_impairment_range
    CHECK (functional_impairment IS NULL OR (functional_impairment >= 0 AND functional_impairment <= 3));

ALTER TABLE assessments ADD CONSTRAINT check_severity_level
    CHECK (severity_level IN ('minimal', 'mild', 'moderate', 'severe'));

ALTER TABLE assessments ADD CONSTRAINT check_answers_structure
    CHECK (
        jsonb_typeof(answers::jsonb) = 'array' AND
        jsonb_array_length(answers::jsonb) = 7
    );

-- Voice analyses constraints
ALTER TABLE voice_analyses ADD CONSTRAINT check_sentiment_score_range
    CHECK (sentiment_score IS NULL OR (sentiment_score >= -1 AND sentiment_score <= 1));

ALTER TABLE voice_analyses ADD CONSTRAINT check_emotion_confidence_range
    CHECK (emotion_confidence IS NULL OR (emotion_confidence >= 0 AND emotion_confidence <= 1));

ALTER TABLE voice_analyses ADD CONSTRAINT check_transcription_confidence_range
    CHECK (transcription_confidence IS NULL OR (transcription_confidence >= 0 AND transcription_confidence <= 1));

ALTER TABLE voice_analyses ADD CONSTRAINT check_audio_duration_positive
    CHECK (audio_duration IS NULL OR audio_duration > 0);

ALTER TABLE voice_analyses ADD CONSTRAINT check_file_size_positive
    CHECK (file_size_bytes IS NULL OR file_size_bytes > 0);

ALTER TABLE voice_analyses ADD CONSTRAINT check_processing_status
    CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed'));

COMMIT;

-- Verify constraints
SELECT conname, contype, conrelid::regclass, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname LIKE 'check_%'
ORDER BY conrelid::regclass::text, conname;
```

### 6.5. **Script 005: Add Soft Delete** (Phase 2)

```sql
-- File: database/migrations/005_add_soft_delete.sql
-- Description: Add soft delete capability
-- Phase: 2

BEGIN;

-- Add deleted_at columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE students ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE parents ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE counselors ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE assessments ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE ai_conversations ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

-- Add indices for soft delete (partial indices for better performance)
CREATE INDEX IF NOT EXISTS idx_users_deleted_at
    ON users(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_students_deleted_at
    ON students(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_parents_deleted_at
    ON parents(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_counselors_deleted_at
    ON counselors(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_assessments_deleted_at
    ON assessments(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_voice_analyses_deleted_at
    ON voice_analyses(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ai_conversations_deleted_at
    ON ai_conversations(deleted_at) WHERE deleted_at IS NULL;

COMMIT;
```

---

## 7. TÓM TẮT VÀ KHUYẾN NGHỊ

### 7.1. **Tóm tắt vấn đề**

| Vấn đề                          | Mức độ        | Ưu tiên |
| ------------------------------- | ------------- | ------- |
| Kiểu dữ liệu ID không nhất quán | 🔴 Cao        | P0      |
| Thiếu indices                   | 🔴 Cao        | P0      |
| Thiếu CHECK constraints         | 🟡 Trung bình | P1      |
| Thiếu soft delete               | 🟡 Trung bình | P2      |
| Thiếu timestamps                | 🟢 Thấp       | P1      |
| JSON không validation           | 🟡 Trung bình | P1      |

### 7.2. **Mức độ ảnh hưởng code**

**Phase 1 (Basic improvements):**

- Backend: ~15-20 files cần sửa
- Frontend: Không cần sửa
- Downtime: 2-3 giờ (cho ID migration)
- Công sức: 1-2 tuần

**Phase 2 (Advanced features):**

- Backend: ~30-40 files cần sửa
- Frontend: Có thể cần sửa soft delete logic
- Downtime: Không cần
- Công sức: 2-3 tuần

### 7.3. **Khuyến nghị**

✅ **NÊN LÀM NGAY:**

1. Add indices (không ảnh hưởng code, cải thiện performance lớn)
2. Add timestamps (ảnh hưởng nhỏ)
3. Migrate ID → BIGINT (future-proof)

⚠️ **NÊN LÀM SAU:** 4. Add CHECK constraints (cần validate data kỹ) 5. JSON validation (cần test kỹ)

🔄 **LÀM Ở PHASE 2:** 6. Soft delete (breaking changes lớn) 7. Partitioning (chỉ khi cần)

### 7.4. **Rủi ro và Mitigation**

| Rủi ro                             | Xác suất   | Ảnh hưởng  | Mitigation                                    |
| ---------------------------------- | ---------- | ---------- | --------------------------------------------- |
| ID migration fails                 | Thấp       | Cao        | Full backup, test trên staging, rollback plan |
| Constraints fail với data hiện tại | Trung bình | Trung bình | Validate trước, fix data trước                |
| Performance regression             | Thấp       | Trung bình | Test performance, có thể rollback indices     |
| Soft delete bugs                   | Cao        | Cao        | Comprehensive testing, gradual rollout        |

### 7.5. **Timeline đề xuất**

```
Week 1:
├─ Mon-Tue: Backup, setup staging, add indices
├─ Wed-Thu: Add timestamps, test
└─ Fri: Monitor performance

Week 2:
├─ Mon-Tue: Prepare ID migration, validate data
├─ Wed: ID migration (maintenance window)
├─ Thu: Update code, deploy
└─ Fri: Monitor, fix issues

Week 3:
├─ Mon-Wed: Add CHECK constraints
├─ Thu-Fri: JSON validation
└─ Monitor

Week 4 (Phase 2):
├─ Mon-Thu: Implement soft delete
└─ Fri: Final testing, documentation
```

### 7.6. **Chi phí vs Lợi ích**

**Chi phí:**

- Development time: 2-4 tuần
- Testing time: 1 tuần
- Downtime: 2-3 giờ (chỉ ID migration)
- Risk: Trung bình (với proper testing)

**Lợi ích:**

- ✅ Performance improvement: 2-5x trên queries lớn
- ✅ Data integrity: Tránh data corruption
- ✅ Scalability: Có thể scale đến billions records
- ✅ Maintainability: Code sạch hơn, ít bugs hơn
- ✅ Future-proof: Không phải migrate lại

**Kết luận:** Đáng đầu tư! 🎯

---

## 8. NEXT STEPS

### 8.1. **Immediate Actions**

1. **Review document này với team** (1-2 ngày)

   - [ ] Tech lead review
   - [ ] Product manager review
   - [ ] Quyết định phase nào làm trước

2. **Setup staging environment** (1 ngày)

   - [ ] Clone production DB to staging
   - [ ] Setup test data
   - [ ] Configure monitoring

3. **Create backup strategy** (1 ngày)

   - [ ] Setup automated backups
   - [ ] Test restore procedure
   - [ ] Document rollback plans

4. **Start Phase 1** (2 tuần)
   - [ ] Follow kế hoạch chi tiết ở section 5

### 8.2. **Questions to Answer**

1. Có cần downtime không? Khi nào là thời gian tốt nhất?
2. Staging environment có sẵn chưa?
3. Team có experience với PostgreSQL migrations không?
4. Có monitoring/alerting setup chưa?
5. Có rollback plan rõ ràng chưa?

### 8.3. **Resources Needed**

- **People:** 1-2 backend developers, 1 DBA (nếu có)
- **Tools:**
  - pgAdmin/DBeaver for database management
  - Alembic for migrations
  - Sentry/DataDog for monitoring
- **Time:** 2-4 tuần full-time

---

## 📞 SUPPORT

Nếu có thắc mắc trong quá trình migration, liên hệ:

- Documentation: Xem file này
- Migration scripts: `database/migrations/`
- Rollback scripts: `database/migrations/*_rollback.sql`

---

**Document version:** 1.0  
**Last updated:** 2025-10-07  
**Author:** GitHub Copilot Analysis  
**Status:** Ready for Review
