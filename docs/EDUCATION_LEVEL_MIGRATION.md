# 🎓 Migration: Thay year_of_study → education_level + grade

## 📋 Vấn Đề

- `year_of_study` (1-5) chỉ phù hợp cho sinh viên
- Cần support cả học sinh THPT (lớp 10, 11, 12)

## ✅ Giải Pháp

Thay 1 column `year_of_study` bằng 2 columns:

1. `education_level` (enum): 'high_school' | 'undergraduate' | 'graduate' | 'other'
2. `grade` (varchar): '10', '11', '12', '1', '2', '3', '4', '5'...

---

## 🔧 BƯỚC 1: Chạy SQL Migration trên Supabase

### 1.1. Thêm columns mới

```sql
-- Thêm education_level enum
ALTER TABLE students
ADD COLUMN education_level VARCHAR(50) CHECK (
    education_level IN ('high_school', 'undergraduate', 'graduate', 'other')
);

-- Thêm grade (flexible string)
ALTER TABLE students
ADD COLUMN grade VARCHAR(20);
```

### 1.2. Migrate data cũ (nếu có)

```sql
-- Convert year_of_study sang undergraduate + grade
UPDATE students
SET
    education_level = 'undergraduate',
    grade = CAST(year_of_study AS VARCHAR)
WHERE year_of_study IS NOT NULL;

-- Verify
SELECT
    year_of_study,
    education_level,
    grade
FROM students
WHERE year_of_study IS NOT NULL
LIMIT 10;
```

### 1.3. Xóa column cũ (sau khi verify)

```sql
-- Chỉ xóa sau khi test kỹ!
ALTER TABLE students
DROP COLUMN year_of_study;
```

---

## 📝 BƯỚC 2: Update Backend Schemas

### 2.1. Tạo Enums (`ai-service/app/schemas/student.py`)

```python
class EducationLevelEnum(str, Enum):
    """Education level options"""
    HIGH_SCHOOL = "high_school"        # THPT
    UNDERGRADUATE = "undergraduate"    # Đại học
    GRADUATE = "graduate"              # Sau đại học
    OTHER = "other"                    # Khác

class GradeEnum(str, Enum):
    """Grade/Year options"""
    # High school
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"

    # Undergraduate
    YEAR_1 = "1"
    YEAR_2 = "2"
    YEAR_3 = "3"
    YEAR_4 = "4"
    YEAR_5 = "5"
    YEAR_6 = "6"
```

### 2.2. Update StudentBase

```python
class StudentBase(BaseModel):
    # ... existing fields ...

    # Academic info - NEW
    education_level: Optional[EducationLevelEnum] = None
    grade: Optional[str] = Field(None, max_length=20, description="Grade/Year (e.g., '10', '11', '12', '1', '2'...)")

    # Remove: year_of_study
```

---

## 🎨 BƯỚC 3: Update Frontend

### 3.1. Types (`frontend/src/types/auth.ts`)

```typescript
export type EducationLevel =
  | "high_school" // THPT
  | "undergraduate" // Đại học
  | "graduate" // Sau đại học
  | "other"; // Khác

export interface RegisterRequest {
  // ... existing fields ...
  education_level?: EducationLevel;
  grade?: string; // '10', '11', '12', '1', '2', '3', '4', '5'
  // Remove: year_of_study
}
```

### 3.2. Registration Form UI

```tsx
{
  /* Education Level */
}
<div className="form-group">
  <label htmlFor="education_level" className="form-label">
    Trình độ học vấn
  </label>
  <select
    id="education_level"
    name="education_level"
    value={formData.education_level || ""}
    onChange={handleChange}
    className="form-select"
  >
    <option value="">Chọn trình độ</option>
    <option value="high_school">Học sinh THPT</option>
    <option value="undergraduate">Sinh viên Đại học</option>
    <option value="graduate">Sau đại học</option>
    <option value="other">Khác</option>
  </select>
</div>;

{
  /* Grade - Dynamic based on education_level */
}
{
  formData.education_level && (
    <div className="form-group">
      <label htmlFor="grade" className="form-label">
        {formData.education_level === "high_school" ? "Lớp" : "Năm học"}
      </label>
      <select
        id="grade"
        name="grade"
        value={formData.grade || ""}
        onChange={handleChange}
        className="form-select"
      >
        <option value="">
          {formData.education_level === "high_school"
            ? "Chọn lớp"
            : "Chọn năm học"}
        </option>

        {/* High School */}
        {formData.education_level === "high_school" && (
          <>
            <option value="10">Lớp 10</option>
            <option value="11">Lớp 11</option>
            <option value="12">Lớp 12</option>
          </>
        )}

        {/* Undergraduate */}
        {formData.education_level === "undergraduate" && (
          <>
            <option value="1">Năm 1</option>
            <option value="2">Năm 2</option>
            <option value="3">Năm 3</option>
            <option value="4">Năm 4</option>
            <option value="5">Năm 5</option>
          </>
        )}

        {/* Graduate/Other */}
        {(formData.education_level === "graduate" ||
          formData.education_level === "other") && (
          <option value="other">Khác</option>
        )}
      </select>
    </div>
  );
}
```

---

## 📊 BƯỚC 4: Update Display Logic

### Profile Page Display

```typescript
const getEducationDisplay = (profile: StudentProfile) => {
  if (!profile.education_level) return "Chưa cập nhật";

  const levelMap = {
    high_school: "THPT",
    undergraduate: "Đại học",
    graduate: "Sau đại học",
    other: "Khác",
  };

  const level = levelMap[profile.education_level];

  if (profile.grade) {
    if (profile.education_level === "high_school") {
      return `${level} - Lớp ${profile.grade}`;
    } else {
      return `${level} - Năm ${profile.grade}`;
    }
  }

  return level;
};

// Display: "THPT - Lớp 11" hoặc "Đại học - Năm 2"
```

---

## ✅ Checklist Migration

- [ ] Chạy SQL migration (thêm columns mới)
- [ ] Migrate data cũ (year_of_study → education_level + grade)
- [ ] Verify data migration
- [ ] Update backend models (`student.py`)
- [ ] Update backend schemas (`student.py`)
- [ ] Update frontend types (`auth.ts`, `userService.ts`)
- [ ] Update registration form UI
- [ ] Update profile page display
- [ ] Test registration flow
- [ ] Test profile update
- [ ] ✋ Xóa `year_of_study` column (sau khi mọi thứ OK)

---

## 🎯 Ưu Điểm Của Giải Pháp Mới

| Feature        | Cũ (year_of_study) | Mới (education_level + grade) |
| -------------- | ------------------ | ----------------------------- |
| Support THPT   | ❌ Không           | ✅ Có (10, 11, 12)            |
| Support SV     | ✅ Có              | ✅ Có (1, 2, 3, 4, 5)         |
| Support Sau ĐH | ❌ Không           | ✅ Có                         |
| Flexible       | ❌ Cứng (1-5)      | ✅ Linh hoạt (string)         |
| Clear meaning  | ❌ Không rõ        | ✅ Rõ ràng                    |

---

**Next:** Bạn muốn tôi generate code hoàn chỉnh cho migration này không?
