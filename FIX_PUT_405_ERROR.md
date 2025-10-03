# ✅ FIX: PUT /api/v1/auth/me 405 Method Not Allowed

## 🔴 Vấn Đề

Frontend gọi `PUT /api/v1/auth/me` nhưng endpoint này **KHÔNG TỒN TẠI** → 405 Method Not Allowed

## ✅ Giải Pháp

Chỉ cần **1 endpoint duy nhất**: `PUT /api/v1/students/me` để update tất cả (user info + student profile + parent email)

---

## 🔧 Các Thay Đổi

### 1. **Backend Schema** (`ai-service/app/schemas/student.py`)

**Thêm `full_name` và `parent_email` vào `StudentUpdate`:**

```python
class StudentUpdate(BaseModel):
    """Schema for updating student profile - all fields optional"""
    # User basic info
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)

    # Student info
    student_code: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    gender: Optional[GenderEnum] = None
    university: Optional[str] = Field(None, max_length=255)
    major: Optional[str] = Field(None, max_length=255)
    year_of_study: Optional[int] = Field(None, ge=1, le=6)

    # Emergency contact
    emergency_contact_parent_id: Optional[int] = None
    parent_email: Optional[str] = None  # ← NEW: Accept in body
```

### 2. **Backend Endpoint** (`ai-service/app/api/v1/endpoints/students.py`)

**Signature thay đổi:**

```python
# OLD (nhận parent_email qua query parameter)
def update_current_student_profile(
    student_data: StudentUpdate,
    parent_email: Optional[EmailStr] = None,  # Query param
    ...
):

# NEW (nhận parent_email qua body)
def update_current_student_profile(
    student_data: StudentUpdate,  # parent_email trong body
    ...
):
```

**Logic xử lý:**

```python
# Exclude parent_email và full_name khỏi student fields
update_data = student_data.model_dump(
    exclude_unset=True,
    exclude={'parent_email', 'full_name'}
)

# Update full_name trong users table
if student_data.full_name:
    current_student.user.full_name = student_data.full_name

# Handle parent_email (tạo parent nếu chưa có)
if student_data.parent_email:
    parent_email = student_data.parent_email
    # ... logic tạo/link parent
    update_data['emergency_contact_parent_id'] = parent.id

# Update student record
for field, value in update_data.items():
    setattr(current_student, field, value)
```

### 3. **Frontend Service** (`frontend/src/services/userService.ts`)

**Đánh dấu `updateUser` deprecated:**

```typescript
/**
 * @deprecated Use updateStudentProfile instead
 */
static async updateUser(data: { full_name?: string; phone?: string }) {
    throw new Error("Use updateStudentProfile instead");
}

/**
 * Update student profile (includes user basic info)
 */
static async updateStudentProfile(
    data: Partial<StudentProfile> & { full_name?: string }
): Promise<StudentDetails> {
    const response = await api.put("/api/v1/students/me", data);
    return response.data;
}
```

### 4. **Frontend ProfilePage** (`frontend/src/pages/ProfilePage/ProfilePage.tsx`)

**Chỉ gọi 1 API duy nhất:**

```typescript
const handleSaveProfile = async (data: any) => {
  // Single API call với tất cả data
  const studentData = {
    full_name: data.full_name, // ← User basic info
    phone_number: data.phone,
    date_of_birth: data.date_of_birth,
    gender: data.gender,
    address: data.address,
    university: data.university,
    major: data.major,
    year_of_study: data.year_of_study
      ? parseInt(data.year_of_study)
      : undefined,
    parent_email: data.parent_email, // ← Emergency contact
  };

  const updatedProfile = await UserService.updateStudentProfile(studentData);
  setStudentProfile(updatedProfile);

  // Update user state
  setUser((prev) =>
    prev
      ? {
          ...prev,
          full_name: data.full_name || prev.full_name,
          phone: data.phone || prev.phone,
        }
      : null
  );
};
```

---

## ✅ Testing

### Test 1: Update Full Name + Phone

```bash
PUT /api/v1/students/me
{
    "full_name": "Nguyễn Văn A",
    "phone_number": "0912345678"
}
```

**Expected:**

- ✅ `users.full_name` updated
- ✅ `students.phone_number` updated
- ✅ Response includes updated data

### Test 2: Update Profile + Parent Email

```bash
PUT /api/v1/students/me
{
    "full_name": "Nguyễn Văn B",
    "university": "HCMUT",
    "major": "Computer Science",
    "parent_email": "parent@example.com"
}
```

**Expected:**

- ✅ User info updated
- ✅ Student profile updated
- ✅ Parent account created/linked
- ✅ Response includes `parent_email`

### Test 3: Update Only Parent Email

```bash
PUT /api/v1/students/me
{
    "parent_email": "newparent@example.com"
}
```

**Expected:**

- ✅ Old parent unlinked
- ✅ New parent created/linked
- ✅ Other fields unchanged

---

## 📊 Architecture Summary

### OLD (❌ Broken):

```
Frontend → PUT /api/v1/auth/me (update user)
        → PUT /api/v1/students/me (update student)

Problem: /api/v1/auth/me doesn't exist!
```

### NEW (✅ Working):

```
Frontend → PUT /api/v1/students/me (update everything)
           ├─ Update users.full_name
           ├─ Update students.*
           └─ Handle parent_email (create/link parent)
```

---

## 🎯 Ưu Điểm

1. ✅ **Đơn giản hơn:** Chỉ 1 API call thay vì 2
2. ✅ **Atomic:** Tất cả updates trong 1 transaction
3. ✅ **Consistent:** User info + Student info luôn sync
4. ✅ **Flexible:** Accept parent_email trong body cùng với các fields khác

---

## 📝 Files Modified

### Backend (2 files):

1. ✅ `ai-service/app/schemas/student.py` - StudentUpdate schema
2. ✅ `ai-service/app/api/v1/endpoints/students.py` - PUT /me endpoint

### Frontend (2 files):

1. ✅ `frontend/src/services/userService.ts` - Deprecated updateUser
2. ✅ `frontend/src/pages/ProfilePage/ProfilePage.tsx` - Single API call

---

## 🚀 Next Steps

1. **Restart Backend:**

   ```bash
   cd ai-service
   python -m uvicorn app.main:app --reload
   ```

2. **Test trong Browser:**

   - Mở Profile Page
   - Click "Chỉnh sửa"
   - Update thông tin
   - Click "Lưu"
   - Verify không còn lỗi 405

3. **Check Network Tab:**
   ```
   Request: PUT /api/v1/students/me
   Payload: { full_name, phone_number, parent_email, ... }
   Response: 200 OK with updated data
   ```

---

**Status:** ✅ Fixed - Ready to Test  
**Date:** October 3, 2025
