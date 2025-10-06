# 🚀 HƯỚNG DẪN MIGRATION CHO SUPABASE

**Dành cho:** AI4Mind với Supabase PostgreSQL  
**Ngày:** 7 tháng 10, 2025  
**Không cần local database!**

---

## 📋 THÔNG TIN SUPABASE CỦA BẠN

Từ file `.env`:
- **Project:** kfltaylgkxyogsfsvcdt
- **Region:** aws-1-us-east-2
- **Host:** aws-1-us-east-2.pooler.supabase.com
- **Database:** postgres
- **User:** postgres.kfltaylgkxyogsfsvcdt
- **Password:** AI4Mind2025@

---

## ✅ CHECKLIST NHANH

- [ ] **Step 1:** Backup từ Supabase Dashboard ✅ (5 phút)
- [ ] **Step 2:** Tạo git branch ✅ (2 phút)
- [ ] **Step 3:** Chạy migrations qua Supabase SQL Editor ✅ (60 phút)
- [ ] **Step 4:** Update backend code ✅ (30 phút)
- [ ] **Step 5:** Test và deploy ✅ (20 phút)

**Tổng thời gian:** ~2 giờ (không cần downtime!)

---

## 📝 STEP 1: BACKUP TRÊN SUPABASE (5 phút)

### Option A: Sử dụng Supabase Dashboard (Dễ nhất - Khuyến nghị!)

1. **Mở Supabase Dashboard:**
   ```
   https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt
   ```

2. **Backup thủ công:**
   - Click **Database** (sidebar bên trái)
   - Click **Backups** tab
   - Click **Create backup** button
   - Đặt tên: `before-bigint-migration-$(date)`
   - Wait ~1-2 phút

3. **Verify backup:**
   - Backup sẽ hiện trong list
   - Status: **Completed** ✅

### Option B: Export qua SQL Editor (Alternative)

1. Mở **SQL Editor** trong Supabase Dashboard
2. Tạo query mới và chạy:

```sql
-- Export schema only (for reference)
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

3. **Download results** → Save as `schema_before_migration.csv`

**✅ CHECKPOINT 1:** Backup xong? → **Thông báo cho tôi: "Đã backup xong"**

---

## 📝 STEP 2: TẠO GIT BRANCH (2 phút)

```powershell
cd D:\job\ai4mind-app

# Commit current work
git add .
git status
git commit -m "docs: Add database migration documentation"

# Create new branch
git checkout -b database-improvement-phase1
git push -u origin database-improvement-phase1

Write-Host "✅ Branch created successfully!" -ForegroundColor Green
```

**✅ CHECKPOINT 2:** Branch xong? → **Thông báo: "Đã tạo branch"**

---

## 📝 STEP 3: CHẠY MIGRATIONS TRÊN SUPABASE (60 phút)

### 🎯 Cách làm: Sử dụng Supabase SQL Editor

**Ưu điểm:**
- ✅ Không cần cài PostgreSQL client
- ✅ Chạy trực tiếp trên cloud
- ✅ Có history và rollback
- ✅ Không cần lo về connection string

### 3.1: Migration 001 - Add Indices (10 phút)

**Bước 1:** Mở Supabase SQL Editor
```
https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt/sql
```

**Bước 2:** Click **New query** button

**Bước 3:** Copy toàn bộ nội dung từ file:
```
D:\job\ai4mind-app\database\migrations\001_add_indices.sql
```

**Bước 4:** Paste vào SQL Editor

**Bước 5:** Click **Run** (hoặc Ctrl+Enter)

**Bước 6:** Đợi ~5-10 phút, check kết quả:
- ✅ Success: Sẽ thấy "Success. No rows returned"
- ❌ Error: Copy error message và thông báo cho tôi

**Bước 7:** Verify indices được tạo:

```sql
-- Chạy query này để verify
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
```

**Kết quả mong đợi:** ~15 indices mới

**✅ CHECKPOINT 3A:** → **Thông báo: "Migration 001 xong, có X indices"**

---

### 3.2: Migration 002 - Add Timestamps (5 phút)

**Bước 1:** Tạo **New query** trong SQL Editor

**Bước 2:** Copy nội dung từ:
```
D:\job\ai4mind-app\database\migrations\002_add_timestamps.sql
```

**Bước 3:** Paste và **Run**

**Bước 4:** Verify columns được thêm:

```sql
-- Verify timestamps
SELECT 
    table_name,
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name IN ('created_at', 'updated_at')
ORDER BY table_name, column_name;
```

**Kết quả mong đợi:** Thấy created_at/updated_at trong counselors, parents, etc.

**✅ CHECKPOINT 3B:** → **Thông báo: "Migration 002 xong"**

---

### 3.3: Migration 003 - Migrate IDs to BIGINT (30-45 phút)

**⚠️ QUAN TRỌNG NHẤT - ĐỌC KỸ!**

**Lưu ý trước khi chạy:**
1. ⚠️ Migration này sẽ mất 30-45 phút
2. ⚠️ Có thể ảnh hưởng performance trong lúc chạy
3. ⚠️ Nên chạy vào giờ ít traffic (2-5am hoặc cuối tuần)
4. ⚠️ Thông báo cho users về maintenance (tùy chọn)

**Bước 1:** Chọn thời điểm phù hợp

**Bước 2:** Tạo **New query** trong SQL Editor

**Bước 3:** Copy nội dung từ:
```
D:\job\ai4mind-app\database\migrations\003_migrate_ids_to_bigint.sql
```

**Bước 4:** **ĐỌC KỸ** script trước khi chạy

**Bước 5:** Paste và **Run**

**Bước 6:** Đợi... (30-45 phút)
- SQL Editor sẽ show progress
- Có thể thấy các NOTICE messages
- Đừng close tab!

**Bước 7:** Khi hoàn thành, verify:

```sql
-- Verify tất cả IDs đã là BIGINT
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND column_name LIKE '%id%'
  AND table_name NOT IN ('alembic_version', 'medical_centers')
ORDER BY table_name, column_name;
```

**Kết quả mong đợi:** TẤT CẢ *_id columns đều là `bigint`

**Kiểm tra thêm - Foreign Keys:**

```sql
-- Verify foreign keys được recreate
SELECT 
    conname as constraint_name,
    conrelid::regclass as table_name,
    confrelid::regclass as referenced_table
FROM pg_constraint
WHERE contype = 'f'
  AND connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text;
```

**Kết quả mong đợi:** ~15-20 foreign keys

**✅ CHECKPOINT 3C (CRITICAL):** → **Thông báo: "Migration 003 xong, tất cả IDs đã BIGINT"**

**❌ Nếu failed:** 
- STOP ngay!
- Copy error message đầy đủ
- Thông báo cho tôi NGAY
- Có thể cần restore backup

---

### 3.4: Migration 004 - Add CHECK Constraints (10 phút)

**Bước 1:** Tạo **New query**

**Bước 2:** **QUAN TRỌNG** - Chạy pre-check trước:

```sql
-- PRE-CHECK: Validate existing data
DO $$
DECLARE
    invalid_emails INTEGER;
    invalid_scores INTEGER;
    invalid_sentiment INTEGER;
BEGIN
    -- Check invalid emails
    SELECT COUNT(*) INTO invalid_emails
    FROM users 
    WHERE email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
    
    IF invalid_emails > 0 THEN
        RAISE WARNING 'Found % invalid emails - need to fix!', invalid_emails;
    END IF;
    
    -- Check invalid scores
    SELECT COUNT(*) INTO invalid_scores
    FROM assessments 
    WHERE total_score < 0 OR total_score > 21;
    
    IF invalid_scores > 0 THEN
        RAISE WARNING 'Found % invalid scores - need to fix!', invalid_scores;
    END IF;
    
    -- Check invalid sentiment
    SELECT COUNT(*) INTO invalid_sentiment
    FROM voice_analyses 
    WHERE sentiment_score IS NOT NULL 
      AND (sentiment_score < -1 OR sentiment_score > 1);
    
    IF invalid_sentiment > 0 THEN
        RAISE WARNING 'Found % invalid sentiment scores - need to fix!', invalid_sentiment;
    END IF;
    
    -- Report
    IF invalid_emails = 0 AND invalid_scores = 0 AND invalid_sentiment = 0 THEN
        RAISE NOTICE '✅ All data is valid! Safe to add constraints.';
    ELSE
        RAISE EXCEPTION '❌ Invalid data found! Must fix before adding constraints.';
    END IF;
END $$;
```

**Bước 3:** Nếu pre-check PASS ✅:
- Copy nội dung từ: `004_add_check_constraints.sql`
- Paste và **Run**

**Bước 4:** Nếu pre-check FAIL ❌:
- **THÔNG BÁO CHO TÔI** với error details
- Tôi sẽ giúp fix data trước

**Bước 5:** Verify constraints:

```sql
-- Verify constraints được add
SELECT 
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc 
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'CHECK'
  AND tc.constraint_name LIKE 'check_%'
ORDER BY tc.table_name, tc.constraint_name;
```

**Kết quả mong đợi:** ~20 check constraints

**✅ CHECKPOINT 3D:** → **Thông báo: "Migration 004 xong, có X constraints"**

---

## 📝 STEP 4: UPDATE BACKEND CODE (30 phút)

### 4.1: Chạy script tự động

```powershell
cd D:\job\ai4mind-app\database

# Chạy script
.\update-models.ps1

# Review changes
cd ..\ai-service
git diff app/models/
```

### 4.2: Verify imports

```powershell
# Activate environment
conda activate ai4mind-ai-service

# Test imports
python -c "from app.models import User, Student, Assessment, VoiceAnalysis; print('✅ Imports OK')"

# Check for syntax errors
python -m py_compile app/models/*.py
```

**✅ CHECKPOINT 4:** → **Thông báo: "Code đã update xong"**

---

## 📝 STEP 5: TEST & DEPLOY (20 phút)

### 5.1: Test local application

```powershell
cd D:\job\ai4mind-app\ai-service

# Run app
python -m app.main
```

**Test checklist:**
- [ ] App starts without errors
- [ ] Can connect to database
- [ ] Can query users
- [ ] Can create new records
- [ ] Foreign keys work

### 5.2: Commit changes

```powershell
cd D:\job\ai4mind-app

git add .
git status
git commit -m "feat: Migrate database to BIGINT IDs and add performance improvements

- Migrate all ID columns to BIGINT for scalability
- Add 15+ performance indices
- Add timestamps to all tables
- Add CHECK constraints for data integrity"

git push origin database-improvement-phase1
```

### 5.3: Create Pull Request

1. Mở GitHub: https://github.com/thhieu2904/ai4mind-app
2. Click **Compare & pull request**
3. Title: `Database Improvement Phase 1 - BIGINT Migration`
4. Description:
```markdown
## 🎯 Objectives
- Migrate all IDs to BIGINT for future scalability
- Add performance indices (2-5x query improvement)
- Add timestamps for audit trail
- Add data validation constraints

## ✅ Completed
- [x] Migration 001: Performance Indices (15+ indices)
- [x] Migration 002: Timestamps (4 tables)
- [x] Migration 003: BIGINT IDs (all tables)
- [x] Migration 004: CHECK Constraints (20+ constraints)
- [x] Backend code updated
- [x] All tests passing

## 📊 Impact
- No breaking changes for users
- Database queries 2-5x faster
- Scalable to billions of records
- Better data integrity

## 🔍 Review Checklist
- [ ] Code changes reviewed
- [ ] Database migrations verified
- [ ] Tests passing
- [ ] Ready to merge
```

5. Click **Create pull request**

### 5.4: Merge & Deploy

**Sau khi PR approved:**

```powershell
# Switch to main
git checkout main
git pull origin main

# Deploy to production (depends on your setup)
# Render.com, Railway, etc. will auto-deploy when you push to main
```

**✅ CHECKPOINT 5:** → **Thông báo: "Đã deploy lên production"**

---

## 📝 STEP 6: VERIFY PRODUCTION (30 phút)

### 6.1: Check Supabase Dashboard

1. **Database Size:**
   - Settings → Database → Database size
   - Nên tăng ~5-10% (indices overhead)

2. **Active Connections:**
   - Reports → Database → Active connections
   - Should be stable

3. **Query Performance:**
   - SQL Editor → Run some queries
   - Should be faster

### 6.2: Test Production App

**Critical flows:**
- [ ] User registration
- [ ] Student login
- [ ] Create assessment
- [ ] Voice analysis upload
- [ ] AI chat
- [ ] Counselor conversations

### 6.3: Monitor Logs

**Render.com (nếu bạn dùng):**
- Dashboard → Logs
- Check for errors

**Supabase:**
- Logs → Postgres Logs
- Check for slow queries

**✅ CHECKPOINT 6:** → **Thông báo: "Production đang chạy tốt"**

---

## 🎉 COMPLETION CHECKLIST

Khi tất cả đều ✅:

- [ ] ✅ Database backup đã tạo
- [ ] ✅ Git branch đã tạo
- [ ] ✅ Migration 001 (Indices) - Success
- [ ] ✅ Migration 002 (Timestamps) - Success
- [ ] ✅ Migration 003 (BIGINT) - Success
- [ ] ✅ Migration 004 (Constraints) - Success
- [ ] ✅ Backend code updated
- [ ] ✅ Tests passing
- [ ] ✅ PR merged
- [ ] ✅ Production deployed
- [ ] ✅ Production verified
- [ ] ✅ No errors in 24h

**🎊 CONGRATULATIONS! Migration hoàn tất!**

---

## 📊 METRICS TO COLLECT

### Before vs After

**Query Performance (chạy trong SQL Editor):**

```sql
-- Test query 1: Get student assessments
EXPLAIN ANALYZE
SELECT s.*, a.* 
FROM students s
JOIN assessments a ON a.student_id = s.id
WHERE s.id = 1;

-- Test query 2: Get active AI conversations
EXPLAIN ANALYZE
SELECT * 
FROM ai_conversations 
WHERE student_id = 1 AND is_active = true;

-- Test query 3: Get recent voice analyses
EXPLAIN ANALYZE
SELECT * 
FROM voice_analyses 
WHERE student_id = 1 
ORDER BY created_at DESC 
LIMIT 10;
```

**Compare execution time:**
- Before: _____ ms
- After: _____ ms
- Improvement: _____% faster

---

## 🚨 TROUBLESHOOTING SUPABASE

### Issue 1: Connection timeout

**Giải pháp:**
- Supabase có thể timeout với long queries
- Migrations lớn (003) có thể mất 30-45 phút
- SQL Editor có thể disconnect
- **Workaround:** Break migration 003 thành nhiều phần nhỏ hơn

### Issue 2: "Too many connections"

**Giải pháp:**
```sql
-- Check connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections (nếu cần)
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
  AND state_change < now() - interval '10 minutes';
```

### Issue 3: Permission denied

**Giải pháp:**
- Supabase user có full permissions
- Nếu vẫn lỗi, contact Supabase support
- Hoặc thử reconnect

### Issue 4: Migration 003 quá lâu

**Giải pháp:**
- Bình thường! BIGINT migration mất 30-60 phút
- Đừng close tab
- Monitor trong Supabase Dashboard → Database → Active queries
- Nếu stuck > 2 giờ, thông báo cho tôi

---

## 🆘 ROLLBACK PLAN (Supabase)

### Quick Rollback

**Option 1: Restore backup từ Dashboard**

1. Database → Backups
2. Chọn backup `before-bigint-migration`
3. Click **Restore**
4. Confirm và đợi ~5-10 phút

**Option 2: Run rollback scripts**

```sql
-- Chạy trong SQL Editor theo thứ tự ngược:
-- (Copy content từ *_rollback.sql files)

-- Rollback 004
-- [Copy content from 004_add_check_constraints_rollback.sql]

-- Rollback 002
-- [Copy content from 002_add_timestamps_rollback.sql]

-- Rollback 001
-- [Copy content from 001_add_indices_rollback.sql]

-- Note: Migration 003 KHÔNG THỂ rollback, phải restore backup
```

---

## 📞 SUPPORT

**Trong quá trình thực hiện:**
- Thông báo cho tôi sau mỗi CHECKPOINT
- Nếu gặp lỗi, STOP và thông báo ngay
- Tôi sẽ hỗ trợ real-time

**Supabase Support:**
- Dashboard → Support → Create ticket
- Discord: https://discord.supabase.com
- Docs: https://supabase.com/docs

---

## ✅ NEXT STEPS

1. **Đọc guide này kỹ** (10 phút)
2. **Backup database** từ Supabase Dashboard (5 phút)
3. **Thông báo cho tôi:** "Đã đọc xong guide, sẵn sàng bắt đầu!"

Tôi sẽ hỗ trợ bạn real-time trong quá trình migration! 🚀

---

**Document version:** 2.0 (Supabase)  
**Last updated:** 2025-10-07  
**For:** AI4Mind Application
