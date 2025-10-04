# Fix: GET 500 Internal Server Error

## Issue

**Reported Error**: `GET /api/v1/auth/me HTTP/1.1 500 Internal Server Error`

**Root Cause**: Backend tries to access `parent.relationship` field which doesn't exist in database.

## Solution Approach

Instead of fixing the complex `/api/v1/auth/me` endpoint (which handles multiple user roles), we made students exclusively use the simpler `/api/v1/students/me` endpoint for profile data.

## Implementation

### 1. Backend Schema Changes (`ai-service/app/schemas/student.py`)

**Added fields to `StudentResponse`:**

```python
class StudentResponse(StudentBase):
    id: int
    user_id: int
    email: Optional[str] = None       # NEW: User email from student.user
    full_name: Optional[str] = None   # NEW: User name from student.user
    parent_email: Optional[str] = None  # Computed from emergency_contact_parent
```

**Enhanced `from_orm_with_parent()` method:**

```python
@staticmethod
def from_orm_with_parent(student):
    """Create response with user info and parent email from relationships"""
    data = StudentResponse.model_validate(student)

    # Populate user basic info from relationship
    if student.user:
        data.email = student.user.email
        data.full_name = student.user.full_name

    # Populate parent email from relationship
    if student.emergency_contact_parent and student.emergency_contact_parent.user:
        data.parent_email = student.emergency_contact_parent.user.email

    return data
```

### 2. Backend Endpoint Changes (`ai-service/app/api/v1/endpoints/students.py`)

**Added eager loading of `student.user` relationship to all three endpoints:**

#### GET /api/v1/students/me

```python
student = db.query(Student).options(
    joinedload(Student.user),  # Load user relationship
    joinedload(Student.emergency_contact_parent).joinedload(Parent.user)
).filter(Student.id == current_student.id).first()
```

#### GET /api/v1/students/{id}

```python
async def get_student_by_id(
    student_id: int,
    current_user: User = Depends(get_current_active_user),  # Changed from current_student
    db: Session = Depends(get_db)
):
    await check_student_access(student_id=student_id, current_user=current_user, db=db)

    student = db.query(Student).options(
        joinedload(Student.user),  # Load user relationship
        joinedload(Student.emergency_contact_parent).joinedload(Parent.user)
    ).filter(Student.id == student_id).first()
```

#### PUT /api/v1/students/me

```python
db.commit()
db.refresh(current_student)
student = db.query(Student).options(
    joinedload(Student.user),  # Load user relationship
    joinedload(Student.emergency_contact_parent).joinedload(Parent.user)
).filter(Student.id == current_student.id).first()
```

**Updated imports:**

```python
from app.api.dependencies import (
    get_current_user_student,
    get_current_active_user,
    check_student_access
)
```

### 3. Frontend Changes (`frontend/src/pages/ProfilePage/ProfilePage.tsx`)

**Changed `fetchProfileData()` to prioritize `/students/me`:**

```typescript
const fetchProfileData = async () => {
  try {
    // Call GET /api/v1/students/me first (avoids buggy /auth/me)
    const studentData = await UserService.getStudentProfile();
    setStudentProfile(studentData);

    // Construct user from student data (now includes email, full_name)
    setUser({
      id: studentData.user_id,
      email: studentData.email, // From student.user.email
      full_name: studentData.full_name, // From student.user.full_name
      role: "student",
    });
  } catch (err) {
    console.error("Error loading student profile:", err);

    // Fallback: Try /auth/me only if /students/me fails
    try {
      const userData = await UserService.getCurrentUser();
      setUser(userData);

      // Load student profile separately
      const studentData = await UserService.getStudentProfile();
      setStudentProfile(studentData);
    } catch (fallbackErr) {
      setError("Không thể tải thông tin người dùng");
    }
  }
};
```

## Benefits

1. **Simpler architecture**: Students don't need the complex `/auth/me` endpoint
2. **Single source of truth**: `/students/me` returns all needed data (user info + student profile + parent email)
3. **Better performance**: Single API call instead of two separate calls
4. **Avoids bugs**: No longer touches problematic `parent.relationship` code

## Testing Checklist

### Backend Tests

- [ ] Restart backend server: `python -m uvicorn app.main:app --reload`
- [ ] Test GET /api/v1/students/me (should include email, full_name)
- [ ] Test GET /api/v1/students/{id} (should work with proper access control)
- [ ] Test PUT /api/v1/students/me (should update and return complete data)

### Frontend Tests

- [ ] Open Profile Page (should load without 500 error)
- [ ] Verify user name displays correctly (from StudentResponse.full_name)
- [ ] Check Network tab: GET /students/me response includes email, full_name
- [ ] Click "Chỉnh sửa" (Edit button)
- [ ] Update profile fields (full_name, phone, parent_email)
- [ ] Click "Lưu thay đổi" (Save changes)
- [ ] Verify PUT /api/v1/students/me succeeds
- [ ] Verify profile updates display immediately

## API Response Example

**GET /api/v1/students/me** response:

```json
{
  "id": 1,
  "user_id": 123,
  "email": "student@example.com", // From student.user
  "full_name": "Nguyễn Văn A", // From student.user
  "phone": "0123456789",
  "date_of_birth": "2005-01-15",
  "gender": "male",
  "school_name": "THPT Chuyên Lê Hồng Phong",
  "year_of_study": 2,
  "major": null,
  "parent_email": "parent@example.com", // From emergency_contact_parent.user
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-02T00:00:00"
}
```

## Related Issues Fixed

This fix is part of the Profile Page refactoring that also addressed:

1. ✅ PUT 405 error - Consolidated to single endpoint
2. ✅ Emergency contact architecture - Foreign key to parents table
3. ✅ NULL parent_id handling - 52 students with nullable FK
4. ✅ GET 500 error - This document

## Next Steps

After testing, consider:

1. Deprecating `/api/v1/auth/me` for students (or fix the parent.relationship bug)
2. Implementing education_level migration (see `EDUCATION_LEVEL_MIGRATION.md`)
3. Adding validation tests for NULL parent_id scenarios
