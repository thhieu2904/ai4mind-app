# 🔐 AI4Mind Login Credentials & Access Guide

**Last Updated:** January 2025  
**Status:** Active Test Accounts

---

## 👨‍💼 Admin Accounts

### Admin User

```
Email:    admin@example.com
Password: [Check scripts/seed-data.py or database admin]
Role:     ADMIN
Name:     Admin User
```

**Permissions:**

- Full system access
- User management (CRUD)
- View all assessments
- System configuration

**Access:**

- Frontend: Login at `http://localhost:5173/login`
- Admin panel: `http://localhost:5173/admin` (if implemented)
- API: Direct access to all endpoints

---

## 👨‍⚕️ Counselor Accounts (5 Active)

### Counselor 1 (Primary)

```
Email:    counselor1@ai4mind.com
Password: [Check scripts/seed-data.py]
Role:     COUNSELOR
Name:     TS. Nguyễn Văn A
License:  [Check database]
```

### Counselor 2 (Primary)

```
Email:    counselor1@example.com
Password: [Check scripts/seed-data.py]
Role:     COUNSELOR
Name:     Dr. Phạm Văn Tâm
License:  [Check database]
```

### Counselor 3 (Primary)

```
Email:    counselor2@ai4mind.com
Password: [Check scripts/seed-data.py]
Role:     COUNSELOR
Name:     ThS. Trần Thị B
License:  [Check database]
```

### Counselor 4 (Primary)

```
Email:    counselor3@ai4mind.com
Password: [Check scripts/seed-data.py]
Role:     COUNSELOR
Name:     ThS. Lê Văn C
License:  [Check database]
```

### Counselor 5 (Test Account)

```
Email:    test.counselor.1759315279.733213@example.com
Password: [Check scripts/seed-data.py]
Role:     COUNSELOR
Name:     Test Counselor
License:  [Check database]
```

**Counselor Permissions:**

- View all student assessments
- Chat with assigned students
- View student profiles
- Generate reports
- Cannot delete users or assessments

**Access:**

- Frontend: Login at `http://localhost:5173/login`
- Dashboard: View assigned students
- Chat: Access counselor chat interface

---

## 👨‍🎓 Student Test Accounts

### Test Student 1 (Primary Test Account)

```
Email:       thhieu2904das@gmail.com
Password:    [Original registration password]
Role:        STUDENT
Assessments: 3 active assessments
```

**Used for:**

- Security testing (verified fix - sees only own 3 assessments)
- Authorization testing
- Assessment list filtering

**Data:**

- Assessment IDs: 32, 33, 34
- Scores: 11, 12, 8
- Severity: moderate, moderate, mild

### Additional Students

```
Total Students: 52 accounts
Query to list: SELECT email, full_name FROM users WHERE role = 'STUDENT' LIMIT 10;
```

**Student Permissions:**

- View only own assessments
- Take new assessments (GAD-7, PHQ-9)
- Chat with assigned counselor
- View own profile
- Export own assessment history

---

## 👪 Parent Test Accounts

```
Total Parents: 3 accounts
Query: SELECT email, full_name FROM users WHERE role = 'PARENT';
```

**Parent Permissions:**

- View linked student's assessments
- Receive notifications about student
- Cannot take assessments
- Cannot chat with counselor (depends on feature implementation)

---

## 🔑 Password Management

### Reset Password via Database

```sql
-- Reset password to 'Password123!'
-- First, generate bcrypt hash (use online tool or Python):
-- python -c "from bcrypt import hashpw, gensalt; print(hashpw(b'Password123!', gensalt()).decode())"

UPDATE users
SET hashed_password = '$2b$12$YOUR_GENERATED_HASH_HERE'
WHERE email = 'admin@example.com';
```

### Get Current Password from Seed Script

```bash
# Check seed data script for default passwords
cat scripts/seed-data.py | grep -A5 "password"

# Or check initialization script
cat scripts/init-db.py | grep -A5 "password"
```

### Supabase Dashboard Access

```
URL: https://supabase.com/dashboard
Project: ai4mind (or your project name)
Auth: Check Authentication > Users > Find email
```

---

## 🗄️ Database Queries for User Management

### List All Users by Role

```sql
-- Summary
SELECT role, COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

-- Detailed list
SELECT
    id,
    email,
    full_name,
    role,
    created_at,
    last_login
FROM users
WHERE role = 'COUNSELOR'  -- or STUDENT, PARENT, ADMIN
ORDER BY created_at DESC;
```

### Find User by Email

```sql
SELECT
    id,
    email,
    full_name,
    role,
    education_level,
    university,
    major_field,
    created_at
FROM users
WHERE email = 'counselor1@ai4mind.com';
```

### Check User Assessments

```sql
-- Get student's assessments
SELECT
    a.id,
    a.score,
    a.severity_level,
    a.functional_impairment,
    a.created_at,
    u.email as student_email,
    u.full_name as student_name
FROM assessments a
JOIN users u ON a.student_id = u.id
WHERE u.email = 'thhieu2904das@gmail.com'
ORDER BY a.created_at DESC;
```

### Verify Role Data Integrity

```sql
-- Check for lowercase roles (should return 0)
SELECT * FROM users WHERE role::text ~ '^[a-z]';

-- Check role enum values
SELECT DISTINCT role FROM users ORDER BY role;
-- Expected: ADMIN, COUNSELOR, PARENT, STUDENT
```

---

## 🧪 Testing Credentials

### API Testing with cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "thhieu2904das@gmail.com", "password": "YOUR_PASSWORD"}'

# Save token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get assessments (should return only student's own)
curl http://localhost:8000/api/v1/assessments/ \
  -H "Authorization: Bearer $TOKEN"
```

### Python Testing Script

```python
import requests

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "counselor1@ai4mind.com",
    "password": "YOUR_PASSWORD"
})
token = response.json()["access_token"]

# Get assessments
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/assessments/", headers=headers)
print(f"Assessments: {len(response.json()['items'])}")
```

---

## 🚨 Security Notes

### ⚠️ IMPORTANT WARNINGS

1. **Development Credentials Only**

   - These credentials are for development/testing ONLY
   - DO NOT use in production
   - Change all passwords before deployment

2. **Password Security**

   - Default passwords should be in `scripts/seed-data.py`
   - Never commit real passwords to git
   - Use environment variables for production

3. **Token Management**

   - Access tokens expire after 24 hours (1440 minutes)
   - No refresh token currently implemented
   - Users must re-login after expiry

4. **Database Access**
   - Only grant database access to authorized personnel
   - Use read-only credentials for reports
   - Enable audit logging for sensitive tables

---

## 📱 Login Flow

### Student/Parent/Counselor Login

1. Navigate to `http://localhost:5173/login`
2. Enter email and password
3. Click "Đăng nhập" (Login)
4. Redirected to role-specific dashboard:
   - Student → `/dashboard` (own assessments)
   - Counselor → `/counselor/dashboard` (all students)
   - Parent → `/parent/dashboard` (linked student)

### Admin Login

1. Same login page as above
2. After login, access admin features:
   - User management: `/admin/users`
   - System stats: `/admin/stats`
   - Database tools: `/admin/tools`

**Note:** Admin UI may not be fully implemented - check `frontend/src/pages/` for available routes

---

## 🔍 Troubleshooting Login Issues

### Issue: "Invalid credentials"

**Solutions:**

1. Check password is correct (see seed script)
2. Verify email is in database:
   ```sql
   SELECT email, role FROM users WHERE email = 'your@email.com';
   ```
3. Ensure role is UPPERCASE in database (after security fix)

### Issue: "User not found"

**Solutions:**

1. Run seed script: `python scripts/seed-data.py`
2. Create user manually via SQL:
   ```sql
   INSERT INTO users (email, hashed_password, full_name, role)
   VALUES ('test@example.com', '$2b$12$...', 'Test User', 'STUDENT');
   ```

### Issue: "Token expired"

**Solutions:**

1. Re-login to get new token
2. Token valid for 24 hours by default
3. Check `ACCESS_TOKEN_EXPIRE_MINUTES` in env file

### Issue: "Unauthorized" after login

**Solutions:**

1. Check token is being sent in `Authorization: Bearer <token>` header
2. Verify CORS settings in backend allow frontend origin
3. Check browser console for errors
4. Verify role comparison uses enum (after security fix)

---

## 📊 Current User Statistics

**Last Database Check:**

- **Total Users:** 61
  - Students: 52
  - Counselors: 5
  - Parents: 3
  - Admins: 1

**Verification Query:**

```sql
SELECT
    role,
    COUNT(*) as total,
    COUNT(last_login) as logged_in_at_least_once
FROM users
GROUP BY role;
```

---

## 🔐 Secure Credential Storage

### For Production Deployment

1. **Environment Variables**

   ```env
   # .env (DO NOT COMMIT)
   ADMIN_EMAIL=admin@yourdomain.com
   ADMIN_PASSWORD=secure_random_password_here
   ```

2. **Secret Management Service**

   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Supabase Vault

3. **Password Policies**
   - Minimum 8 characters
   - Require uppercase, lowercase, number, special char
   - Force password change on first login
   - Implement password expiry (90 days)

---

## 📞 Support

**For Password Resets:**

- Development: Check `scripts/seed-data.py`
- Database access: Use SQL UPDATE with bcrypt hash
- Supabase: Use dashboard reset function

**For New Accounts:**

- Students: Register via frontend `/register`
- Counselors: Contact admin (requires license verification)
- Admin: Manual SQL INSERT (limited to 1-2 accounts)

**For Role Changes:**

```sql
-- Promote user to counselor
UPDATE users
SET role = 'COUNSELOR',
    counselor_license_number = 'LICENSE123'
WHERE email = 'user@example.com';
```

---

**Document Maintained By:** Development Team  
**Last Verified:** January 2025 (after security fix)  
**Related Documents:**

- `docs/PROJECT_ISSUES_REPORT.md` - Full project status
- `docs/SECURITY_FIX_SUMMARY.md` - Security fix details
- `scripts/seed-data.py` - User initialization script

---

## ⚠️ FINAL WARNING

**These are TEST credentials for DEVELOPMENT ONLY.**

Before deploying to production:

1. ✅ Change ALL passwords
2. ✅ Remove test accounts
3. ✅ Enable password complexity requirements
4. ✅ Implement account lockout after failed attempts
5. ✅ Enable audit logging for authentication
6. ✅ Set up monitoring/alerting for suspicious logins
7. ✅ Review and update CORS settings
8. ✅ Enable rate limiting on login endpoint
9. ✅ Implement CAPTCHA for registration
10. ✅ Use HTTPS only (no HTTP in production)

**Security is not a feature - it's a requirement.**
