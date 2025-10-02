# 🎯 PHÂN TÍCH THIẾT KẾ - GAD-7 & VOICE ANALYSIS

**Date**: October 2, 2025  
**Focus**: Use Cases, Schema Design, UX Flow  
**Context**: Mental health screening for students (10-20 users)

---

## 📊 PHẦN 1: CÁC HƯỚNG TIẾP CẬN

### Option A: GAD-7 ONLY (Chỉ Bảng Câu Hỏi)

**Ưu điểm** ✅:

- **Nhanh**: 2-3 phút hoàn thành
- **Khách quan**: Điểm số chuẩn quốc tế (0-21)
- **Dễ theo dõi**: So sánh qua thời gian
- **Không ngại**: Không cần thu âm (privacy concern)
- **Có sẵn**: Đã implement hoàn chỉnh

**Nhược điểm** ❌:

- **Thiếu ngữ cảnh**: Chỉ có số, không có câu chuyện
- **Self-report bias**: Student có thể "che giấu" hoặc không nhận ra
- **Thiếu cảm xúc**: Không bắt được tone, giọng nói, ngắt nghỉ
- **Ít thông tin**: AI khó đưa ra recommendation cá nhân hóa sâu

**Khi nào dùng**:

- Student bận, không có thời gian
- Student ngại chia sẻ bằng giọng nói
- Check-in nhanh hàng tuần
- Screening ban đầu

---

### Option B: VOICE ONLY (Chỉ Ghi Âm)

**Ưu điểm** ✅:

- **Tự nhiên**: Như kể chuyện, ít áp lực
- **Giàu thông tin**: Tone, emotion, keywords, pauses
- **Bắt cảm xúc**: AI phát hiện anxiety/sadness từ giọng
- **Cá nhân hóa**: Transcript cho context chi tiết

**Nhược điểm** ❌:

- **Mất thời gian**: 3-5 phút record + xử lý
- **Privacy concern**: Nhiều student ngại ghi âm
- **Khó so sánh**: Không có số cụ thể để track qua thời gian
- **Phụ thuộc ngôn ngữ**: Tiếng Việt, phát âm, giọng địa phương
- **Không chuẩn**: Không có score quốc tế

**Khi nào dùng**:

- Student muốn chia sẻ chi tiết
- Tư vấn sâu (counselor cần context)
- Follow-up sau GAD-7 cao
- Student ngại điền form

---

### Option C: BOTH (GAD-7 + Voice) - ⭐ RECOMMENDED

**Ưu điểm** ✅:

- **Toàn diện**: Có cả objective (số) + subjective (cảm xúc)
- **Chính xác hơn**: Cross-validate giữa 2 nguồn
  - VD: GAD-7 = 8 (mild) nhưng voice cho thấy anxiety 85% → Cần chú ý!
- **Context phong phú**: AI có nhiều data để analyze
- **Personalized**: Recommendations dựa trên cả score + câu chuyện
- **Phát hiện sớm**: Voice có thể catch những gì student không nói ra trong GAD-7

**Nhược điểm** ❌:

- **Tốn thời gian**: 5-8 phút tổng
- **Phức tạp**: Student có thể overwhelm
- **Không phải lúc nào cũng cần**: Weekly check-in không cần voice

**Khi nào dùng**:

- Assessment ban đầu (comprehensive)
- GAD-7 score thay đổi đột ngột
- Student tự nguyện chia sẻ thêm
- Monthly deep check-in

---

## 🎯 PHẦN 2: ĐỀ XUẤT THIẾT KẾ UX

### Flow Đề Xuất (Flexible + Optional):

```
┌─────────────────────────────────────────────────────────────┐
│ BƯỚC 1: GAD-7 Assessment (REQUIRED)                         │
├─────────────────────────────────────────────────────────────┤
│ 7 câu hỏi, 2-3 phút                                         │
│ → Score: 12/21 (Moderate anxiety)                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ BƯỚC 2: Voice Recording (OPTIONAL) 🎤                       │
├─────────────────────────────────────────────────────────────┤
│ ℹ️  Tooltip:                                                │
│ "Chia sẻ thêm qua giọng nói giúp chúng tôi hiểu rõ hơn     │
│  về tình trạng của bạn và đưa ra gợi ý phù hợp hơn.        │
│  Hoàn toàn tùy chọn và bảo mật."                            │
│                                                              │
│ Prompt: "Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua      │
│          (30-60 giây). Bạn đã trải qua những gì?"          │
│                                                              │
│ [Skip] [Record]                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ BƯỚC 3: Analysis & Recommendations                          │
├─────────────────────────────────────────────────────────────┤
│ Nếu CHỈ GAD-7:                                              │
│   ✓ Score: 12/21 (Moderate)                                │
│   ✓ Basic AI analysis dựa trên GAD-7                       │
│   ✓ Standard recommendations                                │
│                                                              │
│ Nếu CÓ Voice:                                               │
│   ✓ Score: 12/21 + Voice insights                          │
│   ✓ "Chúng tôi nhận thấy giọng bạn có dấu hiệu lo âu..."  │
│   ✓ Personalized recommendations based on transcript        │
│   ✓ Counselor có thêm context để support                   │
└─────────────────────────────────────────────────────────────┘
```

### Tooltip Content (cho voice optional):

**Tiêu đề**: "Tại sao nên chia sẻ qua giọng nói?"

**Nội dung**:

```
✅ Giúp AI hiểu rõ hơn tình trạng của bạn
✅ Recommendations được cá nhân hóa dựa trên câu chuyện
✅ Phát hiện những dấu hiệu không rõ qua bảng câu hỏi
✅ Hỗ trợ counselor có context khi tư vấn

🔒 Bảo mật:
- Chỉ bạn và counselor được phân quyền mới xem được
- Có thể xóa bất cứ lúc nào
- Không bắt buộc

⏱️ Thời gian: 30-60 giây
```

---

## 🗂️ PHẦN 3: PHÂN TÍCH SCHEMA DESIGN

### 3.1. Assessment Schema (GAD-7) ✅

```python
class Assessment:
    id: int
    student_id: int  # ✅ Foreign key

    # Core data
    answers: JSON        # ✅ [0,1,2,3,2,1,0] - 7 câu
    total_score: int     # ✅ 0-21
    severity_level: str  # ✅ minimal/mild/moderate/severe
    functional_impairment: int  # ✅ 0-3 (optional)

    # AI Analysis
    analysis: Text       # ✅ Gemini response (Vietnamese)
    recommendations: JSON  # ✅ List of strings

    # Metadata
    created_at: DateTime  # ✅ Timestamp
    notes: Text          # ✅ Student's own notes

    # Relationships
    student: Student     # ✅ One-to-many
    voice_analyses: List[VoiceAnalysis]  # ✅ One-to-many
```

**Đánh giá**: ✅ **Excellent Design**

**Ưu điểm**:

- Compact: Đủ info, không thừa
- Đúng chuẩn GAD-7
- Support multiple voice recordings per assessment
- Clear separation: data vs analysis vs metadata

**Suggestions**: ✅ Không cần thay đổi

---

### 3.2. VoiceAnalysis Schema (27 fields) 🤔

```python
class VoiceAnalysis:
    id: int
    student_id: int      # ✅ Owner
    assessment_id: int   # ✅ Optional link (nullable)

    # ━━━ FILE INFO (4 fields) ━━━
    audio_file_path: str     # ✅ Storage path
    file_size_bytes: int     # ✅ For validation
    audio_duration: float    # ✅ Seconds
    audio_format: str        # ✅ wav/mp3/m4a

    # ━━━ PROMPT (2 fields) ━━━
    prompt_id: int          # ❓ Có cần? (see below)
    prompt_text: Text       # ✅ Actual prompt used

    # ━━━ TRANSCRIPTION (4 fields) ━━━
    transcription: Text     # ✅ Whisper output
    transcription_language: str  # ✅ Default 'vi'
    word_count: int         # ✅ For analysis
    transcription_confidence: float  # ✅ Quality check

    # ━━━ AUDIO FEATURES (1 JSONB) ━━━
    audio_features: JSON    # ✅ {pitch, energy, speech_rate, pauses, stability}

    # ━━━ EMOTIONS (3 fields) ━━━
    detected_emotions: JSON # ✅ {anxiety: 0.75, sadness: 0.60, ...}
    dominant_emotion: str   # ✅ For quick query
    emotion_confidence: float  # ✅ Quality indicator

    # ━━━ TEXT ANALYSIS (3 fields) ━━━
    sentiment_score: float  # ✅ -1 to 1
    keywords: JSON          # ✅ [{word, count, weight}]
    psychological_markers: JSON  # ✅ {negative_words, self_reference, ...}

    # ━━━ NORMALIZATION (2 fields) ━━━
    gender_used: str        # ✅ For fair comparison
    normalized_features: JSON  # ✅ Z-scores

    # ━━━ PROCESSING (5 fields) ━━━
    created_at: DateTime
    processed_at: DateTime
    processing_status: str  # ✅ pending/processing/completed/failed
    processing_time: float
    has_error: int
    error_message: Text

    # Relationships
    student: Student
    assessment: Assessment
    message: Message  # ❓ Có cần? (see below)
```

**Đánh giá**: ⚠️ **Good but có thể tối ưu**

---

### 3.3. Phân Tích Chi Tiết Từng Nhóm Field:

#### ✅ KEEP (Cần thiết):

**1. File Info (4 fields)**:

- ✅ `audio_file_path`: Truy cập file
- ✅ `file_size_bytes`: Validation, quota
- ✅ `audio_duration`: UX display, analysis context
- ✅ `audio_format`: Compatibility check

**2. Transcription (4 fields)**:

- ✅ `transcription`: Core output từ Whisper
- ✅ `transcription_language`: Multi-language support (future)
- ✅ `word_count`: Quality indicator (too short = không đủ info)
- ✅ `transcription_confidence`: Trust score

**3. Audio Features (1 JSONB)**:

- ✅ Đúng design: JSONB cho flexible schema
- ✅ Không nên split ra nhiều columns (pitch_mean, pitch_std, ...)
- ✅ Dễ extend thêm features mới

**4. Emotions (3 fields)**:

- ✅ `detected_emotions` (JSON): Full detail
- ✅ `dominant_emotion` (indexed): Quick filter
- ✅ `emotion_confidence`: Quality check

**5. Text Analysis (3 fields)**:

- ✅ `sentiment_score`: Numeric cho trending
- ✅ `keywords`: SEO-like analysis
- ✅ `psychological_markers`: Research-grade

**6. Normalization (2 fields)**:

- ✅ `gender_used`: Fair comparison, audit trail
- ✅ `normalized_features`: Research purposes

**7. Processing Metadata (5 fields)**:

- ✅ Essential cho error handling + debugging

---

#### 🤔 REVIEW (Cần xem xét):

**1. `prompt_id` (Integer)**:

**Hiện trạng**:

- Column exists
- Nullable (good)
- Không có table `prompts` (chưa implement)

**Options**:

- **A) Keep**: Nếu sẽ có table prompts (chuẩn hóa)

  ```sql
  CREATE TABLE recording_prompts (
      id SERIAL PRIMARY KEY,
      text TEXT NOT NULL,
      category VARCHAR(50),  -- anxiety, depression, general
      order_index INT
  );
  ```

  ✅ Pro: Reusable, consistent, easy to manage
  ❌ Con: Overhead cho 10-20 users

- **B) Remove**: Chỉ dùng `prompt_text`
  ✅ Pro: Simpler
  ❌ Con: Duplicate text, hard to analyze patterns

**Recommendation**:

- **Keep `prompt_id` + Add `prompts` table** nếu:

  - Muốn có library của prompts
  - Muốn A/B test prompts
  - Muốn analytics: "Prompt nào user share nhiều nhất?"

- **Remove `prompt_id`** nếu:
  - Chỉ cần free-form text
  - Không có plan cho prompt library

**Đề xuất cho 10-20 users**: **Keep but make it simple**

```python
# Hardcode 3-5 prompts trong code
PROMPTS = [
    {"id": 1, "text": "Hãy chia sẻ cảm xúc trong 2 tuần qua"},
    {"id": 2, "text": "Điều gì khiến bạn lo lắng gần đây?"},
    {"id": 3, "text": "Bạn đã trải qua những gì trong tuần này?"}
]
```

---

**2. `message` Relationship**:

**Hiện trạng**:

```python
message = relationship("Message", back_populates="voice_analysis", uselist=False)
```

**Câu hỏi**: Voice analysis link với Message để làm gì?

**Possible Use Cases**:

- **A) Counselor reply**: Voice analysis → Counselor xem → Gửi message reply

  ```
  Student: GAD-7 + Voice
  → Counselor xem analysis
  → Counselor: "Em ơi, anh thấy em có vẻ lo lắng, hãy chat với anh nhé"
  → Message có voice_analysis_id
  ```

  ✅ Có ý nghĩa: Track conversation context

- **B) Voice = Message**: Student gửi voice như chat message
  ```
  Student → Voice message (like WhatsApp)
  → System analyze
  → Save to voice_analyses + messages
  ```
  ✅ Có ý nghĩa: Voice as communication method

**Recommendation**:

- **Keep nếu có chat system** với voice messages
- **Remove nếu voice chỉ dùng cho assessment**

**Đề xuất cho MVP**: **Remove hoặc nullable**, thêm lại khi implement chat

---

### 3.4. Thiếu Gì? (Missing Fields)

#### 🆕 Đề Xuất Thêm:

**1. `is_shared_with_counselor` (Boolean)**:

```python
is_shared_with_counselor = Column(Boolean, default=False)
```

**Lý do**: Student có thể muốn làm assessment riêng tư trước khi share

**2. `counselor_notes` (Text)**:

```python
counselor_notes = Column(Text, nullable=True)
```

**Lý do**: Counselor cần ghi chú về voice analysis

**3. `trigger_words_detected` (JSON)**:

```python
trigger_words_detected = Column(JSON, nullable=True)
# ["tự tử", "không muốn sống", "vô vọng"]
```

**Lý do**: Critical safety feature - alert system nếu có trigger words

---

## 🎯 PHẦN 4: PERMISSIONS & ACCESS CONTROL

### Current RLS Policies ✅:

```sql
-- Students: Own data only
CREATE POLICY students_own_voice_analyses
ON voice_analyses FOR SELECT
TO authenticated
USING (student_id IN (
    SELECT id FROM students WHERE user_id = auth.uid()
));

-- Counselors: Assigned students
CREATE POLICY counselors_assigned_voice_analyses
ON voice_analyses FOR SELECT
TO authenticated
USING (student_id IN (
    SELECT student_id FROM counselor_students
    WHERE counselor_id IN (
        SELECT id FROM counselors WHERE user_id = auth.uid()
    )
));

-- Admins: All
CREATE POLICY admins_all_voice_analyses
ON voice_analyses FOR ALL
TO authenticated
USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'ADMIN')
);
```

**Đánh giá**: ✅ **Excellent**

---

### Đề Xuất Thêm: Consent Management

**Problem**: Student có thể không muốn counselor xem voice recording ngay

**Solution**: Add consent table

```sql
CREATE TABLE data_sharing_consents (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    counselor_id INTEGER REFERENCES counselors(id),

    -- Permissions
    can_view_assessments BOOLEAN DEFAULT true,
    can_view_voice_analyses BOOLEAN DEFAULT false,  -- Opt-in!
    can_view_transcripts BOOLEAN DEFAULT false,

    -- Metadata
    granted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    revoked_at TIMESTAMP
);
```

**Update RLS**:

```sql
CREATE POLICY counselors_consented_voice_analyses
ON voice_analyses FOR SELECT
TO authenticated
USING (
    -- Original: Assigned students
    student_id IN (
        SELECT student_id FROM counselor_students
        WHERE counselor_id IN (
            SELECT id FROM counselors WHERE user_id = auth.uid()
        )
    )
    AND
    -- NEW: Student has granted consent
    EXISTS (
        SELECT 1 FROM data_sharing_consents
        WHERE student_id = voice_analyses.student_id
        AND counselor_id IN (SELECT id FROM counselors WHERE user_id = auth.uid())
        AND can_view_voice_analyses = true
        AND (expires_at IS NULL OR expires_at > NOW())
        AND revoked_at IS NULL
    )
);
```

---

## 📋 PHẦN 5: TÓM TẮT & RECOMMENDATIONS

### 5.1. Use Cases Summary:

| Scenario                   | GAD-7       | Voice                 | Best Practice          |
| -------------------------- | ----------- | --------------------- | ---------------------- |
| **Weekly check-in**        | ✅ Required | ❌ Skip               | Quick screening        |
| **First assessment**       | ✅ Required | ✅ Recommended        | Comprehensive baseline |
| **High score (>15)**       | ✅ Done     | ✅ Highly recommended | Deep understanding     |
| **Student wants to share** | ✅ Done     | ✅ Optional           | Let them tell story    |
| **Counselor referral**     | ✅ Done     | ✅ Helpful            | Context for counselor  |
| **Crisis situation**       | ✅ Done     | ✅ Critical           | Trigger word detection |

### 5.2. UX Flow Recommendation:

```
1. GAD-7 (ALWAYS)
   ↓
2. If score >= 10 OR student wants: Prompt voice (OPTIONAL)
   ↓
3. Analysis:
   - GAD-7 only: Standard analysis
   - GAD-7 + Voice: Enhanced analysis
```

### 5.3. Schema Recommendations:

**Priority 1 (Must Have)**:

- ✅ Current schema is excellent foundation
- ✅ Keep all 27 fields (well-designed)
- ✅ RLS policies are solid

**Priority 2 (Nice to Have)**:

- 🆕 Add `trigger_words_detected` for safety
- 🆕 Add consent management for privacy
- 🆕 Consider `prompts` table for prompt library

**Priority 3 (Future)**:

- 🔄 Review `message` relationship when implementing chat
- 🔄 Add counselor notes field
- 🔄 Add sharing permissions

### 5.4. Implementation Priority:

**IMMEDIATE (This sprint)**:

1. ✅ Implement GAD-7 + Voice integration (2-3h)
2. ✅ Add tooltip for voice optional
3. ✅ Add basic prompts (hardcoded 3-5)

**SHORT-TERM (Next sprint)**: 4. Add trigger word detection 5. Add consent management UI 6. Counselor dashboard to view voice analyses

**LONG-TERM (Future)**: 7. Prompt library table 8. Advanced analytics on voice patterns 9. Multi-language support

---

## ✅ KẾT LUẬN

**Schema Design**: ⭐⭐⭐⭐⭐ (5/5)

- Well-thought-out
- Comprehensive but not bloated
- Good separation of concerns

**Current Gap**: Integration (GAD-7 + Voice)
**Fix Time**: 2-3 hours

**Recommendation**:

- **Make voice OPTIONAL but RECOMMENDED**
- **Use tooltip to explain benefits**
- **Allow flexibility based on student preference**

---

**Generated by**: GitHub Copilot  
**Focus**: UX + Schema Design + Permissions
