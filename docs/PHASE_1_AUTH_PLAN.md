# Phase 1: Authentication System - Detailed Plan

## 🎯 MỤC TIÊU

Xây dựng hệ thống authentication hoàn chỉnh với JWT tokens, role-based access control, và user registration/login.

---

## 📋 TASK BREAKDOWN

### ✅ Task 1.1: Setup Dependencies (5 phút)

**Status:** ✅ COMPLETED

- [x] FastAPI installed
- [x] SQLAlchemy installed
- [x] python-jose installed (JWT)
- [x] passlib installed (password hashing)
- [x] bcrypt installed

---

### 🔄 Task 1.2: Create Pydantic Schemas (15 phút)

**File:** `ai-service/app/schemas/auth.py`

**Schemas cần tạo:**

```python
- UserBase (email, full_name)
- UserCreate (extends UserBase + password, role)
- UserLogin (email, password)
- UserResponse (user info without password)
- Token (access_token, token_type)
- TokenData (email, role)
```

**Tại sao cần schemas?**

- Validate input data (email format, password strength)
- Type safety với TypeScript-like experience
- Auto-generate API documentation
- Separate DB models from API models

---

### 🔄 Task 1.3: Enhance Security Module (20 phút)

**File:** `ai-service/app/core/security.py` (already exists, enhance it)

**Functions cần thêm:**

```python
- get_current_user(token: str) -> User
  → Decode JWT token → return User object

- get_current_active_user(user: User) -> User
  → Check if user.is_active == True

- require_role(allowed_roles: List[str])
  → Decorator to check user role
```

**Security checklist:**

- ✅ Password hashing với bcrypt
- ✅ JWT token generation
- 🔲 Token expiration (30 min)
- 🔲 Token refresh mechanism
- 🔲 Role-based access control

---

### 🔄 Task 1.4: Create Auth Endpoints (45 phút)

**File:** `ai-service/app/api/v1/endpoints/auth.py`

#### Endpoint 1: POST /api/v1/auth/register

```python
Input:
{
  "email": "student@example.com",
  "password": "SecurePass123!",
  "full_name": "Nguyen Van A",
  "role": "student"
}

Process:
1. Validate email format
2. Check email not exists
3. Validate password (min 8 chars, has uppercase, number)
4. Hash password
5. Create User record
6. If role=student: create Student profile
7. If role=parent: create Parent profile
8. Generate JWT token
9. Return token + user info

Output:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "full_name": "Nguyen Van A",
    "role": "student"
  }
}
```

#### Endpoint 2: POST /api/v1/auth/login

```python
Input:
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}

Process:
1. Find user by email
2. If not found → 401 Unauthorized
3. Verify password with bcrypt
4. If incorrect → 401 Unauthorized
5. Update last_login timestamp
6. Generate JWT token
7. Return token + user info

Output: Same as register
```

#### Endpoint 3: GET /api/v1/auth/me

```python
Headers:
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Process:
1. Extract token from header
2. Decode & validate token
3. Get user from database
4. Return user info

Output:
{
  "id": 1,
  "email": "student@example.com",
  "full_name": "Nguyen Van A",
  "role": "student",
  "is_active": true,
  "created_at": "2025-01-01T10:00:00Z"
}
```

#### Endpoint 4: POST /api/v1/auth/refresh

```python
Input:
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Process:
1. Validate refresh token
2. Generate new access token
3. Return new token

Output:
{
  "access_token": "new_token...",
  "token_type": "bearer"
}
```

---

### 🔄 Task 1.5: Update Main App (10 phút)

**File:** `ai-service/app/main.py`

**Changes:**

```python
- Import auth router
- Include auth router: app.include_router(auth.router)
- Add CORS middleware (already done)
- Add exception handlers for 401, 403
```

---

### 🔄 Task 1.6: Testing (30 phút)

**Manual Testing với Thunder Client/Postman:**

**Test Case 1: Register New Student**

```bash
POST http://localhost:8000/api/v1/auth/register
{
  "email": "test.student@example.com",
  "password": "Student123!",
  "full_name": "Test Student",
  "role": "student"
}

Expected: 201 Created + JWT token
```

**Test Case 2: Login**

```bash
POST http://localhost:8000/api/v1/auth/login
{
  "email": "test.student@example.com",
  "password": "Student123!"
}

Expected: 200 OK + JWT token
```

**Test Case 3: Get Current User**

```bash
GET http://localhost:8000/api/v1/auth/me
Headers: Authorization: Bearer {token}

Expected: 200 OK + user info
```

**Test Case 4: Invalid Token**

```bash
GET http://localhost:8000/api/v1/auth/me
Headers: Authorization: Bearer invalid_token

Expected: 401 Unauthorized
```

**Test Case 5: Duplicate Email**

```bash
POST http://localhost:8000/api/v1/auth/register
{same email as test 1}

Expected: 400 Bad Request "Email already exists"
```

---

### 🔄 Task 1.7: Write Unit Tests (Optional - 30 phút)

**File:** `ai-service/tests/test_auth.py`

```python
def test_register_new_user():
    # Test successful registration

def test_register_duplicate_email():
    # Test error when email exists

def test_login_success():
    # Test successful login

def test_login_wrong_password():
    # Test error with wrong password

def test_get_current_user():
    # Test get user with valid token

def test_invalid_token():
    # Test error with invalid token
```

---

## 📊 ESTIMATED TIME

| Task                 | Time          | Priority |
| -------------------- | ------------- | -------- |
| 1.2 Create Schemas   | 15 min        | HIGH     |
| 1.3 Enhance Security | 20 min        | HIGH     |
| 1.4 Auth Endpoints   | 45 min        | HIGH     |
| 1.5 Update Main      | 10 min        | HIGH     |
| 1.6 Manual Testing   | 30 min        | HIGH     |
| 1.7 Unit Tests       | 30 min        | MEDIUM   |
| **TOTAL**            | **2.5 hours** |          |

**MVP Time (without unit tests): 2 hours**

---

## 🔐 SECURITY CHECKLIST

### Password Security

- [x] Hash passwords with bcrypt (cost factor 12)
- [ ] Validate password strength (min 8 chars)
- [ ] Require uppercase + lowercase + number
- [ ] Prevent common passwords

### Token Security

- [ ] Use strong JWT secret (32+ characters)
- [ ] Set token expiration (30 minutes)
- [ ] Use refresh tokens (7 days)
- [ ] Validate token signature
- [ ] Check token expiration

### API Security

- [ ] Rate limiting (prevent brute force)
- [ ] CORS properly configured
- [ ] HTTPS only in production
- [ ] Input validation
- [ ] SQL injection prevention (SQLAlchemy handles this)

### User Security

- [ ] Email verification (optional for MVP)
- [ ] Account lockout after failed attempts
- [ ] Password reset flow (optional for MVP)
- [ ] Audit logging (who logged in when)

---

## 🎯 SUCCESS CRITERIA

**You know Task 1 is complete when:**

✅ Can register new student account
✅ Can register new parent account
✅ Can login with email/password
✅ Receive JWT token on successful login
✅ Can access protected endpoint with token
✅ Get 401 error with invalid token
✅ Get 400 error with duplicate email
✅ Password is hashed in database (not plain text)
✅ Last_login timestamp updates on login
✅ Token expires after 30 minutes

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: "JWT decode error"

```python
# Solution: Check JWT_SECRET_KEY in .env
# Make sure it's at least 32 characters
JWT_SECRET_KEY=your_super_secret_jwt_key_at_least_32_characters_long
```

### Issue 2: "bcrypt password verification fails"

```python
# Solution: Make sure to use bcrypt.checkpw() not ==
# See app/core/security.py verify_password()
```

### Issue 3: "CORS error from frontend"

```python
# Solution: Add frontend URL to CORS_ORIGINS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

### Issue 4: "Token expired"

```python
# Solution: Implement refresh token mechanism
# Or increase ACCESS_TOKEN_EXPIRE_MINUTES for development
```

---

## 📝 FILES TO CREATE/MODIFY

```
ai-service/
├── app/
│   ├── schemas/
│   │   ├── __init__.py          [CREATE]
│   │   └── auth.py              [CREATE] ← Start here!
│   ├── api/v1/endpoints/
│   │   └── auth.py              [CREATE]
│   ├── core/
│   │   └── security.py          [MODIFY] ← Add get_current_user
│   ├── main.py                  [MODIFY] ← Include auth router
│   └── models/                  [DONE] ✅
└── tests/
    └── test_auth.py             [CREATE] (optional)
```

---

## 🎓 WHAT YOU'LL LEARN

1. **JWT Authentication** - Industry standard for stateless auth
2. **Password Hashing** - Never store plain text passwords
3. **Pydantic Validation** - Type-safe request/response
4. **Dependency Injection** - FastAPI's powerful feature
5. **OAuth2 Password Flow** - Standard auth flow
6. **Role-Based Access Control** - Permission management

---

## 🚀 LET'S START!

**Next immediate action:**

1. Create `app/schemas/auth.py` with Pydantic models
2. Test that schemas work
3. Then move to auth endpoints

**Ready to code? I'll help you implement step by step! 💪**
