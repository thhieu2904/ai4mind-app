# 🗄️ SUPABASE STORAGE POLICIES SETUP

**Date**: October 2, 2025  
**Bucket**: `audio-files`

---

## ⚠️ QUAN TRỌNG:

Storage policies **KHÔNG THỂ** tạo qua SQL Editor!  
Phải tạo qua **Supabase Storage Dashboard**!

---

## 📍 STEP-BY-STEP GUIDE:

### **Step 1: Mở Storage Dashboard**

URL: https://supabase.com/dashboard/project/kfltaylgkxyogsfsvcdt/storage/buckets

---

### **Step 2: Tạo bucket (nếu chưa có)**

1. Click **"New bucket"**
2. **Name**: `audio-files`
3. **Public**: ❌ **UNCHECK** (Private bucket!)
4. **File size limit**: 50 MB
5. Click **"Create bucket"**

---

### **Step 3: Vào Policies của bucket**

1. Click vào bucket **`audio-files`**
2. Click tab **"Policies"** (bên cạnh "Explorer")
3. Click **"New policy"**

---

### **Step 4: Tạo Policy 1 - Students can SELECT own files**

**Click**: "Create a policy from scratch"

**Policy details:**

- **Policy name**: `Students can view own audio files`
- **Allowed operation**: `SELECT` ✅
- **Target roles**: `authenticated` ✅
- **USING expression**:
  ```sql
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
  )
  ```

**Click**: "Review" → "Save policy"

---

### **Step 5: Tạo Policy 2 - Students can INSERT own files**

**Click**: "New policy" → "Create a policy from scratch"

**Policy details:**

- **Policy name**: `Students can upload to own folder`
- **Allowed operation**: `INSERT` ✅
- **Target roles**: `authenticated` ✅
- **WITH CHECK expression**:
  ```sql
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
  )
  ```

**Click**: "Review" → "Save policy"

---

### **Step 6: Tạo Policy 3 - Students can DELETE own files**

**Click**: "New policy" → "Create a policy from scratch"

**Policy details:**

- **Policy name**: `Students can delete own audio files`
- **Allowed operation**: `DELETE` ✅
- **Target roles**: `authenticated` ✅
- **USING expression**:
  ```sql
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
  )
  ```

**Click**: "Review" → "Save policy"

---

### **Step 7: Tạo Policy 4 - Service role full access**

**Click**: "New policy" → "Create a policy from scratch"

**Policy details:**

- **Policy name**: `Service role full access`
- **Allowed operation**: `All` ✅ (SELECT, INSERT, UPDATE, DELETE)
- **Target roles**: `service_role` ✅
- **USING expression**: `true`
- **WITH CHECK expression**: `true`

**Click**: "Review" → "Save policy"

---

## ✅ VERIFICATION:

Sau khi tạo xong, bạn sẽ thấy **4 policies**:

```
Policies for audio-files bucket:

1. ✅ Students can view own audio files (SELECT)
   - Target: authenticated
   - USING: (storage.foldername(name))[1] IN (...)

2. ✅ Students can upload to own folder (INSERT)
   - Target: authenticated
   - WITH CHECK: (storage.foldername(name))[1] IN (...)

3. ✅ Students can delete own audio files (DELETE)
   - Target: authenticated
   - USING: (storage.foldername(name))[1] IN (...)

4. ✅ Service role full access (ALL)
   - Target: service_role
   - USING: true
```

---

## 🎯 TẠI SAO PHẢI LÀM THẾ NÀY?

**Lý do:**

- ❌ Không thể chạy `ALTER TABLE storage.objects` trong SQL Editor
- ❌ Sẽ báo lỗi: `ERROR: must be owner of table objects`
- ✅ Phải tạo policies qua Storage Dashboard UI

**Security:**

- ✅ Students chỉ access được files trong folder của mình
- ✅ File path: `{student_id}/{filename}.wav`
- ✅ Service role có full access (cho API server)

---

## 📸 SCREENSHOT REFERENCE:

```
┌─────────────────────────────────────────┐
│  Supabase Dashboard                     │
├─────────────────────────────────────────┤
│  Storage → Buckets → audio-files        │
│                                          │
│  [Explorer] [Policies] [Configuration]  │
│              ↑                           │
│         Click here!                      │
├─────────────────────────────────────────┤
│  Policies                                │
│  ┌───────────────────────────────────┐  │
│  │ [+ New policy]                    │  │
│  │                                   │  │
│  │ 1. Students can view own...       │  │
│  │ 2. Students can upload to...      │  │
│  │ 3. Students can delete own...     │  │
│  │ 4. Service role full access       │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 💡 GIẢI THÍCH POLICY:

### **Policy Logic:**

```sql
(storage.foldername(name))[1] IN (
  SELECT id::text FROM students WHERE user_id = (auth.jwt() ->> 'sub')::integer
)
```

**Nghĩa là:**

1. `name` = full file path: `1/audio_123.wav`
2. `storage.foldername(name)` = split path: `['1', 'audio_123.wav']`
3. `[1]` = get first part: `'1'` (student_id)
4. Check nếu `'1'` IN (list student IDs của user hiện tại)
5. ✅ Nếu match → Allow access
6. ❌ Nếu không match → Deny access

---

## 🚨 LƯU Ý:

1. **KHÔNG** tạo policies qua SQL Editor!
2. **PHẢI** tạo qua Storage Dashboard UI!
3. Bucket phải là **Private** (không check "Public")!
4. Service role key **KHÔNG** được expose ra client!

---

## ⏭️ AFTER SETUP:

Sau khi tạo xong 4 policies, bạn có thể:

1. ✅ Chạy SQL cho database tables
2. ✅ Start ai-service và voice-service
3. ✅ Test security implementation

---

**Status**: Ready to create storage policies via Dashboard! 🚀
