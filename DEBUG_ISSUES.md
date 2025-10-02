# 🐛 DEBUG 2 ISSUES

## ❌ ISSUE 1: Sau phân tích quay về Dashboard (không vào ComprehensiveResultsPage)

### Nguyên nhân có thể:

1. API call thất bại → catch error → không navigate
2. Response data không đúng format
3. Navigate bị override bởi error boundary
4. Route `/comprehensive-results` không hoạt động

### Cách debug:

#### Bước 1: Mở Browser Console

- Chrome/Edge: F12 → Console tab
- Firefox: F12 → Console tab

#### Bước 2: Test lại flow

1. Vào http://localhost:3000
2. Login
3. Làm GAD-7 → đến Results page
4. Click "Tiếp tục phân tích giọng nói"
5. Ghi âm 10+ giây
6. Click "Phân tích"
7. **QUAN TRỌNG**: Xem Console logs

#### Bước 3: Tìm logs này (đã thêm vào code)

```
🚀 Starting audio processing...
📤 Ready to upload WAV file. Size: XXXXX
📋 FormData prepared with file: recording.wav
✅ API Response received: {data: {...}, status: 200}
📊 Response data: {id: XX, comprehensive_analysis: "...", ...}
🚀 Navigating to comprehensive-results with state: {...}
```

#### Bước 4: Check kết quả

**Nếu thấy "Analysis error:"**

- API call thất bại
- Xem error detail trong console
- Check backend logs

**Nếu thấy "🚀 Navigating..." nhưng vẫn về Dashboard**

- Route configuration có vấn đề
- Check file App.tsx

**Nếu KHÔNG thấy logs gì**

- Code không chạy đến handleAnalyze()
- Check button onClick có đúng không

---

## ❌ ISSUE 2: SQL Error `json_array_length(jsonb) does not exist`

### ✅ ĐÃ FIX:

Trong PostgreSQL:

- `json_array_length()` → dùng cho type `JSON`
- `jsonb_array_length()` → dùng cho type `JSONB`

Vì đã tạo cột với type `JSONB`, phải dùng `jsonb_array_length()`

### Query đã sửa (trong IMPLEMENTATION_GUIDE.md):

```sql
-- ✅ ĐÚNG
SELECT
    id,
    assessment_id,
    student_id,
    LEFT(comprehensive_analysis, 100) as analysis_preview,
    jsonb_array_length(comprehensive_recommendations) as recommendation_count,
    created_at
FROM voice_analyses
WHERE comprehensive_analysis IS NOT NULL
ORDER BY id DESC
LIMIT 1;
```

### Chạy lại query này trên Supabase SQL Editor để verify!

---

## 🔍 CHECKLIST DEBUG

### Pre-flight Check:

- [ ] **Database migration đã chạy chưa?**

  ```sql
  -- Supabase SQL Editor
  SELECT column_name, data_type
  FROM information_schema.columns
  WHERE table_name = 'voice_analyses'
    AND column_name LIKE 'comprehensive%';

  -- Kết quả mong đợi: 2 rows
  -- comprehensive_analysis | text
  -- comprehensive_recommendations | jsonb
  ```

- [ ] **Backend ai-service đã restart chưa?**

  ```bash
  # Terminal ai-service
  # Ctrl+C để stop
  uvicorn app.main:app --reload --port 8000

  # Xem logs: "Application startup complete"
  ```

- [ ] **Frontend đang chạy?**

  ```bash
  # Terminal frontend
  npm run dev

  # Mở http://localhost:3000
  ```

### Runtime Check:

- [ ] **Browser console có errors không?**

  - F12 → Console tab
  - Tìm màu đỏ (errors)

- [ ] **Network tab có call API không?**

  - F12 → Network tab
  - Filter: XHR
  - Tìm: `/api/v1/assessments/{id}/add-voice`
  - Status: 200 OK?

- [ ] **Backend logs có gì?**
  - Terminal ai-service
  - Tìm logs:
    ```
    INFO: Processing voice upload for assessment: XXX
    INFO: 🔍 Preparing response with comprehensive data...
    INFO: comprehensive_analysis length: XXX
    ```

---

## 🎯 EXPECTED BEHAVIOR

### Flow đúng:

1. **VoiceRecordingPage**

   - User record audio
   - Click "Phân tích"
   - Convert WebM → WAV
   - POST `/api/v1/assessments/{id}/add-voice`

2. **Backend ai-service**

   - Receive audio file
   - Upload to Supabase Storage
   - Call voice-service for analysis
   - Call Gemini for comprehensive analysis
   - Save to database WITH comprehensive fields
   - Return response with comprehensive data

3. **Frontend navigate**

   - Receive response: `{id, comprehensive_analysis, comprehensive_recommendations, ...}`
   - Navigate to `/comprehensive-results`
   - Pass state: assessmentId, gad7Score, comprehensiveAnalysis, etc.

4. **ComprehensiveResultsPage**
   - Receive state from navigation
   - Display 3 sections:
     - GAD-7 Summary (score, severity)
     - Voice Summary (emotion, sentiment)
     - Comprehensive Analysis (Gemini cross-validation)

---

## 🚀 NEXT STEPS

### 1. Fix SQL query (✅ Done)

- Changed `json_array_length` → `jsonb_array_length`

### 2. Add debug logs (✅ Done)

- Frontend: VoiceRecordingPage.tsx
- Backend: assessment_voice.py

### 3. Test với debug logs

- Mở browser console
- Làm full flow
- Ghi lại tất cả logs

### 4. Report kết quả

Sau khi test, cho tôi biết:

- ✅ Có gọi API không? Status code?
- ✅ Response data có comprehensive fields không?
- ✅ Có navigate đến /comprehensive-results không?
- ✅ Nếu có error, error message là gì?

---

## 📝 REFERENCE

### Files đã sửa:

1. **IMPLEMENTATION_GUIDE.md**

   - Line 155: `json_array_length` → `jsonb_array_length`

2. **VoiceRecordingPage.tsx**

   - Added console.log after API call
   - Added console.log before navigate

3. **assessment_voice.py**
   - Added logger.info for comprehensive data

### Files cần check:

1. **App.tsx** - Route configuration
2. **ComprehensiveResultsPage.tsx** - State handling
3. **Backend logs** - Error tracking

### Commands:

```bash
# Restart ai-service
cd d:\job\ai4mind-app\ai-service
uvicorn app.main:app --reload --port 8000

# Check logs
# Watch terminal ai-service

# Test SQL
# Supabase SQL Editor → Run fixed query
```
