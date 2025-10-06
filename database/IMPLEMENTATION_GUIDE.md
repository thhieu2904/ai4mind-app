# 🚀 HƯỚNG DẪN THỰC HIỆN MIGRATION - STEP BY STEP

**Ngày bắt đầu:** 7 tháng 10, 2025  
**Ước tính thời gian:** 2-3 giờ cho Phase 1

---

## ✅ CHECKLIST NHANH

- [ ] **Step 1:** Backup database ✅ (10 phút)
- [ ] **Step 2:** Tạo git branch ✅ (2 phút)
- [ ] **Step 3:** Update backend code ✅ (30 phút)
- [ ] **Step 4:** Test locally ✅ (10 phút)
- [ ] **Step 5:** Chạy migrations trên production ✅ (30-60 phút)
- [ ] **Step 6:** Deploy code mới ✅ (10 phút)
- [ ] **Step 7:** Verify và monitor ✅ (30 phút)

---

## 📝 STEP 1: BACKUP DATABASE (10 phút)

### Option A: Sử dụng Supabase Dashboard (Dễ nhất)

1. Mở Supabase Dashboard: https://supabase.com/dashboard
2. Chọn project của bạn
3. Vào **Database** → **Backups**
4. Click **Create backup** hoặc download backup gần nhất

### Option B: Sử dụng pg_dump (Khuyến nghị)

```powershell
# 1. Lấy connection string từ Supabase
# Dashboard → Settings → Database → Connection string

# 2. Set biến môi trường
$env:PGPASSWORD = "your-database-password"
$SUPABASE_HOST = "db.your-project-ref.supabase.co"
$SUPABASE_USER = "postgres"
$SUPABASE_DB = "postgres"

# 3. Tạo backup
$BackupFile = "backup_before_migration_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
Write-Host "Creating backup: $BackupFile" -ForegroundColor Cyan

pg_dump -h $SUPABASE_HOST -U $SUPABASE_USER -d $SUPABASE_DB > $BackupFile

# 4. Verify backup
if (Test-Path $BackupFile) {
    $size = (Get-Item $BackupFile).Length / 1MB
    Write-Host "✅ Backup created successfully: $([math]::Round($size, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "❌ Backup failed!" -ForegroundColor Red
    exit 1
}

# 5. Upload backup to safe location (Google Drive, Dropbox, etc.)
Write-Host "⚠️ Remember to copy backup to a safe location!" -ForegroundColor Yellow
```

**✅ CHECKPOINT 1:** Bạn đã có file backup? → **Thông báo cho tôi!**

---

## 📝 STEP 2: TẠO GIT BRANCH (2 phút)

```powershell
cd D:\job\ai4mind-app

# Commit current work
git add .
git status
git commit -m "docs: Add database improvement documentation"

# Create new branch
git checkout -b database-improvement-phase1
git push -u origin database-improvement-phase1

Write-Host "✅ Branch created: database-improvement-phase1" -ForegroundColor Green
```

**✅ CHECKPOINT 2:** Branch đã tạo? → **Thông báo cho tôi!**

---

## 📝 STEP 3: UPDATE BACKEND CODE (30 phút)

### 3.1: Tạo file để track changes

```powershell
# File để log changes
$ChangesLog = "database\code_changes_log.txt"
"=== CODE CHANGES LOG ===" | Out-File $ChangesLog
"Started: $(Get-Date)" | Out-File $ChangesLog -Append
"" | Out-File $ChangesLog -Append
```

### 3.2: Update Models (Integer → BigInteger)

Tôi sẽ tạo một script PowerShell để tự động update:

```powershell
# File: update-models.ps1
$files = @(
    "ai-service\app\models\user.py",
    "ai-service\app\models\student.py",
    "ai-service\app\models\parent.py",
    "ai-service\app\models\counselor.py",
    "ai-service\app\models\assessment.py",
    "ai-service\app\models\voice_analysis.py",
    "ai-service\app\models\conversation.py",
    "ai-service\app\models\ai_chat.py",
    "ai-service\app\models\counselor_chat.py"
)

foreach ($file in $files) {
    $fullPath = "D:\job\ai4mind-app\$file"

    if (Test-Path $fullPath) {
        Write-Host "Updating: $file" -ForegroundColor Cyan

        # Backup original
        Copy-Item $fullPath "$fullPath.backup"

        # Read content
        $content = Get-Content $fullPath -Raw

        # Replace Integer with BigInteger in imports
        $content = $content -replace 'from sqlalchemy import Column, Integer,', 'from sqlalchemy import Column, Integer, BigInteger,'
        $content = $content -replace 'from sqlalchemy import Column, Integer ', 'from sqlalchemy import Column, Integer, BigInteger '

        # Replace Integer columns (but keep years_of_experience as Integer)
        $content = $content -replace '(\s+id = Column\()Integer(, primary_key=True)', '$1BigInteger$2'
        $content = $content -replace '(\s+user_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+student_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+parent_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+counselor_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+assessment_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+conversation_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+voice_analysis_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'
        $content = $content -replace '(\s+emergency_contact_parent_id = Column\()Integer(, ForeignKey)', '$1BigInteger$2'

        # Write back
        $content | Out-File $fullPath -Encoding UTF8 -NoNewline

        Write-Host "  ✅ Updated" -ForegroundColor Green
    }
}

Write-Host "`n✅ All model files updated!" -ForegroundColor Green
Write-Host "⚠️ Please review changes manually" -ForegroundColor Yellow
```

**HOẶC** tôi sẽ giúp bạn update từng file:

**✅ CHECKPOINT 3A:** Bạn muốn tôi tạo script tự động hay update từng file thủ công? → **Thông báo cho tôi!**

### 3.3: Add Timestamps to Models

Cần thêm timestamps vào:

- `counselor.py`
- `parent.py` (ParentConsent)
- `counselor_chat.py` (CounselorConversation)

**✅ CHECKPOINT 3B:** Hoàn thành update models? → **Thông báo cho tôi!**

---

## 📝 STEP 4: TEST LOCALLY (10 phút)

```powershell
cd ai-service

# Activate conda environment
conda activate ai4mind-ai-service

# Test imports
python -c "from app.models import User, Student, Assessment; print('✅ Models import OK')"

# Run tests nếu có
# pytest tests/ -v

Write-Host "✅ Local testing passed" -ForegroundColor Green
```

**✅ CHECKPOINT 4:** Tests pass? → **Thông báo cho tôi!**

---

## 📝 STEP 5: CHẠY MIGRATIONS (30-60 phút)

### ⚠️ QUAN TRỌNG: Schedule maintenance window

**Thời gian đề xuất:**

- Cuối tuần (2-5am Sunday)
- Hoặc giờ ít traffic nhất

### 5.1: Migration 001 - Add Indices (10 phút)

```powershell
# Connect to database
$env:PGPASSWORD = "your-password"
$SUPABASE_HOST = "db.your-project.supabase.co"

# Run migration
Write-Host "Running Migration 001: Add Indices..." -ForegroundColor Cyan
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\001_add_indices.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration 001 completed" -ForegroundColor Green
} else {
    Write-Host "❌ Migration 001 failed!" -ForegroundColor Red
    exit 1
}
```

**✅ CHECKPOINT 5A:** Migration 001 thành công? → **Thông báo cho tôi!**

### 5.2: Migration 002 - Add Timestamps (5 phút)

```powershell
Write-Host "Running Migration 002: Add Timestamps..." -ForegroundColor Cyan
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\002_add_timestamps.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration 002 completed" -ForegroundColor Green
} else {
    Write-Host "❌ Migration 002 failed!" -ForegroundColor Red
    exit 1
}
```

**✅ CHECKPOINT 5B:** Migration 002 thành công? → **Thông báo cho tôi!**

### 5.3: Migration 003 - Migrate IDs to BIGINT (30-45 phút)

**⚠️ DOWNTIME REQUIRED - 2-3 hours**

```powershell
Write-Host "⚠️⚠️⚠️ CRITICAL MIGRATION - REQUIRES DOWNTIME ⚠️⚠️⚠️" -ForegroundColor Red
Write-Host "This migration will take 30-60 minutes" -ForegroundColor Yellow
Write-Host "Application should be in maintenance mode" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Type 'YES' to continue"

if ($confirm -ne "YES") {
    Write-Host "❌ Migration cancelled" -ForegroundColor Red
    exit 0
}

# Enable maintenance mode (if applicable)
# ...

Write-Host "Running Migration 003: Migrate IDs to BIGINT..." -ForegroundColor Cyan
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\003_migrate_ids_to_bigint.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration 003 completed" -ForegroundColor Green
} else {
    Write-Host "❌ Migration 003 failed! RESTORE BACKUP IMMEDIATELY!" -ForegroundColor Red
    exit 1
}
```

**✅ CHECKPOINT 5C:** Migration 003 thành công? → **Thông báo cho tôi NGAY!**

### 5.4: Migration 004 - Add CHECK Constraints (10 phút)

```powershell
Write-Host "Running Migration 004: Add CHECK Constraints..." -ForegroundColor Cyan
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\004_add_check_constraints.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration 004 completed" -ForegroundColor Green
} else {
    Write-Host "❌ Migration 004 failed!" -ForegroundColor Red
    exit 1
}
```

**✅ CHECKPOINT 5D:** Migration 004 thành công? → **Thông báo cho tôi!**

---

## 📝 STEP 6: DEPLOY CODE MỚI (10 phút)

```powershell
# Commit changes
git add .
git commit -m "feat: Update models for BIGINT IDs and add timestamps"
git push origin database-improvement-phase1

# Create PR
Write-Host "Create Pull Request on GitHub" -ForegroundColor Cyan
Write-Host "Title: Database Improvement Phase 1 - BIGINT Migration" -ForegroundColor Yellow
Write-Host "Review changes and merge to main" -ForegroundColor Yellow

# Sau khi merge, deploy to production
# (Depends on your deployment process)
```

**✅ CHECKPOINT 6:** Code deployed? → **Thông báo cho tôi!**

---

## 📝 STEP 7: VERIFY & MONITOR (30 phút)

### 7.1: Verify Database

```powershell
# Check all IDs are BIGINT
psql -h $SUPABASE_HOST -U postgres -d postgres -c "
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND column_name LIKE '%id%'
ORDER BY table_name, column_name;
"

# Check indices
psql -h $SUPABASE_HOST -U postgres -d postgres -c "
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public' AND indexname LIKE 'idx_%'
ORDER BY tablename;
"

# Check constraints
psql -h $SUPABASE_HOST -U postgres -d postgres -c "
SELECT conname, conrelid::regclass
FROM pg_constraint
WHERE conname LIKE 'check_%'
ORDER BY conrelid::regclass;
"
```

### 7.2: Test Application

- [ ] User registration works
- [ ] Student login works
- [ ] Create assessment works
- [ ] Voice analysis upload works
- [ ] AI chat works
- [ ] Counselor conversations work
- [ ] No errors in logs

### 7.3: Monitor Performance

- [ ] Query times improved
- [ ] No spike in errors
- [ ] Database CPU/memory normal
- [ ] User experience smooth

**✅ CHECKPOINT 7:** Tất cả đều OK? → **Thông báo cho tôi!**

---

## 🎉 COMPLETION

Khi tất cả checkpoints đều ✅:

```powershell
# Log completion
"" | Out-File $ChangesLog -Append
"=== MIGRATION COMPLETED ===" | Out-File $ChangesLog -Append
"Completed: $(Get-Date)" | Out-File $ChangesLog -Append
"Status: SUCCESS" | Out-File $ChangesLog -Append

Write-Host ""
Write-Host "🎉🎉🎉 MIGRATION COMPLETED SUCCESSFULLY! 🎉🎉🎉" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Monitor application for 24-48 hours"
Write-Host "2. Collect performance metrics"
Write-Host "3. Plan Phase 2 if needed"
Write-Host ""
```

---

## 🚨 ROLLBACK PLAN (Nếu có vấn đề)

### Quick Rollback

```powershell
# Option 1: Run rollback scripts
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\004_add_check_constraints_rollback.sql"
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\002_add_timestamps_rollback.sql"
psql -h $SUPABASE_HOST -U postgres -d postgres -f "database\migrations\001_add_indices_rollback.sql"

# Option 2: Restore from backup (Migration 003 không thể rollback)
psql -h $SUPABASE_HOST -U postgres -d postgres < $BackupFile

# Revert code
git revert HEAD
git push origin database-improvement-phase1
```

---

## 📞 CONTACT

**Trong quá trình thực hiện:**

- Thông báo cho tôi sau mỗi CHECKPOINT
- Nếu gặp lỗi, STOP ngay và thông báo cho tôi
- Đừng skip bất kỳ bước nào

**Tôi sẽ:**

- Hỗ trợ real-time trong quá trình migration
- Giúp debug nếu có lỗi
- Verify kết quả cùng bạn

---

**🚀 SẴN SÀNG BẮT ĐẦU?**

Hãy bắt đầu từ **STEP 1: BACKUP DATABASE** và thông báo cho tôi sau khi hoàn thành!
