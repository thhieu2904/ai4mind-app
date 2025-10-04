# Fix: ActivitySummaryCard Invalid Date Crash

## 🐛 Reported Error

```
Uncaught RangeError: Invalid time value
    at ActivitySummaryCard (ActivitySummaryCard.tsx:71:18)
```

## 🔍 Root Cause

### The Problem Chain:

1. **ProfilePage** constructs user object from `studentData` with `created_at: ""`
2. **ActivitySummaryCard** receives `memberSince={user.created_at}` → empty string `""`
3. **date-fns** tries to format: `format(new Date(""), "dd/MM/yyyy")` → **RangeError: Invalid time value**

### Code Flow:

```typescript
// ProfilePage.tsx (Line 49)
setUser({
  created_at: "", // ❌ Empty string!
});

// ProfilePage.tsx (Line 198)
<ActivitySummaryCard
  memberSince={user.created_at} // Passes empty string
/>;

// ActivitySummaryCard.tsx (Line 71)
format(new Date(memberSince), "dd/MM/yyyy"); // 💥 CRASH!
```

## ✅ Solution Implemented

### 1. Backend: Add `created_at` to StudentResponse (`ai-service/app/schemas/student.py`)

**Added field:**

```python
class StudentResponse(StudentBase):
    id: int
    user_id: int

    # User info (from users table)
    email: Optional[str] = None
    full_name: Optional[str] = None

    # Timestamps
    created_at: Optional[str] = None  # NEW: From users.created_at

    # Computed field
    parent_email: Optional[str] = None
```

**Updated `from_orm_with_parent()` method:**

```python
@staticmethod
def from_orm_with_parent(student) -> 'StudentResponse':
    data = StudentResponse.model_validate(student)

    if student.user:
        data.email = student.user.email
        data.full_name = student.user.full_name
        # Convert datetime to ISO string
        if student.user.created_at:
            data.created_at = student.user.created_at.isoformat()

    # ... parent_email population
    return data
```

### 2. Frontend: Update `StudentDetails` Type (`frontend/src/services/userService.ts`)

```typescript
export interface StudentDetails extends StudentProfile {
  id: number;
  user_id: number;
  email?: string; // From student.user relationship
  full_name?: string; // From student.user relationship
  created_at?: string; // NEW: Timestamp when student was created
}
```

### 3. Frontend: Use Real Data in ProfilePage (`frontend/src/pages/ProfilePage/ProfilePage.tsx`)

**Before:**

```typescript
setUser({
  id: studentData.user_id,
  email: "", // ❌ Empty
  full_name: "", // ❌ Empty
  created_at: "", // ❌ Empty - CAUSES CRASH
  // ...
});
```

**After:**

```typescript
setUser({
  id: studentData.user_id,
  email: studentData.email || "", // ✅ From backend
  full_name: studentData.full_name || "", // ✅ From backend
  created_at: studentData.created_at || new Date().toISOString(), // ✅ Real date or fallback
  // ...
});
```

### 4. Frontend: Add Date Validation in ActivitySummaryCard

**Before:**

```typescript
<div className="stat-value">
  {format(new Date(memberSince), "dd/MM/yyyy", { locale: vi })}
</div>
```

**After:**

```typescript
interface ActivitySummaryCardProps {
  memberSince?: string; // Made optional
  // ...
}

<div className="stat-value">
  {memberSince && memberSince.trim() !== ""
    ? format(new Date(memberSince), "dd/MM/yyyy", { locale: vi })
    : "Chưa có"}
</div>;
```

## 📊 API Response Example

**GET /api/v1/students/me** now returns:

```json
{
  "id": 52,
  "user_id": 57,
  "email": "thhieu2904das@gmail.com",
  "full_name": "Hoàng Nguyễn",
  "created_at": "2024-09-15T10:30:00.123456", // NEW: ISO format timestamp
  "student_code": null,
  "date_of_birth": "2001-02-03",
  "phone_number": "",
  "education_level": null,
  "grade": null,
  "parent_email": null
}
```

## 🧪 Testing

### Backend Test:

```bash
# Restart backend
cd ai-service
python -m uvicorn app.main:app --reload
```

Test API response:

```bash
curl -X GET http://localhost:8000/api/v1/students/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: Response includes `"created_at": "2024-..."` in ISO format

### Frontend Test:

```bash
# Restart frontend
cd frontend
npm run dev
```

1. Open Profile Page → Should load without crash ✅
2. Check "Thành viên từ" field → Should display "DD/MM/YYYY" format ✅
3. Verify in DevTools Network tab → `created_at` field present in response ✅

## 🔧 Files Changed

### Backend (1 file):

- ✅ `ai-service/app/schemas/student.py`
  - Added `created_at: Optional[str]` field
  - Updated `from_orm_with_parent()` to populate from `student.user.created_at`

### Frontend (3 files):

- ✅ `frontend/src/services/userService.ts`
  - Added `created_at?: string` to `StudentDetails` interface
- ✅ `frontend/src/pages/ProfilePage/ProfilePage.tsx`
  - Use real `studentData.created_at` instead of empty string
  - Fallback to current date if not available
- ✅ `frontend/src/pages/ProfilePage/components/ActivitySummaryCard.tsx`
  - Made `memberSince` optional in props
  - Added validation before formatting date
  - Show "Chưa có" if date is invalid

## 📝 Prevention

To prevent similar date-related crashes in the future:

1. **Always validate dates before parsing:**

   ```typescript
   const isValidDate = dateStr && dateStr.trim() !== "";
   if (isValidDate) {
     format(new Date(dateStr), "dd/MM/yyyy");
   }
   ```

2. **Use optional types for nullable data:**

   ```typescript
   memberSince?: string  // Better than memberSince: string
   ```

3. **Provide fallback values:**

   ```typescript
   created_at: studentData.created_at || new Date().toISOString();
   ```

4. **Backend should always return complete data:**
   - Don't leave timestamp fields as null if possible
   - Use database defaults: `DEFAULT now()` in SQL

## ✅ Resolution Status

- [x] Backend schema updated with `created_at` field
- [x] Backend populates `created_at` from `users.created_at`
- [x] Frontend types updated
- [x] ProfilePage uses real data
- [x] ActivitySummaryCard validates dates
- [ ] Backend server restart
- [ ] Frontend server restart
- [ ] Test Profile Page loads without crash
- [ ] Verify "Thành viên từ" displays correctly
