# Fix: Improved Validation & Error Handling

## 🎯 Vấn đề

User gặp lỗi khi cập nhật Profile Page với parent email:

- **Duplicate email error**: Dùng email đã tồn tại (role student) → 500 Internal Server Error
- **Error message khó hiểu**: Backend trả về lỗi database thô, không thân thiện
- **Không có validation frontend**: User phải submit rồi mới biết lỗi
- **Không có warning modal**: Lỗi hiển thị không rõ ràng

## ✅ Giải pháp đã implement

### 1. **Backend Validation Improvements** (`ai-service/app/api/v1/endpoints/students.py`)

#### Validation logic mới:

```python
# 1. Normalize và validate email format
parent_email = student_data.parent_email.strip().lower()
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
if not re.match(email_pattern, parent_email):
    raise HTTPException(400, "Email phụ huynh không hợp lệ")

# 2. Prevent self-reference
if parent_email == current_student.user.email.lower():
    raise HTTPException(400, "Không thể sử dụng email của chính bạn làm email phụ huynh")

# 3. Check duplicate email with different role
existing_user = db.query(User).filter(User.email == parent_email).first()
if existing_user:
    role_names = {"student": "học sinh", "parent": "phụ huynh", ...}
    raise HTTPException(
        400,
        f"Email {parent_email} đã được đăng ký với vai trò '{role_vn}'.
         Vui lòng sử dụng email khác cho phụ huynh."
    )
```

**Key improvements:**

- ✅ Email normalization (lowercase, trim)
- ✅ Regex validation for email format
- ✅ Self-reference check (can't use own email)
- ✅ Duplicate check with Vietnamese role translation
- ✅ Clear, user-friendly error messages in Vietnamese

### 2. **Schema Validators** (`ai-service/app/schemas/student.py`)

```python
class StudentUpdate(BaseModel):
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("Họ và tên phải có ít nhất 2 ký tự")
        return v.strip() if v else v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None and v.strip():
            phone = v.strip()
            if not re.match(r'^[0-9+\-\(\)\s]{8,15}$', phone):
                raise ValueError("Số điện thoại không hợp lệ")
            return phone
        return None if not v or not v.strip() else v

    @validator('parent_email')
    def validate_parent_email(cls, v):
        if v is not None and v.strip():
            email = v.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValueError("Email phụ huynh không hợp lệ")
            return email
        return None if not v or not v.strip() else v
```

**Key improvements:**

- ✅ Handles `None` and empty strings gracefully
- ✅ Returns `None` for empty optional fields (prevents database constraint violations)
- ✅ Normalizes data (trim, lowercase for emails)
- ✅ Vietnamese error messages

### 3. **Reusable AlertModal Component** (`frontend/src/components/AlertModal/`)

**New component structure:**

```
AlertModal/
├── AlertModal.tsx    # Main component with MUI Dialog
└── index.ts          # Export with types
```

**Features:**

- ✅ 4 alert types: `success`, `info`, `warning`, `error`
- ✅ Icon for each type (CheckCircle, Info, Warning, Error)
- ✅ Customizable title & message
- ✅ Optional cancel button
- ✅ Support for React nodes (not just strings)
- ✅ Responsive MUI design

**Usage:**

```tsx
<AlertModal
  open={alertModal.open}
  onClose={closeAlert}
  type="error"
  title="Email không hợp lệ"
  message="Không thể sử dụng email của chính bạn..."
  confirmText="Đã hiểu"
/>
```

### 4. **Frontend Validation** (`frontend/src/pages/ProfilePage/components/EditProfileModal.tsx`)

#### Pre-submission validation:

```typescript
const onSubmit = async (data: EditProfileFormData) => {
  // 1. Validate parent email
  if (data.parent_email) {
    const parentEmail = data.parent_email.trim().toLowerCase();

    // Check self-reference
    if (parentEmail === user.email.toLowerCase()) {
      showAlert(
        "error",
        "Email không hợp lệ",
        "Không thể sử dụng email của chính bạn..."
      );
      return;
    }

    // Validate format
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(parentEmail)) {
      showAlert(
        "error",
        "Email không hợp lệ",
        "Vui lòng nhập địa chỉ email hợp lệ..."
      );
      return;
    }

    data.parent_email = parentEmail; // Normalize
  }

  try {
    await onSave(data);
    onClose();
  } catch (error: any) {
    // Handle backend errors with AlertModal
    if (error.response?.data?.detail) {
      showAlert("error", "Không thể cập nhật", error.response.data.detail);
    }
  }
};
```

**Key improvements:**

- ✅ Client-side validation BEFORE API call (faster feedback)
- ✅ Email normalization matches backend
- ✅ Self-reference check prevents unnecessary API call
- ✅ Backend errors displayed in AlertModal (not console)
- ✅ Vietnamese user-friendly messages

## 🎨 UX Improvements

### Before:

```
User enters own email → Submit → 500 error → Nothing displayed
```

### After:

```
User enters own email → Submit → AlertModal appears:
┌─────────────────────────────────┐
│ ❌ Email không hợp lệ           │
├─────────────────────────────────┤
│ Không thể sử dụng email của     │
│ chính bạn làm email phụ huynh.  │
│ Vui lòng nhập email khác.       │
├─────────────────────────────────┤
│                    [Đã hiểu]    │
└─────────────────────────────────┘
```

## 📋 Validation Rules Summary

| Field          | Rules                                     | Error Message                                     |
| -------------- | ----------------------------------------- | ------------------------------------------------- |
| `full_name`    | Min 2 chars, trim whitespace              | "Họ và tên phải có ít nhất 2 ký tự"               |
| `phone_number` | 8-15 digits, optional                     | "Số điện thoại không hợp lệ"                      |
| `parent_email` | Valid email format, not own email, unique | "Email đã được đăng ký với vai trò 'học sinh'..." |
| Empty strings  | Converted to `None`                       | -                                                 |

## 🧪 Test Cases

### Test 1: Use own email as parent email

**Input:** parent_email = current_user.email  
**Expected:** ❌ AlertModal with "Không thể sử dụng email của chính bạn..."  
**Status:** ✅ Frontend catches, no API call

### Test 2: Email already registered (student role)

**Input:** parent_email = "existing_student@gmail.com"  
**Expected:** ❌ AlertModal with "Email đã được đăng ký với vai trò 'học sinh'..."  
**Status:** ✅ Backend catches, returns 400 error

### Test 3: Invalid email format

**Input:** parent_email = "invalid@email"  
**Expected:** ❌ AlertModal with "Email không hợp lệ"  
**Status:** ✅ Frontend catches, no API call

### Test 4: Valid new parent email

**Input:** parent_email = "new_parent@gmail.com"  
**Expected:** ✅ Create parent account, link to student  
**Status:** ✅ Works as expected

### Test 5: Empty optional fields

**Input:** phone_number = "", address = ""  
**Expected:** ✅ Save as `NULL` in database  
**Status:** ✅ Validators convert empty strings to `None`

## 🔧 Files Modified

### Backend (Python/FastAPI):

- `ai-service/app/api/v1/endpoints/students.py` - Enhanced validation logic
- `ai-service/app/schemas/student.py` - Added Pydantic validators

### Frontend (React/TypeScript):

- `frontend/src/components/AlertModal/AlertModal.tsx` - New reusable component
- `frontend/src/components/AlertModal/index.ts` - Export file
- `frontend/src/pages/ProfilePage/components/EditProfileModal.tsx` - Integrated AlertModal + validation

## 🚀 Next Steps (Optional Improvements)

1. **Email Verification System**

   - Send welcome email to parent with activation link
   - Auto-generate secure temporary password
   - Parent must verify email before account is active

2. **Enhanced AlertModal Features**

   - Support for lists/arrays in message (for multiple errors)
   - Progress indicator for async actions
   - Toast notifications for non-critical alerts

3. **More Granular Validation**

   - Phone number country code detection
   - Address autocomplete with Google Maps API
   - Student code format validation based on university

4. **Audit Logging**
   - Log all profile updates with timestamp
   - Track parent account creation events
   - Email notifications on security-critical changes

## 📚 References

- Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/
- MUI Dialog: https://mui.com/material-ui/react-dialog/
- React Hook Form: https://react-hook-form.com/
