# Fix Counselor Login Error - Bcrypt Hash Issue

## Vấn đề

Khi tạo user trực tiếp trên Supabase SQL Editor với password hash không đúng format:

```
ValueError: salt too small (bcrypt requires exactly 22 chars)
```

### Nguyên nhân

- Tạo user với `hashed_password = '$2b$12$...'` (chỉ có placeholder `...`)
- Bcrypt requires **exactly 60 characters** cho full hash
- Format: `$2b$12$[22 chars salt][31 chars hash]`

## Giải pháp

### Bước 1: Generate proper bcrypt hash

```bash
cd scripts
python generate_bcrypt_hash.py
```

**Output** (đã generate):

```
counselor1@ai4mind.com
Password: Counselor123!
Hash: $2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR.

counselor2@ai4mind.com
Password: Counselor123!
Hash: $2b$12$nOiTgPmKEDxbCizWJCbBn.ygPx9d1YerMfLdbhALoiIxR0QvZqKB2

counselor3@ai4mind.com
Password: Counselor123!
Hash: $2b$12$2JeDZu9Mo6BYzgIG73oyweryG/r8Y/3wWBWTw5cGPKrgQxcU05Epy
```

### Bước 2: Run SQL script trên Supabase

**File**: `database/create_counselors.sql`

**Cách chạy**:

1. Mở Supabase Dashboard
2. Project → SQL Editor
3. New Query
4. Copy toàn bộ nội dung từ `create_counselors.sql`
5. Click **Run**

**Kết quả**:

- ✅ Created 3 counselor accounts
- ✅ Email: `counselor1@ai4mind.com` | Password: `Counselor123!`
- ✅ Email: `counselor2@ai4mind.com` | Password: `Counselor123!`
- ✅ Email: `counselor3@ai4mind.com` | Password: `Counselor123!`

### Bước 3: Xóa counselor cũ (nếu có)

Nếu bạn đã tạo counselor với hash sai trước đó:

```sql
-- Xóa counselors table records
DELETE FROM counselors
WHERE user_id IN (
    SELECT id FROM users WHERE email LIKE 'counselor%@ai4mind.com'
);

-- Xóa users table records
DELETE FROM users
WHERE email LIKE 'counselor%@ai4mind.com';
```

Sau đó chạy lại script `create_counselors.sql`.

## Test Login

### Frontend Test

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to `/login`
4. Enter:
   - Email: `counselor1@ai4mind.com`
   - Password: `Counselor123!`
5. Click **Đăng nhập**
6. ✅ Should login successfully!

### Backend Test (cURL)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "counselor1@ai4mind.com",
    "password": "Counselor123!"
  }'
```

**Expected Response**:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 123,
    "email": "counselor1@ai4mind.com",
    "full_name": "TS. Nguyễn Văn A",
    "role": "counselor"
  }
}
```

## Tại sao lỗi này xảy ra?

### Bcrypt Hash Structure

```
$2b$12$SomeSalt22CharsHere$SomeHash31CharsHereForSecurePassword
│  │  │                     │
│  │  │                     └─ Hash (31 chars)
│  │  └─ Salt (22 chars base64)
│  └─ Cost factor (12 = 2^12 rounds)
└─ Algorithm version (2b)
```

**Total length**: 60 characters exactly

### Ví dụ hash hợp lệ:

```
$2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR.
└─────┘└────────────────────┘└─────────────────────────────────┘
 prefix      salt (22)              hash (31)
```

### Hash không hợp lệ:

```
$2b$12$...
└─────┘└─┘
 prefix  ❌ Only 3 chars, needs 22!
```

## Lưu ý quan trọng

### ❌ KHÔNG BAO GIỜ làm:

```sql
-- SAI - Salt quá ngắn
INSERT INTO users (email, hashed_password, ...)
VALUES ('test@example.com', '$2b$12$...', ...);
```

### ✅ LUÔN LUÔN làm:

```python
# Generate hash bằng Python trước
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("MyPassword123!")
print(hashed)  # Copy vào SQL
```

Hoặc dùng script `generate_bcrypt_hash.py`:

```bash
cd scripts
python generate_bcrypt_hash.py
```

## Files liên quan

- ✅ `scripts/generate_bcrypt_hash.py` - Generate bcrypt hashes
- ✅ `database/create_counselors.sql` - SQL script với hashes đúng
- ✅ `ai-service/app/core/security.py` - Bcrypt verification logic
- ✅ `ai-service/app/models/user.py` - User model với enum fix

## Summary

### Problem

- Created users on Supabase with invalid bcrypt hash (`$2b$12$...`)
- Bcrypt requires exactly 60 chars (salt 22 + hash 31)

### Solution

1. ✅ Generate proper hashes: `python generate_bcrypt_hash.py`
2. ✅ Run SQL: `create_counselors.sql` on Supabase
3. ✅ Test login with: `counselor1@ai4mind.com` / `Counselor123!`

### Result

- 3 counselor accounts created
- All can login successfully
- Password properly hashed with bcrypt

---

**Created**: 2025-10-05
**Status**: ✅ Resolved
