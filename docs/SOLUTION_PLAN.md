"""
SOLUTION PLAN - Backend API Endpoints

=== Vấn đề 1: Missing PUT endpoints ===

Cần tạo 2 endpoints mới:

1. PUT /api/v1/auth/me
   - Update user basic info (full_name, phone)
   - File: app/api/v1/endpoints/auth.py
   - Schema: UserUpdate (cần tạo mới)
2. PUT /api/v1/students/me
   - Update student profile
   - File: app/api/v1/endpoints/students.py
   - Schema: StudentUpdate (đã có sẵn)

=== Vấn đề 2: Missing emergency_contact_email ===

Option A (RECOMMENDED - Simple & Clear):

- Thêm column `emergency_contact_email` vào students table
- Update StudentUpdate schema thêm field emergency_contact_email
- Frontend EditProfileModal thêm input email

Lý do chọn Option A:
✅ Đơn giản, dễ maintain
✅ Emergency contact có thể là bất kỳ ai (không nhất thiết phải là parent trong hệ thống)
✅ Không cần phức tạp hóa với parent_consents relationship
✅ Cho phép nhập email trực tiếp khi cần gửi thông báo khẩn cấp

Option B (Complex - Not recommended for now):

- Link students với parents qua parent_consents table
- Lấy email từ parents.user_id → users.email
- Phức tạp, cần nhiều joins, overkill cho emergency contact

=== Implementation Steps ===

Step 1: Database Migration

- Thêm column emergency_contact_email VARCHAR vào students table
- Alembic migration script

Step 2: Update Schemas

- Thêm emergency_contact_email vào StudentBase, StudentUpdate schemas
- Tạo UserUpdate schema cho auth endpoint

Step 3: Create Backend Endpoints

- Implement PUT /api/v1/auth/me
- Implement PUT /api/v1/students/me

Step 4: Update Frontend

- Thêm emergency_contact_email input vào EditProfileModal
- Update StudentProfile interface
- Update display trong AcademicInfoCard

=== Files cần thay đổi ===

Backend:

1. app/api/v1/endpoints/auth.py - Thêm PUT /me endpoint
2. app/api/v1/endpoints/students.py - Thêm PUT /me endpoint
3. app/schemas/auth.py - Thêm UserUpdate schema
4. app/schemas/student.py - Thêm emergency_contact_email field
5. alembic/versions/xxx_add_emergency_email.py - Migration script

Frontend:

1. src/services/userService.ts - Interface StudentProfile thêm emergency_contact_email
2. src/pages/ProfilePage/components/EditProfileModal.tsx - Thêm email input
3. src/pages/ProfilePage/components/AcademicInfoCard.tsx - Display email
   """
