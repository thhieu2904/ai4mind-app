# Fix: year_of_study Column Not Found Error

## 🐛 Reported Error

```
INFO: 127.0.0.1:54784 - "GET /api/v1/auth/me HTTP/1.1" 500 Internal Server Error

"message": "Database error occurred"
"detail": "(psycopg2.errors.UndefinedColumn) column students.year_of_study does not exist"
```

## 🔍 Root Cause Analysis

### Timeline of Events:

1. **Database was migrated** - The `year_of_study` column was **DROPPED** from `students` table
2. **New columns added** - `education_level` (enum) + `grade` (string) were added
3. **Backend code not updated** - SQLAlchemy models/schemas still referenced the old `year_of_study` column
4. **Query failed** - When SQLAlchemy tried to SELECT `students.year_of_study`, PostgreSQL returned error

### Why This Error Appeared Now:

**NOT** because of the emergency contact fix! The error occurred because:

- ✅ Database schema changed (removed `year_of_study`, added `education_level` + `grade`)
- ❌ Backend code still had old field definitions
- 🔥 Mismatch caused 500 error when querying student data

### Database Schema (from sql.txt):

```sql
CREATE TABLE public.students (
  -- ...
  university character varying,
  major character varying,
  education_level character varying CHECK (
    education_level::text = ANY (ARRAY[
      'high_school'::character varying,
      'undergraduate'::character varying,
      'graduate'::character varying,
      'other'::character varying
    ]::text[])
  ),
  grade character varying,  -- Replaces year_of_study
  -- ...
);
```

## ✅ Solution Implemented

### 1. Updated Model (`ai-service/app/models/student.py`)

**Before:**

```python
year_of_study = Column(Integer, nullable=True)  # Năm học (1, 2, 3, 4)
```

**After:**

```python
education_level = Column(String(50), nullable=True)  # high_school, undergraduate, graduate, other
grade = Column(String(50), nullable=True)  # Grade/Year: '10', '11', '12', '1'-'5', etc.
```

### 2. Updated Schemas (`ai-service/app/schemas/student.py`)

**Added EducationLevelEnum:**

```python
class EducationLevelEnum(str, Enum):
    """Education level options"""
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    OTHER = "other"
```

**Updated StudentBase:**

```python
# Before
year_of_study: Optional[int] = Field(None, ge=1, le=6, description="Year of study (1-6)")

# After
education_level: Optional[EducationLevelEnum] = Field(None, description="Education level")
grade: Optional[str] = Field(None, max_length=50, description="Grade/Year (e.g., '10', '11', '1', '2')")
```

**Updated StudentUpdate:**

```python
# Before
year_of_study: Optional[int] = Field(None, ge=1, le=6)

# After
education_level: Optional[EducationLevelEnum] = None
grade: Optional[str] = Field(None, max_length=50)
```

**Updated StudentPublicProfile:**

```python
# Before
year_of_study: Optional[int]

# After
education_level: Optional[str]
grade: Optional[str]
```

### 3. Updated Auth Schema (`ai-service/app/schemas/auth.py`)

**RegisterRequest:**

```python
# Before
year_of_study: Optional[int] = Field(None, ge=1, le=7)

# After
education_level: Optional[str] = Field(None, pattern="^(high_school|undergraduate|graduate|other)$")
grade: Optional[str] = Field(None, max_length=50)
```

### 4. Updated Registration Endpoint (`ai-service/app/api/v1/endpoints/auth.py`)

**Student creation:**

```python
# Before
student = Student(
    user_id=user.id,
    # ...
    year_of_study=user_data.year_of_study,
    emergency_contact_parent_id=emergency_contact_parent_id
)

# After
student = Student(
    user_id=user.id,
    # ...
    education_level=user_data.education_level,
    grade=user_data.grade,
    emergency_contact_parent_id=emergency_contact_parent_id
)
```

**GET /auth/me response:**

```python
# Before
profile = {
    "student_code": student.student_code,
    "university": student.university,
    "major": student.major,
    "year_of_study": student.year_of_study
}

# After
profile = {
    "student_code": student.student_code,
    "university": student.university,
    "major": student.major,
    "education_level": student.education_level,
    "grade": student.grade
}
```

## 📊 Migration Mapping

### For High School Students:

- `education_level` = `"high_school"`
- `grade` = `"10"`, `"11"`, or `"12"`

### For University Students:

- `education_level` = `"undergraduate"`
- `grade` = `"1"`, `"2"`, `"3"`, `"4"`, or `"5"`

### For Graduate Students:

- `education_level` = `"graduate"`
- `grade` = `"1"`, `"2"`, `"3"`, etc.

### For Other:

- `education_level` = `"other"`
- `grade` = Any custom value

## 🧪 Testing

### Backend Test:

```powershell
cd d:\job\ai4mind-app\ai-service
python -m uvicorn app.main:app --reload
```

Then test:

1. **GET /api/v1/auth/me** - Should return 200 with `education_level` + `grade`
2. **GET /api/v1/students/me** - Should work without column errors
3. **POST /api/v1/auth/register** - Test with new fields

### Sample Request:

```json
{
  "email": "student@test.com",
  "password": "Test1234!",
  "full_name": "Test Student",
  "role": "student",
  "student_code": "HS001",
  "education_level": "high_school",
  "grade": "11",
  "date_of_birth": "2008-05-15",
  "gender": "male",
  "university": "THPT Chuyên Lê Hồng Phong",
  "parent_email": "parent@test.com"
}
```

### Expected Response:

```json
{
  "id": 1,
  "user_id": 123,
  "email": "student@test.com",
  "full_name": "Test Student",
  "education_level": "high_school",
  "grade": "11",
  "university": "THPT Chuyên Lê Hồng Phong",
  "parent_email": "parent@test.com"
}
```

## ✅ Verification Checklist

- [x] Model updated: `year_of_study` → `education_level` + `grade`
- [x] Schemas updated: All occurrences replaced
- [x] Endpoints updated: Registration and GET /me
- [x] No more `year_of_study` references in backend (verified with grep)
- [ ] Backend restart and test
- [ ] Frontend registration form test
- [ ] Profile page display test

## 🔗 Related Documents

- `EDUCATION_LEVEL_MIGRATION.md` - Original migration guide
- `FIX_GET_500_ERROR.md` - GET /auth/me emergency contact fix
- `FIX_PUT_405_ERROR.md` - PUT endpoint consolidation

## 📝 Notes

This fix aligns the backend code with the database schema that was migrated earlier. The `year_of_study` field was replaced with a more flexible `education_level` + `grade` system to support both high school (grades 10-12) and university (years 1-5+) students.
