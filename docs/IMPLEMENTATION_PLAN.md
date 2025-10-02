# 🚀 KẾ HOẠCH TRIỂN KHAI - GAD-7 + VOICE INTEGRATION

**Date**: October 2, 2025  
**Approach**: Both Required (Simplified)  
**Estimated Time**: 2-3 hours

---

## ✅ VẤN ĐỀ ĐƯỢC GIẢI QUYẾT

### **1. Core Integration Gap** ❌→✅

**Before**: GAD-7 và Voice hoạt động độc lập, không kết nối

```python
# Hiện tại
POST /assessments/submit → Assessment created (no voice)
POST /voice-analysis/upload → VoiceAnalysis created (no assessment)
# assessment_id = NULL trong voice_analyses
```

**After**: Unified flow, always connected

```python
# Sau khi implement
POST /assessments/submit-with-voice → Assessment + VoiceAnalysis
# assessment_id ALWAYS populated
```

---

### **2. Data Consistency** ❌→✅

**Before**: Orphaned records, NULL foreign keys

```sql
-- voice_analyses table
id | student_id | assessment_id | transcript
1  | 5          | NULL         | "Tôi cảm thấy lo lắng..."  ← Orphaned!
2  | 5          | NULL         | "Hôm nay tốt hơn..."       ← Orphaned!

-- assessments table
id | student_id | total_score | analysis
1  | 5          | 12          | "Moderate anxiety"  ← No voice data!
2  | 5          | 8           | "Mild anxiety"      ← No voice data!
```

**After**: Perfect consistency

```sql
-- voice_analyses table
id | student_id | assessment_id | transcript
1  | 5          | 1            | "Tôi cảm thấy lo lắng..."  ← Linked!
2  | 5          | 2            | "Hôm nay tốt hơn..."       ← Linked!

-- assessments table
id | student_id | total_score | analysis
1  | 5          | 12          | "Combined analysis..."  ← Has voice!
2  | 5          | 8           | "Combined analysis..."  ← Has voice!
```

---

### **3. Referential Integrity** ❌→✅

**Before**: FK exists but unused

```python
# voice_analysis.py
assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=True)
# Always NULL → FK pointless
```

**After**: FK always populated

```python
assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
# NOT NULL → Enforces data integrity
```

---

### **4. Query Simplification** ❌→✅

**Before**: Complex queries, need NULL checks

```python
# Get assessment with voice (might not exist)
assessment = db.query(Assessment).filter(Assessment.id == 1).first()
voice = db.query(VoiceAnalysis).filter(
    VoiceAnalysis.assessment_id == 1
).first()  # Might be None!

if voice:
    # Combined analysis
else:
    # GAD-7 only
```

**After**: Simple JOIN, always works

```python
# Get assessment with voice (always exists)
assessment = db.query(Assessment)\
    .join(VoiceAnalysis)\
    .filter(Assessment.id == 1)\
    .first()

# voice_analyses relationship always has 1 item
voice = assessment.voice_analyses[0]  # Never empty!
```

---

### **5. Gemini Prompt Complexity** ❌→✅

**Before**: 2 separate prompts

```python
def analyze_gad7(answers, score):
    """GAD-7 only analysis"""
    prompt = f"Analyze GAD-7: {score}/21..."

def analyze_with_voice(gad7, voice):
    """Combined analysis (rarely used)"""
    prompt = f"Analyze GAD-7 + Voice..."
```

**After**: 1 unified prompt

```python
def analyze_combined(gad7, voice):
    """Always combined (single source of truth)"""
    prompt = f"Analyze GAD-7 + Voice..."
    # Cross-validation built-in
```

---

## 📋 IMPLEMENTATION CHECKLIST

### **Phase 1: Schema Updates** (5 phút)

- [ ] **1.1** Update `VoiceAnalysis` model:

  - Change `assessment_id` from `nullable=True` → `nullable=False`
  - Add constraint comment

- [ ] **1.2** Create Alembic migration:
  - Handle existing NULL records (if any)
  - Add NOT NULL constraint

### **Phase 2: Backend Implementation** (90 phút)

- [ ] **2.1** Create combined endpoint:

  - `POST /api/v1/assessments/submit-with-voice`
  - Accept: GAD-7 answers + audio file
  - Return: Assessment + VoiceAnalysis

- [ ] **2.2** Create Gemini combined analysis:

  - `analyze_combined(gad7_data, voice_data)`
  - Enhanced prompt with cross-validation
  - Return: Analysis + Recommendations

- [ ] **2.3** Update voice service integration:

  - Keep existing `/analyze` endpoint
  - No changes needed (already working)

- [ ] **2.4** Transaction handling:
  - Atomic: Both succeed or both rollback
  - Error handling for voice processing
  - Retry logic for Gemini

### **Phase 3: Testing** (30 phút)

- [ ] **3.1** Unit tests:

  - Test combined endpoint
  - Test Gemini prompt
  - Test error cases

- [ ] **3.2** Integration tests:

  - End-to-end flow
  - Database consistency
  - RLS policies still work

- [ ] **3.3** Manual testing:
  - Upload real audio
  - Verify analysis quality
  - Check database state

### **Phase 4: Documentation** (15 phút)

- [ ] **4.1** Update API docs:

  - New endpoint specification
  - Request/response examples

- [ ] **4.2** Update README:
  - New flow diagram
  - Usage examples

---

## 🔧 DETAILED IMPLEMENTATION

### **Step 1: Schema Update**

**File**: `ai-service/app/models/voice_analysis.py`

```python
# Before
assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=True)

# After
assessment_id = Column(
    Integer,
    ForeignKey('assessments.id', ondelete='CASCADE'),
    nullable=False,  # ← Changed: Always required
    comment="Required: Every voice analysis must link to an assessment"
)
```

**Migration**: `alembic/versions/xxx_make_assessment_id_required.py`

```python
def upgrade():
    # Step 1: Delete orphaned voice_analyses (if any)
    op.execute("""
        DELETE FROM voice_analyses
        WHERE assessment_id IS NULL
    """)

    # Step 2: Add NOT NULL constraint
    op.alter_column(
        'voice_analyses',
        'assessment_id',
        existing_type=sa.Integer(),
        nullable=False
    )

def downgrade():
    op.alter_column(
        'voice_analyses',
        'assessment_id',
        existing_type=sa.Integer(),
        nullable=True
    )
```

---

### **Step 2: Combined Endpoint**

**File**: `ai-service/app/api/v1/endpoints/assessments.py`

```python
@router.post("/submit-with-voice", response_model=AssessmentResponse)
async def submit_assessment_with_voice(
    # GAD-7 data
    answers: List[int] = Form(..., description="7 answers (0-3 each)"),
    functional_impairment: int = Form(0, ge=0, le=3),
    notes: Optional[str] = Form(None),

    # Voice data
    audio_file: UploadFile = File(..., description="Voice recording"),
    gender: str = Form(..., pattern="^(male|female|other|prefer_not_to_say)$"),
    prompt_text: Optional[str] = Form("Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua"),

    # Dependencies
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Submit GAD-7 assessment with voice recording (unified flow).

    Process:
    1. Validate GAD-7 answers
    2. Upload audio to storage
    3. Send to voice-service for analysis
    4. Combine GAD-7 + voice data
    5. Send to Gemini for integrated analysis
    6. Save both to database (atomic transaction)
    """

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Validate GAD-7
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if len(answers) != 7:
        raise HTTPException(400, "Must provide exactly 7 answers")

    if any(a < 0 or a > 3 for a in answers):
        raise HTTPException(400, "Each answer must be 0-3")

    total_score = sum(answers)
    severity = calculate_severity(total_score)

    logger.info(f"GAD-7: score={total_score}, severity={severity}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Process Voice Recording
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    student = current_user.student
    if not student:
        raise HTTPException(403, "Only students can submit assessments")

    # Read audio file
    audio_bytes = await audio_file.read()
    file_size = len(audio_bytes)

    # Gender mapping (prefer_not_to_say → other)
    gender_for_voice_service = "other" if gender == "prefer_not_to_say" else gender

    # Save to Supabase Storage
    try:
        storage_path = await storage.save_audio(
            student_id=student.id,
            audio_bytes=audio_bytes,
            filename=audio_file.filename
        )
        logger.info(f"Audio saved: {storage_path}")
    except Exception as e:
        logger.error(f"Storage error: {e}")
        raise HTTPException(500, f"Failed to save audio: {str(e)}")

    # Send to voice-service
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            files = {"file": (audio_file.filename, audio_bytes, audio_file.content_type)}
            data = {
                "gender": gender_for_voice_service,
                "prompt": prompt_text
            }

            response = await client.post(
                f"{VOICE_SERVICE_URL}/api/v1/analyze",
                files=files,
                data=data
            )
            response.raise_for_status()
            voice_result = response.json()

        logger.info(f"Voice analysis: emotions={voice_result.get('emotions')}")

    except httpx.HTTPError as e:
        logger.error(f"Voice service error: {e}")
        raise HTTPException(502, f"Voice analysis failed: {str(e)}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Combined Gemini Analysis
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    gad7_data = {
        "answers": answers,
        "total_score": total_score,
        "severity": severity,
        "functional_impairment": functional_impairment
    }

    try:
        gemini_result = await gemini_service.analyze_combined(
            gad7_data=gad7_data,
            voice_data=voice_result
        )
        logger.info("Gemini analysis completed")

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(500, f"AI analysis failed: {str(e)}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: Save to Database (Atomic Transaction)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    try:
        # Create assessment first
        assessment = Assessment(
            student_id=student.id,
            answers=answers,
            total_score=total_score,
            severity_level=severity,
            functional_impairment=functional_impairment,
            analysis=gemini_result["analysis"],
            recommendations=gemini_result["recommendations"],
            notes=notes
        )
        db.add(assessment)
        db.flush()  # Get assessment.id

        # Create linked voice analysis
        voice_analysis = VoiceAnalysis(
            student_id=student.id,
            assessment_id=assessment.id,  # ← Always linked!

            # File info
            audio_file_path=storage_path,
            file_size_bytes=file_size,
            audio_duration=voice_result.get("audio_duration"),
            audio_format=audio_file.filename.split(".")[-1] if "." in audio_file.filename else "unknown",

            # Prompt
            prompt_text=prompt_text,

            # Transcription
            transcription=voice_result.get("transcript"),
            transcription_language=voice_result.get("language", "vi"),
            word_count=len(voice_result.get("transcript", "").split()) if voice_result.get("transcript") else 0,
            transcription_confidence=voice_result.get("transcription_confidence"),

            # Audio features
            audio_features=voice_result.get("audio_features"),

            # Emotions
            detected_emotions=voice_result.get("emotions"),
            dominant_emotion=max(voice_result.get("emotions", {}), key=voice_result.get("emotions", {}).get, default=None),
            emotion_confidence=max(voice_result.get("emotions", {}).values(), default=0.0),

            # Text analysis
            sentiment_score=voice_result.get("text_analysis", {}).get("sentiment_score"),
            keywords=voice_result.get("text_analysis", {}).get("keywords"),
            psychological_markers=voice_result.get("text_analysis", {}).get("psychological_markers"),

            # Normalization
            gender_used=gender_for_voice_service,
            normalized_features=voice_result.get("normalized_features"),

            # Processing metadata
            processing_status="completed",
            processed_at=datetime.utcnow(),
            processing_time=voice_result.get("processing_time", 0.0)
        )
        db.add(voice_analysis)

        # Commit both together (atomic)
        db.commit()
        db.refresh(assessment)
        db.refresh(voice_analysis)

        logger.info(f"Saved: assessment_id={assessment.id}, voice_id={voice_analysis.id}")

        return {
            "id": assessment.id,
            "student_id": assessment.student_id,
            "total_score": assessment.total_score,
            "severity_level": assessment.severity_level,
            "analysis": assessment.analysis,
            "recommendations": assessment.recommendations,
            "voice_analysis_id": voice_analysis.id,
            "created_at": assessment.created_at
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(500, f"Failed to save: {str(e)}")
```

---

### **Step 3: Gemini Service**

**File**: `ai-service/app/services/gemini_service.py`

````python
async def analyze_combined(
    self,
    gad7_data: dict,
    voice_data: dict
) -> dict:
    """
    Combined analysis using both GAD-7 and voice data.

    This provides:
    1. Cross-validation between objective (GAD-7) and subjective (voice)
    2. Detection of emotional suppression (low score but high anxiety in voice)
    3. Richer context for personalized recommendations
    """

    # Extract data
    score = gad7_data["total_score"]
    severity = gad7_data["severity"]
    answers = gad7_data["answers"]

    transcript = voice_data.get("transcript", "")
    emotions = voice_data.get("emotions", {})
    audio_features = voice_data.get("audio_features", {})
    text_analysis = voice_data.get("text_analysis", {})

    # Build enhanced prompt
    prompt = f"""
Bạn là chuyên gia tâm lý lâm sàng. Hãy phân tích tổng hợp tình trạng tâm lý của sinh viên dựa trên:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PHẦN 1: BẢNG CÂU HỎI GAD-7 (Objective Assessment)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Điểm số: {score}/21 - Mức độ: {severity}
Câu trả lời chi tiết:
1. Cảm thấy lo lắng, bồn chồn: {answers[0]}/3
2. Không kiểm soát được lo lắng: {answers[1]}/3
3. Lo lắng quá nhiều về nhiều thứ: {answers[2]}/3
4. Khó thư giãn: {answers[3]}/3
5. Bồn chồn khó ngồi yên: {answers[4]}/3
6. Dễ khó chịu hoặc cáu gắt: {answers[5]}/3
7. Cảm thấy sợ hãi: {answers[6]}/3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎤 PHẦN 2: PHÂN TÍCH GIỌNG NÓI (Subjective Expression)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nội dung chia sẻ:
"{transcript}"

Cảm xúc phát hiện từ giọng nói:
- Lo âu (Anxiety): {emotions.get('anxiety', 0):.1%}
- Buồn bã (Sadness): {emotions.get('sadness', 0):.1%}
- Giận dữ (Anger): {emotions.get('anger', 0):.1%}
- Trung tính (Neutral): {emotions.get('neutral', 0):.1%}

Đặc điểm giọng nói:
- Cao độ trung bình: {audio_features.get('pitch', {}).get('mean', 0):.1f} Hz
- Độ ổn định giọng: {audio_features.get('voice_stability', 0):.2f}
- Năng lượng trung bình: {audio_features.get('energy', {}).get('mean', 0):.2f}
- Tốc độ nói: {audio_features.get('speech_rate', 0):.1f} từ/phút
- Số lần ngắt quãng: {audio_features.get('pause_count', 0)} lần
- Thời gian ngắt quãng: {audio_features.get('pause_duration', 0):.1f} giây

Phân tích văn bản:
- Cảm xúc văn bản (Sentiment): {text_analysis.get('sentiment_score', 0):.2f} (-1 to 1)
- Từ khóa tâm lý: {', '.join([k.get('word', '') for k in text_analysis.get('keywords', [])[:5]])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ PHẦN 3: CROSS-VALIDATION (Quan trọng!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hãy kiểm tra sự nhất quán giữa GAD-7 và giọng nói:

1. **Nhất quán (Consistent)**:
   - VD: GAD-7 = cao (15+) VÀ giọng nói có anxiety cao (>60%)
   → Xác nhận tình trạng lo âu đáng kể

2. **Không nhất quán (Discrepancy)**:
   - VD: GAD-7 = thấp (<10) NHƯNG giọng nói có anxiety cao (>60%)
   → Có thể đang che giấu cảm xúc hoặc chưa nhận thức được

   - VD: GAD-7 = cao (15+) NHƯNG giọng nói bình thường
   → Có thể đang cố gắng kiểm soát hoặc đã quen với trạng thái lo âu

3. **Dấu hiệu cần chú ý**:
   - Pause quá nhiều (>5 lần) → Khó diễn đạt, có thể stress cao
   - Giọng không ổn định (stability <0.5) → Cảm xúc dao động
   - Sentiment âm (<-0.3) + GAD-7 cao → Nguy cơ depression
   - Từ khóa tiêu cực nhiều → Cần hỗ trợ tâm lý sâu hơn

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 YÊU CẦU OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hãy đưa ra phân tích bằng tiếng Việt, bao gồm:

1. **Tổng quan (2-3 câu)**:
   - Đánh giá tổng thể về tình trạng tâm lý
   - Nhận định về sự nhất quán giữa GAD-7 và giọng nói

2. **Phân tích chi tiết (3-4 đoạn)**:
   - Phân tích GAD-7: Điểm số nào cao? Ý nghĩa?
   - Phân tích giọng nói: Cảm xúc gì nổi bật? Đặc điểm gì đáng chú ý?
   - Cross-validation: Có nhất quán không? Nếu không, giải thích tại sao?
   - Dấu hiệu cần lưu ý (nếu có)

3. **Gợi ý hỗ trợ (3-5 gợi ý cụ thể)**:
   - Dựa trên CẢ GAD-7 VÀ giọng nói
   - Cá nhân hóa theo nội dung chia sẻ
   - Thực tế, dễ thực hiện
   - Có mức độ ưu tiên

Định dạng JSON:
{{
    "analysis": "...",
    "recommendations": ["...", "...", "..."]
}}
"""

    try:
        response = self.model.generate_content(prompt)
        text = response.text.strip()

        # Parse JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)

        return {
            "analysis": result.get("analysis", ""),
            "recommendations": result.get("recommendations", [])
        }

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        # Fallback
        return {
            "analysis": f"Phân tích tổng hợp dựa trên GAD-7 (điểm {score}) và giọng nói. Cần kiểm tra lại kết quả.",
            "recommendations": [
                "Tiếp tục theo dõi tình trạng",
                "Gặp tư vấn viên nếu cần",
                "Thực hành các kỹ thuật thư giãn"
            ]
        }
````

---

## ⏱️ TIMELINE

| Phase       | Task              | Time           | Priority |
| ----------- | ----------------- | -------------- | -------- |
| **Phase 1** | Schema migration  | 5 min          | P0       |
| **Phase 2** | Combined endpoint | 60 min         | P0       |
| **Phase 2** | Gemini service    | 30 min         | P0       |
| **Phase 3** | Integration tests | 30 min         | P0       |
| **Phase 4** | Documentation     | 15 min         | P1       |
| **TOTAL**   |                   | **~2.5 hours** |          |

---

## ✅ SUCCESS CRITERIA

1. ✅ Every `voice_analyses` record has `assessment_id` (NOT NULL)
2. ✅ Single endpoint creates both Assessment + VoiceAnalysis atomically
3. ✅ Gemini uses combined prompt for enhanced analysis
4. ✅ Database queries simpler (no NULL checks needed)
5. ✅ All existing tests still pass
6. ✅ New integration tests pass

---

## 🚀 READY TO START?

Bạn confirm, mình sẽ bắt đầu implement ngay! 🔥
