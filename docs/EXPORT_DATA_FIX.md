# Export Data Fix Summary

## ✅ Issues Fixed:

### 1. **Rating Form - ENV Variable** ✅

**Problem:** Hard-coded Google Form URL  
**Fix:** Sử dụng `import.meta.env.VITE_GOOGLE_FORM_URL` từ `.env`

**File:** `frontend/src/pages/RatingPage/RatingPage.tsx`

```tsx
// Before:
const googleFormUrl =
  "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform?embedded=true";

// After:
const googleFormUrl = import.meta.env.VITE_GOOGLE_FORM_URL;
```

### 2. **Rating Form - Layout Improvements** ✅

**Changes:**

- ✅ Container: `md` → `lg` (wider)
- ✅ iframe height: Fixed `800px` → Dynamic `calc(100vh - 250px)` (responsive)
- ✅ Min height: Added `600px` (scrollable trên mobile)
- ✅ Title: Added gradient color effect
- ✅ iframe style: Added `display: block` để tránh white space

**Result:** Form giờ chiếm full màn hình, dễ nhìn, có thể scroll thoải mái

---

### 3. **Export Data - API URL Fix** ✅

**Problem:** Wrong env variable name  
**Fix:** `VITE_API_BASE_URL` → `VITE_API_URL`

**File:** `frontend/src/components/layout/Header/Header.tsx`

```tsx
// Before:
`${import.meta.env.VITE_API_BASE_URL}/api/v1/export/user-data`// After:
`${import.meta.env.VITE_API_URL}/api/v1/export/user-data`;
```

### 4. **Export Data - Empty Data Handling** ✅

**Problem:** Excel file rỗng khi user chưa có data  
**Fix:** Tạo placeholder rows cho empty sheets

**File:** `ai-service/app/api/v1/endpoints/export.py`

**Before:**

```python
# Sheets only created if data exists
if assessments_data:
    df_assessments.to_excel(...)
# → Result: Missing sheets nếu không có data
```

**After:**

```python
# Always create all 5 sheets, show "Chưa có dữ liệu" if empty
if assessments_data:
    df_assessments = pd.DataFrame(assessments_data)
else:
    df_assessments = pd.DataFrame([{
        "Ngày đánh giá": "Chưa có dữ liệu",
        "Tổng điểm": "",
        ...
    }])
df_assessments.to_excel(...)
```

**Result:** Excel file luôn có đầy đủ 5 sheets, dễ hiểu hơn

### 5. **Export Data - Better Error Handling** ✅

**Improvements:**

- ✅ Added logging với `logger.info()` và `logger.error()`
- ✅ Better error messages in frontend alert
- ✅ Console log error response từ backend
- ✅ Success notification sau khi download

**File:** `frontend/src/components/layout/Header/Header.tsx`

```tsx
// Better error handling
if (!response.ok) {
  const errorText = await response.text();
  console.error("Export error response:", errorText);
  throw new Error(`Export failed: ${response.status}`);
}

// Success notification
alert("✅ Đã xuất dữ liệu thành công!");
```

---

## 🧪 Testing:

### Quick Test Script

**File:** `scripts/test_export.py`

**Usage:**

```bash
# 1. Get your access token
# - Login to app in browser
# - Open DevTools (F12) → Console
# - Run: localStorage.getItem('access_token')

# 2. Update ACCESS_TOKEN in test_export.py

# 3. Run test
python scripts/test_export.py
```

**Expected Output:**

```
🧪 Testing Export Endpoint...
Status Code: 200
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Length: 12345 bytes

✅ SUCCESS! File saved as: test_export.xlsx
📊 Please open test_export.xlsx to verify the data
```

---

## 🚀 How to Test in Browser:

### 1. Start Backend:

```bash
cd ai-service
uvicorn app.main:app --reload
```

### 2. Start Frontend:

```bash
cd frontend
npm run dev
```

### 3. Test Flow:

1. ✅ Login as a student
2. ✅ Click user icon (top right) → Dropdown menu appears
3. ✅ Click "Đánh giá ứng dụng" → Rating page opens with Google Form
4. ✅ Check form is full-width and scrollable
5. ✅ Go back, click user icon again
6. ✅ Click "Xuất dữ liệu cá nhân" → Excel file downloads
7. ✅ Open Excel file → Should have 5 sheets
8. ✅ Check data in each sheet (or "Chưa có dữ liệu" if empty)

---

## 📊 Excel File Structure:

### Sheet 1: Thông tin cá nhân

- Always has data (user profile)

### Sheet 2: Lịch sử đánh giá

- Shows assessment history
- Or "Chưa có dữ liệu" if none

### Sheet 3: Phân tích giọng nói

- Shows voice analysis records
- Or "Chưa có dữ liệu" if none

### Sheet 4: Lịch sử AI Chat

- Shows all AI conversation messages
- Or "Chưa có dữ liệu" if none

### Sheet 5: Thống kê tổng quan

- Always has data (summary statistics)
- Shows counts even if 0

---

## 🔍 Debugging Tips:

### If export still fails:

1. **Check Backend Logs:**

```bash
# Look for errors in terminal where backend is running
# Should see:
# INFO:     127.0.0.1:xxxx - "GET /api/v1/export/user-data HTTP/1.1" 200 OK
```

2. **Check Frontend Console:**

```javascript
// Open DevTools (F12) → Console
// Look for errors when clicking "Xuất dữ liệu"
```

3. **Verify Auth Token:**

```javascript
// In browser console:
localStorage.getItem("access_token");
// Should return a valid JWT token
```

4. **Test API Directly:**

```bash
# Using curl:
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/export/user-data \
     --output test.xlsx
```

---

## ✨ Summary:

| Issue                      | Status   | Fix                    |
| -------------------------- | -------- | ---------------------- |
| Rating form hard-coded URL | ✅ Fixed | Use env variable       |
| Rating form too small      | ✅ Fixed | Dynamic height + wider |
| Export wrong API URL       | ✅ Fixed | Use VITE_API_URL       |
| Export empty data crash    | ✅ Fixed | Placeholder rows       |
| Export no error handling   | ✅ Fixed | Better logs + alerts   |

**All fixed!** Giờ test thử nhé! 🎉
