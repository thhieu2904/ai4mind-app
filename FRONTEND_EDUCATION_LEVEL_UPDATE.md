# Frontend Update: education_level + grade

## ✅ Files Updated

### 1. **Types** (`frontend/src/types/auth.ts`)

- Updated `User.student` interface
- Updated `RegisterRequest` interface
- Replaced `year_of_study: number` → `education_level: string` + `grade: string`

### 2. **Services** (`frontend/src/services/userService.ts`)

- Updated `StudentProfile` interface
- Now matches backend schema

### 3. **Components**

#### AcademicInfoCard (`frontend/src/pages/ProfilePage/components/AcademicInfoCard.tsx`)

- Replaced `getYearLabel()` → `getEducationLabel()` helper
- Updated display logic to show education level + grade
- Example display: "THPT - Lớp 11" or "Đại học - Lớp 3"

#### EditProfileModal (`frontend/src/pages/ProfilePage/components/EditProfileModal.tsx`)

- Updated form data interface
- Changed single "Năm học" dropdown → Two fields:
  1. **Cấp học** dropdown: THPT, Đại học, Sau đại học, Khác
  2. **Lớp/Năm** text input: Free-form (10, 11, 12, 1, 2, 3, 4, 5)
- Updated form reset logic

#### ProfilePage (`frontend/src/pages/ProfilePage/ProfilePage.tsx`)

- Updated `handleSaveProfile()` to send `education_level` + `grade` instead of `year_of_study`

## 📊 UI Changes

### Before:

```
Năm học: [Dropdown: Năm 1, Năm 2, Năm 3, Năm 4, Năm 5]
```

### After:

```
Cấp học: [Dropdown: THPT, Đại học, Sau đại học, Khác]
Lớp/Năm: [Text input: "10", "11", "12", "1", "2", "3", "4", "5"]
```

## 🧪 Testing PUT Endpoint

Your sample data looks correct:

```json
{
  "student_code": null,
  "date_of_birth": "2001-02-03",
  "phone_number": "",
  "address": null,
  "gender": "male",
  "university": null,
  "major": null,
  "education_level": null,
  "grade": null,
  "emergency_contact_parent_id": null,
  "id": 52,
  "user_id": 57,
  "email": "thhieu2904das@gmail.com",
  "full_name": "Hoàng Nguyễn",
  "parent_email": null
}
```

### Test PUT Request

To verify PUT works, try updating profile:

```bash
# Replace YOUR_TOKEN with actual JWT token
curl -X PUT http://localhost:8000/api/v1/students/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Hoàng Nguyễn Updated",
    "phone_number": "0123456789",
    "education_level": "high_school",
    "grade": "11",
    "university": "THPT Chuyên Lê Hồng Phong"
  }'
```

Expected response:

```json
{
  "id": 52,
  "user_id": 57,
  "email": "thhieu2904das@gmail.com",
  "full_name": "Hoàng Nguyễn Updated",
  "phone_number": "0123456789",
  "education_level": "high_school",
  "grade": "11",
  "university": "THPT Chuyên Lê Hồng Phong",
  ...
}
```

## ✅ Verification Checklist

- [x] Backend models updated
- [x] Backend schemas updated
- [x] Backend endpoints updated
- [x] Frontend types updated
- [x] Frontend components updated
- [x] No more `year_of_study` references in codebase
- [ ] Frontend dev server restart
- [ ] Backend server restart
- [ ] Test Profile Page load (GET)
- [ ] Test Profile Page edit (PUT)

## 🚀 Next Steps

1. **Restart frontend dev server:**

   ```bash
   cd frontend
   npm run dev
   ```

2. **Restart backend server:**

   ```bash
   cd ai-service
   python -m uvicorn app.main:app --reload
   ```

3. **Test in browser:**
   - Open Profile Page
   - Should display without crashes
   - Click "Chỉnh sửa"
   - See new "Cấp học" + "Lớp/Năm" fields
   - Update values and save
   - Verify PUT request succeeds

## 🎨 Display Examples

### High School Student:

- **Cấp học:** THPT
- **Lớp:** 11
- **Display:** "THPT - Lớp 11"

### University Student:

- **Cấp học:** Đại học
- **Lớp:** 3
- **Display:** "Đại học - Lớp 3"

### Graduate Student:

- **Cấp học:** Sau đại học
- **Lớp:** 2
- **Display:** "Sau đại học - Lớp 2"
