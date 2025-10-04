# 🎉 Hoàn Thành: Refactor Emergency Contact System

## 📋 Tổng Quan

Đã hoàn thành refactor hệ thống emergency contact từ duplicate data fields sang foreign key relationship với `parents` table, tận dụng architecture có sẵn của hệ thống.

---

## ✅ Các Thay Đổi Đã Thực Hiện

### 🗄️ 1. Database Migration (Supabase)

**File:** `database-migrations/01_add_emergency_contact_parent_fk.sql`

**Thay đổi:**

- ✅ Thêm column `emergency_contact_parent_id INTEGER` vào `students` table
- ✅ Thêm foreign key constraint đến `parents(id)` với `ON DELETE SET NULL`
- ✅ Tạo index cho `emergency_contact_parent_id`
- 🔄 **Chưa xóa:** `emergency_contact_name`, `emergency_contact_phone`, `emergency_contact_relationship` (đợi sau khi test)

**Hướng dẫn:** Xem `SUPABASE_MIGRATION_GUIDE.md` để thực hiện migration từng bước

---

### 🔧 2. Backend Changes

#### **Models** (`ai-service/app/models/student.py`)

```python
# OLD (Duplicate data)
emergency_contact_name = Column(String(255))
emergency_contact_phone = Column(String(20))
emergency_contact_relationship = Column(String(100))

# NEW (Foreign key relationship)
emergency_contact_parent_id = Column(Integer, ForeignKey("parents.id", ondelete="SET NULL"))
emergency_contact_parent = relationship("Parent", foreign_keys=[emergency_contact_parent_id])
```

#### **Schemas** (`ai-service/app/schemas/`)

**`student.py`:**

- ✅ `StudentBase.emergency_contact_parent_id: Optional[int]`
- ✅ `StudentUpdate.emergency_contact_parent_id: Optional[int]`
- ❌ Removed: `emergency_contact_name/phone/relationship`

**`auth.py`:**

- ✅ `UserCreate.parent_email: Optional[EmailStr]` - Cho registration

#### **API Endpoints**

**NEW: `PUT /api/v1/students/me`** (`ai-service/app/api/v1/endpoints/students.py`)

```python
@router.put("/me")
def update_current_student_profile(
    student_data: StudentUpdate,
    parent_email: Optional[EmailStr] = None,  # Query parameter
    current_student: Student = Depends(get_current_user_student),
    db: Session = Depends(get_db)
):
    # Update student profile
    # If parent_email provided:
    #   - Check if parent exists → link to existing parent
    #   - If not exists → create new parent account (inactive, needs verification)
    # Cannot delete parent once set
```

**UPDATED: `POST /api/v1/auth/register`** (`ai-service/app/api/v1/endpoints/auth.py`)

```python
# Handle parent_email during student registration
if user_data.parent_email:
    # Check if parent exists
    # If exists → link student to parent
    # If not → create temporary parent account + send welcome email
    student.emergency_contact_parent_id = parent_id
```

---

### 💻 3. Frontend Changes

#### **Types** (`frontend/src/types/auth.ts`)

```typescript
export interface RegisterRequest {
  // ... existing fields ...
  parent_email?: string; // NEW: Emergency contact parent email
}
```

#### **Services** (`frontend/src/services/userService.ts`)

```typescript
export interface StudentProfile {
  // OLD (removed):
  // emergency_contact_name?: string;
  // emergency_contact_phone?: string;
  // emergency_contact_relationship?: string;

  // NEW:
  emergency_contact_parent_id?: number;
  parent_email?: string; // For display/edit
}
```

#### **Registration Form** (`frontend/src/pages/RegisterPage/RegisterPage.tsx`)

```tsx
{/* NEW: Parent Email Field (for students) */}
<input
  type="email"
  name="parent_email"
  placeholder="phu.huynh@example.com"
/>
<small>
  🔐 Hệ thống sẽ tự động tạo tài khoản cho phụ huynh nếu chưa tồn tại.
</small>
```

#### **Profile Page** (`frontend/src/pages/ProfilePage/`)

**EditProfileModal.tsx:**

- ✅ Replaced 3 emergency contact fields với 1 field: `parent_email`
- ✅ Email validation
- ✅ Hint message về auto-create parent account

**AcademicInfoCard.tsx:**

- ✅ Display parent email thay vì emergency contact name/phone/relationship

**ProfilePage.tsx:**

- ✅ Call `updateStudentProfile()` với `parent_email` parameter

---

## 🎯 Ưu Điểm Của Giải Pháp Mới

### 1. ✅ **Không Duplicate Data**

- Thông tin parent (email, name, phone) chỉ lưu 1 lần trong `parents` + `users` table
- Không cần sync data khi parent thay đổi thông tin

### 2. ✅ **Scalable & Extensible**

- Dễ dàng thêm features:
  - Send email notification đến parent
  - Parent login xem data của con
  - Multiple students có thể share 1 parent
  - Parent consent system đã có sẵn (`parent_consents` table)

### 3. ✅ **Consistent Architecture**

- Tận dụng architecture có sẵn (User → Parent relationship)
- Tất cả roles (student, parent, counselor, admin) đều là `users`

### 4. ✅ **Better Security**

- Parent email được validate tại user level
- Parent account có password riêng (có thể login)
- Parent có thể update thông tin của mình

### 5. ✅ **Future-Proof**

- Trigger/notification system dễ implement:
  ```python
  if assessment.severity_level == 'severe':
      parent_email = student.emergency_contact_parent.user.email
      send_emergency_notification(parent_email, student, assessment)
  ```

---

## 🚀 Các Bước Triển Khai

### **Phase 1: Database Migration** ⏳

1. Backup database trên Supabase
2. Chạy `BƯỚC 1-3` trong `SUPABASE_MIGRATION_GUIDE.md`
3. Verify column `emergency_contact_parent_id` tồn tại

### **Phase 2: Backend Deployment** ⏳

1. Deploy backend code changes
2. Test API endpoints:
   - `POST /api/v1/auth/register` với `parent_email`
   - `PUT /api/v1/students/me` với `parent_email` parameter
3. Verify parent accounts được tạo đúng

### **Phase 3: Frontend Deployment** ⏳

1. Deploy frontend code changes
2. Test registration flow với parent email
3. Test profile update flow với parent email

### **Phase 4: Data Migration** (Optional) ⏳

1. Nếu có data cũ trong `emergency_contact_name/phone`:
   - Chạy migration script tạo temporary parent accounts
   - Link students với parents vừa tạo
2. Verify tất cả students có `emergency_contact_parent_id`

### **Phase 5: Cleanup** ⏳

1. Sau khi verify mọi thứ hoạt động tốt:
   - Xóa columns cũ: `emergency_contact_name/phone/relationship`
   - Set `emergency_contact_parent_id NOT NULL` (optional)

---

## 📝 TODO: Các Features Cần Thêm

### 1. 🔔 **Email Notification System**

```python
# Khi có assessment nguy hiểm
def send_emergency_notification(assessment: Assessment):
    student = assessment.student
    if student.emergency_contact_parent:
        parent_email = student.emergency_contact_parent.user.email
        send_email(
            to=parent_email,
            subject=f"Thông báo khẩn: Kết quả đánh giá của {student.user.full_name}",
            body=f"Điểm GAD-7: {assessment.total_score} (Mức độ: {assessment.severity_level})"
        )
```

### 2. 📧 **Welcome Email For Parents**

```python
# Sau khi tạo parent account mới
def send_parent_welcome_email(parent_email: str):
    send_email(
        to=parent_email,
        subject="Chào mừng đến AI4Mind - Xác thực tài khoản",
        body="""
        Con của bạn đã đăng ký bạn làm liên hệ khẩn cấp.
        Vui lòng click link dưới để kích hoạt tài khoản:
        [Activation Link]
        """
    )
```

### 3. 🔗 **Parent Consent Flow**

```python
# Sử dụng parent_consents table có sẵn
# Student request parent để xem data
# Parent approve/reject request
```

### 4. 📊 **Parent Dashboard**

```python
# Parent login và xem:
# - Danh sách con đã link
# - Assessment history của con (nếu có consent)
# - Notifications về con
```

### 5. ⚙️ **Admin Panel**

```python
# Admin có thể:
# - Xem tất cả student-parent relationships
# - Manually link/unlink students với parents
# - Send batch notifications
```

---

## 📚 File References

### Database

- `database-migrations/01_add_emergency_contact_parent_fk.sql` - Migration script
- `SUPABASE_MIGRATION_GUIDE.md` - Chi tiết từng bước migration
- `sql.txt` - Current database schema

### Backend

- `ai-service/app/models/student.py` - Student model
- `ai-service/app/schemas/student.py` - Student schemas
- `ai-service/app/schemas/auth.py` - Auth schemas (UserCreate)
- `ai-service/app/api/v1/endpoints/students.py` - Students API (PUT /me)
- `ai-service/app/api/v1/endpoints/auth.py` - Auth API (register)

### Frontend

- `frontend/src/types/auth.ts` - RegisterRequest type
- `frontend/src/services/userService.ts` - StudentProfile type
- `frontend/src/pages/RegisterPage/RegisterPage.tsx` - Registration form
- `frontend/src/pages/ProfilePage/ProfilePage.tsx` - Profile page
- `frontend/src/pages/ProfilePage/components/EditProfileModal.tsx` - Edit modal
- `frontend/src/pages/ProfilePage/components/AcademicInfoCard.tsx` - Display card

---

## 🎓 Lessons Learned

1. **Tận dụng Architecture có sẵn:** Thay vì tạo fields mới, hãy xem xét relationships đã có
2. **Foreign Key > Duplicate Data:** Luôn ưu tiên foreign key để đảm bảo data consistency
3. **Migration an toàn:** Thêm columns mới trước, migrate data, rồi mới xóa columns cũ
4. **Scalability matters:** Thiết kế cho future features (notifications, parent dashboard)
5. **Single source of truth:** Parent info chỉ lưu 1 nơi (users + parents table)

---

## 🤝 Next Steps

1. **Chạy migration trên Supabase** theo `SUPABASE_MIGRATION_GUIDE.md`
2. **Test toàn bộ flow:**
   - Registration với parent email
   - Update parent email trong profile
   - Parent account được tạo đúng
3. **Implement email notification system** (high priority)
4. **Deploy to production** sau khi test kỹ

---

**Status:** ✅ Code Complete | ⏳ Pending Database Migration & Testing

**Author:** GitHub Copilot  
**Date:** October 3, 2025  
**Review:** Pending
