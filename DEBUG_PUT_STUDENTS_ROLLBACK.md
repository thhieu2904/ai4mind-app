# Debug: PUT /students/me ROLLBACK Issue

## 🐛 Problem

Backend creates parent account successfully but then **ROLLBACK** without clear error message.

## 🔍 Log Analysis

From your log:

```sql
-- 1. Check if parent exists
SELECT users.* FROM users
WHERE users.email = 'thhieu2904@gmail.com' AND users.role = 'PARENT'
-- Result: Not found

-- 2. Create parent user
INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified, ...)
VALUES ('thhieu2904@gmail.com', '$2b$12$...', 'Phụ huynh', 'PARENT', False, False, ...)
RETURNING users.id, users.created_at
-- Result: SUCCESS (got ID and created_at)

-- 3. Then ROLLBACK immediately
ROLLBACK
```

## 🤔 Possible Causes

### 1. **Parent.user_id Foreign Key Issue**

After creating user, backend tries to create parent profile but may fail if:

- Foreign key constraint violation
- Parent table missing columns

### 2. **Validation Error in StudentResponse**

After commit, backend calls `StudentResponse.from_orm_with_parent(student)` which may fail if:

- Missing required fields
- Type conversion errors
- Relationship not loaded properly

### 3. **Database Transaction Isolation**

The `db.flush()` gets ID but transaction may not be visible to subsequent queries.

## 🔧 Debug Steps Added

Added extensive logging to `PUT /api/v1/students/me`:

```python
# 1. Log parent email being processed
print(f"[DEBUG] Updating parent email to: {parent_email}")

# 2. Log if existing parent found
print(f"[DEBUG] Parent user found: {parent_user.id}")

# 3. Log new parent creation
print(f"[DEBUG] Creating new parent account for: {parent_email}")
print(f"[DEBUG] Created parent profile: {new_parent.id}")

# 4. Log update data
print(f"[DEBUG] Updating student with data: {update_data}")

# 5. Log successful commit
print(f"[DEBUG] Successfully committed changes")

# 6. Log errors with traceback
except Exception as e:
    print(f"[DEBUG] Error during commit/refresh: {e}")
    import traceback
    traceback.print_exc()
```

## 🧪 Testing Instructions

### 1. Restart Backend

```bash
cd ai-service
python -m uvicorn app.main:app --reload
```

### 2. Test PUT Request from Frontend

Edit profile and add parent email, or use curl:

```bash
curl -X PUT http://localhost:8000/api/v1/students/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_email": "test.parent@example.com"
  }'
```

### 3. Check Console Output

Look for debug messages:

```
[DEBUG] Updating parent email to: test.parent@example.com
[DEBUG] Creating new parent account for: test.parent@example.com
[DEBUG] Created parent profile: 123
[DEBUG] Updating student with data: {'emergency_contact_parent_id': 123}
[DEBUG] Successfully committed changes  ← Should see this
[DEBUG] Returning student response
```

If error occurs, you'll see:

```
[DEBUG] Error during commit/refresh: <error message>
<Full traceback>
```

## 🔍 Common Issues to Check

### Issue 1: Parent Profile Creation Fails

**Symptom:** No "Created parent profile: X" message

**Check:**

```sql
-- Verify parents table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'parents';
```

**Expected columns:**

- `id` (PK)
- `user_id` (FK to users.id, NOT NULL, UNIQUE)
- `phone_number` (nullable)
- `address` (nullable)
- `occupation` (nullable)

### Issue 2: Student Update Fails

**Symptom:** Error at "Updating student with data"

**Check:**

```python
# Verify update_data doesn't have invalid fields
print(update_data)  # Should only have valid Student model fields
```

### Issue 3: Response Serialization Fails

**Symptom:** Error at "Returning student response"

**Check:**

- `student.user` relationship loaded? → Need `joinedload(Student.user)`
- `student.emergency_contact_parent` loaded? → Need `joinedload`
- `created_at` field accessible? → Check if `student.user.created_at` exists

## 🎯 Expected Behavior

After fix, successful request should:

1. ✅ Create parent user account
2. ✅ Create parent profile
3. ✅ Update student.emergency_contact_parent_id
4. ✅ Commit transaction
5. ✅ Return complete StudentResponse with:
   - `parent_email`: parent's email
   - `email`: student's email
   - `full_name`: student's name
   - `created_at`: student creation date

## 📋 Next Steps

1. **Restart backend** with debug logging
2. **Reproduce the error** by editing profile with parent email
3. **Check console output** for debug messages
4. **Share the debug log** if error persists

The debug logging will reveal exactly where the failure occurs!
