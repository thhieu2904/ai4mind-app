# 🔑 HOW TO GET SUPABASE KEYS

## 📍 QUAN TRỌNG: Bạn CHỈ CẦN 1 PROJECT DUY NHẤT!

**Project hiện tại của bạn:**
- Project ID: `kfltaylgkxyogsfsvcdt`
- Database URL: `postgresql://postgres:AI4Mind2025%40@db.kfltaylgkxyogsfsvcdt.supabase.co:5432/postgres`
- Storage URL: `https://kfltaylgkxyogsfsvcdt.storage.supabase.co`

---

## 🔑 STEP-BY-STEP: Lấy API Keys

### **Step 1: Vào Supabase Dashboard**
```
https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt
```

### **Step 2: Click "Settings" (biểu tượng ⚙️ bên trái)**

### **Step 3: Click "API" trong menu Settings**

### **Step 4: Tìm section "Project API keys"**

Bạn sẽ thấy 2 keys:

#### **1. `anon` / `public` key** (màu xanh)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtmbHRheWxna3h5b2dzZnN2Y2R0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTg3NDU2MjAsImV4cCI6MjAxNDMyMTYyMH0...
```
- Dài ~200-300 ký tự
- Bắt đầu bằng `eyJ...`
- Dùng cho: Client-side (frontend)

#### **2. `service_role` key** (màu đỏ/cam, có icon 🔒)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtmbHRheWxna3h5b2dzZnN2Y2R0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5ODc0NTYyMCwiZXhwIjoyMDE0MzIxNjIwfQ...
```
- Dài ~200-300 ký tự
- Bắt đầu bằng `eyJ...`
- **QUAN TRỌNG:** Đừng share key này! (Có quyền admin)
- Dùng cho: Server-side (backend)

### **Step 5: Click "Copy" và paste vào `.env`**

---

## 📝 CẬP NHẬT FILE `.env`

Sau khi copy 2 keys, update file `.env`:

```bash
# ======================
# SUPABASE CONFIGURATION
# ======================
DATABASE_URL=postgresql://postgres:AI4Mind2025%40@db.kfltaylgkxyogsfsvcdt.supabase.co:5432/postgres
SUPABASE_DATABASE_URL=postgresql://postgres:AI4Mind2025%40@db.kfltaylgkxyogsfsvcdt.supabase.co:5432/postgres
SUPABASE_PROJECT_URL=https://kfltaylgkxyogsfsvcdt.supabase.co

# 👇 PASTE 2 KEYS NÀY
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtmbHRheWxna3h5b2dzZnN2Y2R0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTg3NDU2MjAsImV4cCI6MjAxNDMyMTYyMH0...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtmbHRheWxna3h5b2dzZnN2Y2R0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5ODc0NTYyMCwiZXhwIjoyMDE0MzIxNjIwfQ...

SUPABASE_BUCKET_URL=https://kfltaylgkxyogsfsvcdt.storage.supabase.co/storage/v1/s3
```

---

## ❌ ĐỪNG LÀM NHỮNG ĐIỀU NÀY:

### **1. ĐỪNG tạo project mới!**
```
❌ Project: dtjkmpogiepcqokxgxgn (project khác!)
✅ Project: kfltaylgkxyogsfsvcdt (project hiện tại!)
```

### **2. ĐỪNG dùng nhiều databases!**
```
❌ Database 1: db.kfltaylgkxyogsfsvcdt.supabase.co
❌ Database 2: db.dtjkmpogiepcqokxgxgn.supabase.co
✅ CHỈ 1 database: db.kfltaylgkxyogsfsvcdt.supabase.co
```

### **3. ĐỪNG nhầm S3 keys với API keys!**
```
S3 Keys (for boto3):
  - Access Key ID: 439cef1a56e2b78d464f8b7d58501baa
  - Secret Key: 879e4ef70008d9caccadef93d1837d3717773976...
  
API Keys (for supabase-py):
  - SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  - SUPABASE_SERVICE_ROLE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Chúng ta đang dùng: Supabase SDK → Cần API Keys (eyJ...)!**

---

## ✅ SAU KHI CÓ 2 KEYS:

### **1. Update `.env`** ✅
### **2. Install dependencies:**
```bash
cd ai-service
pip install supabase==2.0.3
```

### **3. Run RLS SQL script:**
- Vào: https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt/sql
- Click "New query"
- Copy all from `database/rls_policies.sql`
- Run it

### **4. Test:**
```bash
# Terminal 1: Start ai-service
cd ai-service
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start voice-service
cd voice-service
uvicorn app.main:app --reload --port 8001

# Terminal 3: Test API
curl http://localhost:8000/api/v1/voice-analysis/test
```

---

## 🎯 TÓM TẮT:

```
Bạn CẦN:
  ✅ 1 Supabase Project (kfltaylgkxyogsfsvcdt)
  ✅ 1 PostgreSQL Database (đã có!)
  ✅ 1 Storage bucket (đã có!)
  ✅ 2 API Keys (ANON + SERVICE_ROLE) ← CHỈ THIẾU CÁI NÀY!

Bạn KHÔNG CẦN:
  ❌ Project thứ 2
  ❌ Database thứ 2
  ❌ S3 keys (có thể dùng nhưng không cần thiết)
```

---

## 📸 SCREENSHOT REFERENCE:

Trong Supabase Dashboard, keys sẽ trông như này:

```
Project API keys
────────────────────────────────────────────────────

🔑 anon / public
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   [Copy]

🔒 service_role (⚠️ Never share this!)
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   [Copy]
```

---

## 💡 NẾU GẶP KHÓ KHĂN:

1. **Không tìm thấy keys?**
   - Vào: Settings → API → Project API keys

2. **Keys không work?**
   - Check project ID trong URL
   - Đảm bảo đang dùng đúng project (kfltaylgkxyogsfsvcdt)

3. **Vẫn không được?**
   - Screenshot section "Project API keys" và gửi cho mình
   - Hoặc copy cả 2 keys và paste vào `.env`

---

**Ready to continue? Copy 2 keys và paste vào `.env` là xong! 🚀**
