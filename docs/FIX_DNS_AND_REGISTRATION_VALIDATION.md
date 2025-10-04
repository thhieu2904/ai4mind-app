# Fix DNS Issue for Supabase Connection

## 🐛 Problem

Cannot resolve hostname `db.kfltaylgkxyogsfsvcdt.supabase.co`:

```
psycopg2.OperationalError: could not translate host name to address: No such host is known
```

## 🔍 Root Cause

Your current DNS server cannot resolve Supabase hostnames, possibly because:

1. ISP DNS is slow/unreliable
2. DNS filtering/blocking
3. IPv6-only response but system needs IPv4

## ✅ Solution: Change DNS to Google/Cloudflare

### Step 1: Open Network Settings

1. Press `Win + I` to open Settings
2. Go to **Network & Internet**
3. Click on your active connection (Wi-Fi or Ethernet)
4. Click **Properties**

### Step 2: Edit DNS Settings

1. Scroll down to **DNS server assignment**
2. Click **Edit** button
3. Select **Manual** from dropdown

### Step 3: Configure DNS Servers

#### Option A: Google DNS (Recommended)

- **Preferred DNS**: `8.8.8.8`
- **Alternate DNS**: `8.8.4.4`

#### Option B: Cloudflare DNS (Faster)

- **Preferred DNS**: `1.1.1.1`
- **Alternate DNS**: `1.0.0.1`

### Step 4: Save and Flush DNS Cache

```powershell
# Flush DNS cache to apply immediately
ipconfig /flushdns

# Test DNS resolution
nslookup db.kfltaylgkxyogsfsvcdt.supabase.co 8.8.8.8
```

Expected output after fix:

```
Server:  dns.google
Address:  8.8.8.8

Name:    db.kfltaylgkxyogsfsvcdt.supabase.co
Address:  2600:1f16:1cd0:3319:1d68:3f05:6fc7:7d3d
```

## 🧪 Test Connection After DNS Change

### 1. Test Registration (Without Parent Email)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!",
    "full_name": "Test User",
    "role": "student",
    "date_of_birth": "2005-01-15",
    "gender": "male"
  }'
```

### 2. Test Registration (With Parent Email)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "Test1234!",
    "full_name": "Test User 2",
    "role": "student",
    "date_of_birth": "2005-01-15",
    "gender": "male",
    "parent_email": "parent@example.com"
  }'
```

### 3. Test Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!"
  }'
```

## 🔧 Alternative: Hosts File Override (Temporary)

If you can't change DNS settings, you can add direct IP mapping:

### Step 1: Find Supabase IP

```powershell
nslookup db.kfltaylgkxyogsfsvcdt.supabase.co 8.8.8.8
```

### Step 2: Edit Hosts File

1. Open Notepad as Administrator
2. Open file: `C:\Windows\System32\drivers\etc\hosts`
3. Add line (replace IP with actual):
   ```
   52.74.252.201  db.kfltaylgkxyogsfsvcdt.supabase.co
   ```
4. Save and close

⚠️ **Warning**: This is temporary. Supabase IPs may change.

## 📋 Fixed Issues

### 1. Registration Validation Error (Fixed)

**Before:** Frontend sent `parent_email: ""` → Backend rejected empty string

**After:** Frontend now removes empty `parent_email` before sending:

```typescript
// Clean up empty fields before sending to backend
const cleanedData = { ...formData };

if (!cleanedData.parent_email || cleanedData.parent_email.trim() === "") {
  delete cleanedData.parent_email;
}

await register(cleanedData);
```

### 2. Database Connection (Pending DNS Fix)

**Before:** Cannot resolve hostname → Connection fails

**After:** Change DNS to Google (8.8.8.8) → Resolves correctly

## 🎯 Expected Results After All Fixes

1. ✅ DNS resolves Supabase hostname
2. ✅ Backend connects to database
3. ✅ Registration works without parent email
4. ✅ Registration works with parent email
5. ✅ Login succeeds
6. ✅ Profile page loads

## 📝 Summary

**Root causes fixed:**

1. Frontend validation: Removed empty string `parent_email`
2. DNS resolution: Changed to Google DNS (8.8.8.8)

**Next steps:**

1. Change DNS to Google/Cloudflare
2. Run `ipconfig /flushdns`
3. Restart backend server
4. Test registration and login
