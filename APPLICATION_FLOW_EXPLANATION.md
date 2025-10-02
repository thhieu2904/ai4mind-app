# Application Flow - GAD-7 + Voice Analysis

## ✅ Tóm tắt Flow Hiện tại (ĐÚNG)

### Phase 1: GAD-7 Assessment (Phân tích sơ bộ)

```
User → AssessmentPage
  ↓ Submit 7 answers
Backend:
  1. Calculate total_score
  2. Call Gemini.analyze_gad7() ← Chỉ GAD-7 data
  3. Save to assessments table
  4. Return: {id, score, severity, analysis, recommendations}
  ↓
Frontend: ResultsPage
  - Hiển thị: Score, Severity, Phân tích sơ bộ
  - Button: "Phân tích giọng nói ngay"
```

**Kết quả:** Phân tích **đơn lẻ** từ GAD-7 (chủ quan, tự đánh giá)

---

### Phase 2: Voice Analysis (Phân tích tổng hợp)

```
User → VoiceAnalysisPage (select prompt)
  ↓
User → VoiceRecordingPage
  ↓ Record audio + "Phân tích" button
  ↓
Backend: POST /api/v1/assessments/{assessment_id}/add-voice
  │
  ├─ STEP 1: Load Assessment from DB
  │   SELECT * FROM assessments WHERE id = assessment_id
  │   → Get GAD-7 answers, score, severity
  │
  ├─ STEP 2: Upload audio to Supabase Storage
  │   storage.save_audio(file, user_id)
  │   → Get storage_path
  │
  ├─ STEP 3: Call Voice Service
  │   POST http://localhost:8001/api/v1/voice/analyze
  │   FormData: {audio_file, gender, language}
  │   → Get: {
  │       transcript,
  │       audio_features: {pitch, energy, pause_count},
  │       emotion_result: {primary_emotion, confidence},
  │       text_analysis: {sentiment, keywords}
  │     }
  │
  ├─ STEP 4: Call Gemini.analyze_combined() ← Cross-validation!
  │   Input:
  │     - gad7_data: {answers, score, severity}
  │     - voice_data: {transcript, emotions, audio_features}
  │
  │   Gemini AI:
  │     - So sánh GAD-7 (chủ quan) vs Voice (khách quan)
  │     - Phát hiện emotional suppression
  │     - Phát hiện discrepancy (người dùng nói "ok" nhưng giọng lo âu)
  │     - Đưa ra phân tích chính xác hơn
  │
  │   Output:
  │     - comprehensive_analysis (chi tiết, cross-validated)
  │     - comprehensive_recommendations (cá nhân hóa)
  │
  └─ STEP 5: Save VoiceAnalysis to DB
      INSERT INTO voice_analyses (
        student_id,
        assessment_id,  ← Link to GAD-7!
        audio_file_path,
        transcription,
        detected_emotions,
        audio_features,
        sentiment_score,
        comprehensive_analysis,  ← From Gemini
        comprehensive_recommendations  ← From Gemini
      )

  ↓ Return VoiceAnalysisResponse

Frontend: Navigate to ComprehensiveResultsPage
  - Display:
    ✓ GAD-7 Summary (score, severity)
    ✓ Voice Summary (emotion, sentiment)
    ✓ Comprehensive Analysis (AI cross-validation)
    ✓ Comprehensive Recommendations
    ✓ Transcription
```

**Kết quả:** Phân tích **tổng hợp** từ GAD-7 + Voice (chủ quan + khách quan = chính xác hơn)

---

## Database Schema Flow

```sql
-- Phase 1: GAD-7 saved
students (id=51, user_id=56, ...)
  ↓ 1:many
assessments (
  id=26,
  student_id=51,
  answers=[1,1,1,2,1,1,1],
  total_score=8,
  severity_level='mild',
  analysis='...',  ← Gemini analyze_gad7()
  recommendations=['...']
)

-- Phase 2: Voice analysis saved AND linked
voice_analyses (
  id=10,
  student_id=51,
  assessment_id=26,  ← LINK to GAD-7!
  audio_file_path='uploads/user_56/recording_123.webm',
  transcription='Tôi cảm thấy...',
  detected_emotions={'anxiety': 0.85},
  audio_features={'pitch': 180, 'energy': 0.65},
  sentiment_score=-0.3,
  comprehensive_analysis='...',  ← Gemini analyze_combined()
  comprehensive_recommendations=['...']
)
```

---

## Key Differences

| Aspect              | GAD-7 Only (Phase 1)    | GAD-7 + Voice (Phase 2)                |
| ------------------- | ----------------------- | -------------------------------------- |
| **Input**           | 7 câu hỏi tự đánh giá   | GAD-7 + giọng nói + nội dung chia sẻ   |
| **Analysis**        | `Gemini.analyze_gad7()` | `Gemini.analyze_combined()`            |
| **Data type**       | Chủ quan (self-report)  | Chủ quan + Khách quan (voice features) |
| **Accuracy**        | Baseline                | Higher (cross-validation)              |
| **Can detect**      | Triệu chứng tự báo cáo  | Emotional suppression, discrepancy     |
| **Recommendations** | General                 | Personalized based on both data        |
| **Display**         | ResultsPage             | ComprehensiveResultsPage               |

---

## API Endpoints Used

### 1. Submit GAD-7

```http
POST /api/v1/assessments/
Content-Type: application/json
Authorization: Bearer {token}

{
  "answers": [1, 1, 1, 2, 1, 1, 1],
  "functional_impairment": 0,
  "notes": null
}

Response:
{
  "id": 26,
  "student_id": 51,
  "total_score": 8,
  "severity_level": "mild",
  "analysis": "Bạn có mức độ lo âu nhẹ...",
  "recommendations": ["Thực hành thư giãn...", ...],
  "created_at": "2025-10-02T16:10:00Z"
}
```

### 2. Add Voice to Assessment

```http
POST /api/v1/assessments/{assessment_id}/add-voice
Content-Type: multipart/form-data
Authorization: Bearer {token}

FormData:
  - audio_file: Blob (recording.webm)
  - (optional) prompt_id: 1

Response:
{
  "id": 10,
  "student_id": 51,
  "assessment_id": 26,
  "audio_file_path": "uploads/...",
  "transcription": "Tôi cảm thấy lo lắng...",
  "dominant_emotion": "anxiety",
  "sentiment_score": -0.3,
  "processing_status": "completed",
  "created_at": "2025-10-02T16:15:00Z",

  // Comprehensive analysis from Gemini
  "comprehensive_analysis": "Dựa trên đánh giá GAD-7 (8/21 - lo âu nhẹ) và phân tích giọng nói, có sự khác biệt đáng chú ý...",
  "comprehensive_recommendations": [
    "Nên tham khảo tư vấn viên để...",
    "Thực hành kỹ thuật quản lý lo âu..."
  ],

  // Context from GAD-7
  "gad7_score": 8,
  "gad7_severity": "mild"
}
```

---

## Frontend Navigation Flow

```
Dashboard
  ↓ "Làm bài đánh giá"
AssessmentPage (7 questions)
  ↓ Submit
ResultsPage (GAD-7 results)
  ├─ Option 1: "Về trang chủ"
  └─ Option 2: "Phân tích giọng nói" ← Suggested!
      ↓ navigate with: {assessmentId, gad7Score, gad7Severity}
VoiceAnalysisPage (prompts, instructions)
  ↓ "Tiếp tục"
  ↓ navigate with: {assessmentId, gad7Score, gad7Severity, selectedPrompt}
VoiceRecordingPage
  ↓ Record → "Phân tích"
  ↓ POST /add-voice (1 call does everything!)
ComprehensiveResultsPage
  - Display all combined results
  - Options: "Xem chi tiết GAD-7" | "Về trang chủ"
```

---

## ❌ Flow SAI (Bạn mô tả ban đầu)

```
VoiceRecordingPage
  ↓ "Ghi âm" button
  ↓ POST to voice-service only  ❌ SAI!
  ↓ Lưu voice_analysis vào DB
  ↓ User sees results
  ↓ "Phân tích" button
  ↓ POST again to Gemini  ❌ Redundant!
ComprehensiveResultsPage
```

**Vấn đề:**

- 2 lần gọi API (không cần thiết)
- Voice data phải fetch lại từ DB
- Phức tạp hơn, dễ lỗi

---

## ✅ Flow ĐÚNG (Đã implement)

```
VoiceRecordingPage
  ↓ "Phân tích" button (1 lần!)
  ↓ POST /assessments/{id}/add-voice
  ↓ Backend làm TẤT CẢ:
      1. Load GAD-7 from DB
      2. Call voice-service
      3. Call Gemini combine
      4. Save voice_analysis
      5. Return comprehensive results
  ↓
ComprehensiveResultsPage
  - Nhận data từ navigation state
  - Display ngay lập tức
```

**Ưu điểm:**

- ✅ Chỉ 1 request
- ✅ Backend xử lý tất cả logic
- ✅ Frontend đơn giản, chỉ hiển thị
- ✅ Atomic operation (all or nothing)

---

## Gemini AI Role

### Phase 1: `analyze_gad7()`

**Input:**

```json
{
  "answers": [
    {"question": "Cảm thấy lo lắng...", "answer": "Vài ngày", "score": 1},
    ...
  ],
  "total_score": 8
}
```

**Prompt:**

```
Bạn là chuyên gia tâm lý. Sinh viên có GAD-7 score = 8/21 (mild anxiety).
Phân tích tình trạng và đưa ra khuyến nghị.
```

**Output:**

```json
{
  "analysis": "Bạn có mức độ lo âu nhẹ. Các triệu chứng có thể được quản lý...",
  "recommendations": ["Thực hành thư giãn", "Tập thể dục"]
}
```

---

### Phase 2: `analyze_combined()`

**Input:**

```json
{
  "gad7_data": {
    "answers": [...],
    "total_score": 8,
    "severity": "mild"
  },
  "voice_data": {
    "transcript": "Tôi cảm thấy mọi thứ ổn, nhưng đôi khi...",
    "audio_features": {
      "pitch": 180,  // High pitch → stress
      "energy": 0.65,
      "pause_count": 15  // Many pauses → anxiety
    },
    "emotion_result": {
      "primary_emotion": "anxiety",
      "confidence": 0.85
    },
    "text_analysis": {
      "sentiment_score": -0.3,  // Negative
      "keywords": ["lo lắng", "sợ hãi"]
    }
  }
}
```

**Prompt:**

```
Bạn là chuyên gia tâm lý. So sánh 2 nguồn dữ liệu:
1. GAD-7: score=8 (mild) - sinh viên tự báo cáo "lo âu nhẹ"
2. Voice: emotion=anxiety (0.85 confidence), high pitch, many pauses, negative sentiment

Phát hiện discrepancy và đưa ra phân tích chính xác.
```

**Output:**

```json
{
  "analysis": "Có sự khác biệt đáng chú ý giữa tự đánh giá (mild) và phân tích giọng nói (anxiety cao). Điều này có thể cho thấy emotional suppression - sinh viên đang cố gắng che giấu mức độ lo âu thực sự. Giọng nói cho thấy dấu hiệu căng thẳng cao (pitch tăng, nhiều khoảng dừng). Nên gặp tư vấn viên để...",
  "recommendations": [
    "Ưu tiên gặp tư vấn viên trong tuần này",
    "Thực hành kỹ thuật thở sâu khi cảm thấy lo âu",
    "Ghi nhật ký cảm xúc để nhận biết trigger"
  ]
}
```

---

## Summary

### ✅ Những gì ĐÃ ĐÚNG:

1. **GAD-7 Phase:** Submit → Gemini analyze → Save DB → Show results ✅
2. **Voice Phase:** 1 API call làm tất cả (voice-service + Gemini + save DB) ✅
3. **Database:** Proper linking với `assessment_id` foreign key ✅
4. **UI:** ComprehensiveResultsPage hiển thị đầy đủ thông tin ✅

### ❌ Điểm bạn hiểu SAI trong mô tả:

- Bạn nói: "Gửi voice service → lưu DB → **ấn 'Phân tích' → gửi lại**"
- Thực tế: "Ấn 'Phân tích' → **tất cả xảy ra cùng lúc trong 1 request**"

### 🎯 Kết luận:

**Code đã đúng!** Chỉ cần hiểu rõ rằng button "Phân tích" không phải là bước riêng biệt - nó trigger toàn bộ pipeline (voice-service + Gemini + DB) trong **1 lần gọi API duy nhất**.
