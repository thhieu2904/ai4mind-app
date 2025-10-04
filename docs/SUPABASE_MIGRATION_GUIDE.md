# 📋 Hướng Dẫn Chi Tiết: Sửa Database trên Supabase

## 🎯 Mục tiêu

Thay thế các fields `emergency_contact_name/phone/relationship` bằng foreign key `emergency_contact_parent_id` để link đến bảng `parents`.

---

## 📝 BƯỚC 1: Backup Database (Quan trọng!)

### Trên Supabase Dashboard:

1. Vào **Database** → **Backups**
2. Click **Create backup** để tạo backup trước khi migrate
3. Hoặc export data students hiện tại:
   ```sql
   SELECT * FROM students;
   ```

---

## 🔧 BƯỚC 2: Chạy Migration SQL

### 2.1. Mở SQL Editor trên Supabase:

1. Vào project Supabase của bạn
2. Click **SQL Editor** (biểu tượng ⚡ bên trái)
3. Click **New query**

### 2.2. Copy và paste script migration:

Mở file `database-migrations/01_add_emergency_contact_parent_fk.sql` và chạy **BƯỚC 1, 2, 3** trước:

```sql
-- BƯỚC 1: Thêm column mới
ALTER TABLE students
ADD COLUMN emergency_contact_parent_id INTEGER;

-- BƯỚC 2: Thêm foreign key constraint
ALTER TABLE students
ADD CONSTRAINT fk_students_emergency_contact_parent
FOREIGN KEY (emergency_contact_parent_id)
REFERENCES parents(id)
ON DELETE SET NULL;

-- BƯỚC 3: Tạo index
CREATE INDEX idx_students_emergency_contact_parent_id
ON students(emergency_contact_parent_id);
```

### 2.3. Click **Run** ▶️

✅ **Kết quả mong đợi:** `Success. No rows returned`

---

## 📊 BƯỚC 3: Kiểm tra Migration

### 3.1. Verify column mới đã được tạo:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'students'
  AND column_name = 'emergency_contact_parent_id';
```

✅ **Mong đợi:** 1 row với `emergency_contact_parent_id | integer | YES`

### 3.2. Verify foreign key constraint:

```sql

```

✅ **Mong đợi:** 1 row với constraint name `fk_students_emergency_contact_parent`

---

## 🗄️ BƯỚC 4: Migrate Data Cũ (Nếu có)

### 4.1. Kiểm tra xem có data cũ không:

```sql
SELECT COUNT(*)
FROM students
WHERE emergency_contact_name IS NOT NULL;
```

### 4.2. Nếu COUNT > 0, chạy script migrate:

**⚠️ LƯU Ý:** Script sẽ tạo temporary parent accounts với email dạng `parent_temp_123@ai4mind.temp`

```sql
-- Tạo user accounts cho parents
INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified, created_at)
SELECT
    'parent_temp_' || s.id || '@ai4mind.temp' as email,
    '$2b$12$dummyhashfortemporaryparent123456789012345678' as hashed_password,
    COALESCE(s.emergency_contact_name, 'Chưa cập nhật') as full_name,
    'parent' as role,
    false as is_active,
    false as is_verified,
    NOW() as created_at
FROM students s
WHERE s.emergency_contact_name IS NOT NULL
ON CONFLICT (email) DO NOTHING;

-- Tạo parent records
INSERT INTO parents (user_id, phone_number)
SELECT
    u.id as user_id,
    s.emergency_contact_phone as phone_number
FROM students s
JOIN users u ON u.email = 'parent_temp_' || s.id || '@ai4mind.temp'
WHERE s.emergency_contact_name IS NOT NULL
ON CONFLICT (user_id) DO NOTHING;

-- Link students với parents
UPDATE students s
SET emergency_contact_parent_id = p.id
FROM parents p
JOIN users u ON p.user_id = u.id
WHERE u.email = 'parent_temp_' || s.id || '@ai4mind.temp'
  AND s.emergency_contact_name IS NOT NULL;
```

### 4.3. Verify migration thành công:

```sql
-- Check số lượng students đã có parent link
SELECT COUNT(*)
FROM students
WHERE emergency_contact_parent_id IS NOT NULL;

-- Xem chi tiết
SELECT
    s.id as student_id,
    s.student_code,
    u_student.full_name as student_name,
    u_parent.email as parent_email,
    u_parent.full_name as parent_name,
    p.phone_number as parent_phone
FROM students s
LEFT JOIN users u_student ON s.user_id = u_student.id
LEFT JOIN parents p ON s.emergency_contact_parent_id = p.id
LEFT JOIN users u_parent ON p.user_id = u_parent.id
LIMIT 10;
```

---

## 🗑️ BƯỚC 5: Xóa Columns Cũ

### ⚠️ CẢNH BÁO: Chỉ thực hiện sau khi:

- ✅ Đã backup database
- ✅ Đã migrate data thành công
- ✅ Đã verify kỹ càng
- ✅ Backend code đã update xong

### 5.1. Xóa columns cũ:

```sql
ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_name;
ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_phone;
ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_relationship;
```

### 5.2. Verify columns đã bị xóa:

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'students'
  AND column_name LIKE 'emergency_contact%';
```

✅ **Mong đợi:** Chỉ còn `emergency_contact_parent_id`

---

## 🔒 BƯỚC 6 (OPTIONAL): Set NOT NULL Constraint

Sau khi tất cả students đều có `emergency_contact_parent_id`:

```sql
-- Kiểm tra trước
SELECT COUNT(*) FROM students WHERE emergency_contact_parent_id IS NULL;

-- Nếu COUNT = 0, set NOT NULL
ALTER TABLE students
ALTER COLUMN emergency_contact_parent_id SET NOT NULL;
```

---

## 🔄 Rollback (Nếu Có Lỗi)

### Nếu cần quay lại trạng thái ban đầu:

```sql
-- Xóa constraint và column
ALTER TABLE students DROP CONSTRAINT IF EXISTS fk_students_emergency_contact_parent;
DROP INDEX IF EXISTS idx_students_emergency_contact_parent_id;
ALTER TABLE students DROP COLUMN IF EXISTS emergency_contact_parent_id;

-- Restore data từ backup hoặc từ temp parents nếu cần
```

---

## ✅ Checklist Hoàn Thành

- [ ] Đã backup database
- [ ] Đã chạy BƯỚC 1, 2, 3 (thêm column + foreign key)
- [ ] Đã verify column mới tồn tại
- [ ] Đã migrate data cũ (nếu có)
- [ ] Đã verify data migration thành công
- [ ] Đã update backend models (Task 2)
- [ ] Đã update backend schemas (Task 4)
- [ ] Đã test API endpoints
- [ ] ✋ **DỪNG ĐÂY TRƯỚC** - Chỉ xóa columns cũ sau khi mọi thứ hoạt động tốt
- [ ] Đã xóa columns cũ (BƯỚC 5)
- [ ] Đã set NOT NULL constraint (BƯỚC 6 - optional)

---

## 📞 Hỗ Trợ

Nếu gặp lỗi trong quá trình migrate, báo ngay message lỗi để tôi hỗ trợ!

Các lỗi phổ biến:

- **Foreign key violation**: Có parent_id không tồn tại trong bảng parents
- **Permission denied**: Account Supabase không có quyền ALTER TABLE
- **Column already exists**: Migration đã chạy trước đó

---

**Next Steps:** Sau khi hoàn thành BƯỚC 1-3, chuyển sang update backend models! 🚀
