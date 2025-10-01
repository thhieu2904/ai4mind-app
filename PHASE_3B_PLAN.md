# 🎙️ Phase 3b: Voice Service Implementation - Action Plan

**Branch**: `voice-analysis`  
**Date**: October 1, 2025  
**Estimated Time**: 3-4 hours  
**Status**: 📋 PLANNING → EXECUTION

---

## 🎯 Overview

Xây dựng **voice-service microservice** để:

1. Nhận file audio từ frontend
2. Trích xuất audio features (pitch, energy, speech rate)
3. Chuyển đổi giọng nói thành text (Whisper)
4. Phát hiện cảm xúc (anxiety, sadness, anger)
5. Phân tích ngữ nghĩa tiếng Việt
6. **Normalize theo giới tính** để tránh bias
7. Trả kết quả về cho ai-service

---

## 📋 Implementation Plan

### PHASE 3b.1: Voice Service Structure Setup (30 mins)

**Goal**: Tạo cấu trúc microservice hoàn chỉnh

**Tasks**:

- [ ] 1.1. Create `voice-service/` directory structure

  ```
  voice-service/
  ├── app/
  │   ├── main.py              # FastAPI application
  │   ├── core/
  │   │   ├── config.py        # Configuration
  │   │   └── constants.py     # Voice prompts, baselines
  │   ├── api/
  │   │   └── v1/
  │   │       └── endpoints/
  │   │           ├── analyze.py   # POST /analyze
  │   │           └── prompts.py   # GET /prompts
  │   ├── services/
  │   │   ├── audio_processor.py      # librosa features
  │   │   ├── whisper_service.py      # Speech-to-text
  │   │   ├── emotion_classifier.py   # Emotion detection
  │   │   └── text_analyzer.py        # Vietnamese NLP
  │   ├── models/
  │   │   └── schemas.py       # Pydantic models
  │   └── utils/
  │       ├── file_handler.py  # File upload/storage
  │       └── gender_normalizer.py  # Gender-aware normalization
  ├── requirements.txt
  ├── .env
  └── README.md
  ```

- [ ] 1.2. Create `requirements.txt` with dependencies:

  ```
  fastapi==0.104.1
  uvicorn==0.24.0
  openai-whisper==20231117
  librosa==0.10.1
  soundfile==0.12.1
  numpy==1.24.3
  pydantic==2.5.0
  python-multipart==0.0.6
  aiofiles==23.2.1
  ```

- [ ] 1.3. Create `.env` configuration
- [ ] 1.4. Setup `main.py` with FastAPI app
- [ ] 1.5. Create health check endpoint

**Success Criteria**:

- ✅ Directory structure complete
- ✅ Dependencies installable
- ✅ FastAPI app runs on port 8001
- ✅ Health check returns 200 OK

---

### PHASE 3b.2: Audio Processing Service (45 mins)

**Goal**: Trích xuất audio features với librosa

**Tasks**:

- [ ] 2.1. Create `services/audio_processor.py`

  - Load audio file with librosa
  - Extract pitch (F0) using `librosa.pyin()`
  - Extract energy/intensity using RMS
  - Calculate speech rate (syllables per second)
  - Count pauses (silence detection)
  - Calculate voice stability
  - Extract MFCCs (optional)

- [ ] 2.2. Create `utils/gender_normalizer.py`

  - Define gender-specific baselines:
    ```python
    BASELINES = {
        "male": {"pitch_mean": 130, "pitch_std": 40},
        "female": {"pitch_mean": 210, "pitch_std": 45},
        "other": {"pitch_mean": 170, "pitch_std": 50}
    }
    ```
  - Implement `normalize_pitch()` function
  - Calculate z-scores
  - Return normalized features

- [ ] 2.3. Create test audio file processor
  - Test with sample WAV file
  - Verify feature extraction works
  - Test gender normalization

**Success Criteria**:

- ✅ Audio features extracted correctly
- ✅ Gender normalization working
- ✅ Test with sample audio passes

**Example Output**:

```python
{
    "pitch_mean": 220.5,
    "pitch_std": 45.2,
    "energy_mean": 0.68,
    "speech_rate": "fast",
    "pause_count": 12,
    "voice_stability": 0.42,
    "normalized": {
        "pitch_z_score": 0.5,
        "pitch_deviation": 0.5
    }
}
```

---

### PHASE 3b.3: Speech-to-Text Service (30 mins)

**Goal**: Chuyển đổi giọng nói thành text bằng Whisper

**Tasks**:

- [ ] 3.1. Create `services/whisper_service.py`

  - Load Whisper model (base or medium)
  - Implement `transcribe()` function
  - Support Vietnamese language
  - Return transcript, confidence, duration

- [ ] 3.2. Handle audio format conversion

  - Convert MP3/M4A to WAV if needed
  - Resample to 16kHz (Whisper requirement)

- [ ] 3.3. Test Vietnamese transcription
  - Test with Vietnamese audio sample
  - Verify accuracy

**Success Criteria**:

- ✅ Whisper model loaded
- ✅ Vietnamese transcription working
- ✅ Returns transcript + metadata

**Example Output**:

```python
{
    "transcript": "Tuần này em cảm thấy rất lo lắng về học tập...",
    "language": "vi",
    "duration": 45.5,
    "word_count": 120,
    "confidence": 0.92
}
```

---

### PHASE 3b.4: Emotion Detection Service (45 mins)

**Goal**: Phát hiện cảm xúc từ audio features (normalized)

**Tasks**:

- [ ] 4.1. Create `services/emotion_classifier.py`

  - Implement hybrid rule-based approach:
    ```python
    def detect_emotion(normalized_features):
        scores = {"anxiety": 0, "sadness": 0, "anger": 0, "neutral": 1.0}

        # Anxiety indicators
        if normalized_features["pitch_deviation"] > 1.5:
            scores["anxiety"] += 0.3
        if features["speech_rate"] == "fast":
            scores["anxiety"] += 0.2
        if features["pause_count"] > 15:
            scores["anxiety"] += 0.2

        # Sadness indicators
        if normalized_features["pitch_z_score"] < -1.0:
            scores["sadness"] += 0.3
        if features["energy_mean"] < 0.3:
            scores["sadness"] += 0.3

        # Normalize to sum=1
        return normalize_scores(scores)
    ```

- [ ] 4.2. Test emotion detection
  - Test with various audio samples
  - Verify gender normalization impact

**Success Criteria**:

- ✅ Emotion scores calculated
- ✅ Dominant emotion identified
- ✅ Confidence score provided

**Example Output**:

```python
{
    "emotion_scores": {
        "anxiety": 0.75,
        "sadness": 0.60,
        "anger": 0.10,
        "neutral": 0.20
    },
    "dominant_emotion": "anxiety",
    "confidence": 0.85
}
```

---

### PHASE 3b.5: Text Analysis Service (30 mins)

**Goal**: Phân tích ngữ nghĩa tiếng Việt từ transcript

**Tasks**:

- [ ] 5.1. Create `services/text_analyzer.py`

  - Sentiment analysis (simple approach first)
  - Keyword extraction (anxiety-related words)
  - Psychological markers:
    ```python
    markers = {
        "negative_words": ["lo lắng", "sợ", "buồn", "stress", "áp lực"],
        "positive_words": ["vui", "tốt", "hạnh phúc", "thoải mái"],
        "self_reference": ["tôi", "em", "mình"],
        "uncertainty": ["có thể", "không chắc", "chắc là"]
    }
    ```

- [ ] 5.2. Count word frequencies
- [ ] 5.3. Calculate sentiment score (-1 to 1)

**Success Criteria**:

- ✅ Keywords detected
- ✅ Sentiment calculated
- ✅ Psychological markers counted

**Example Output**:

```python
{
    "sentiment_score": -0.6,
    "keywords": [
        {"word": "lo lắng", "count": 5, "weight": 0.8},
        {"word": "stress", "count": 3, "weight": 0.6}
    ],
    "psychological_markers": {
        "negative_words": 15,
        "positive_words": 3,
        "self_reference": 8,
        "uncertainty": 6
    }
}
```

---

### PHASE 3b.6: API Endpoints (45 mins)

**Goal**: Tạo REST API endpoints

**Tasks**:

- [ ] 6.1. Create `api/v1/endpoints/analyze.py`

  - POST /api/v1/voice-analysis/analyze
  - Accept multipart file upload
  - Get student info (including gender)
  - Run parallel processing:
    - Audio features extraction
    - Speech-to-text
  - Combine results
  - Store in database
  - Return analysis_id + results

- [ ] 6.2. Create `api/v1/endpoints/prompts.py`

  - GET /api/v1/voice-analysis/prompts
  - Return list of recording prompts

- [ ] 6.3. Create file upload handler

  - Validate file type (WAV, MP3, M4A)
  - Validate file size (<10MB)
  - Save to storage
  - Generate unique filename

- [ ] 6.4. Add error handling
  - Invalid file type
  - File too large
  - Processing errors

**Success Criteria**:

- ✅ POST /analyze endpoint works
- ✅ File upload handled correctly
- ✅ GET /prompts returns prompts
- ✅ Error handling in place

**API Contract**:

```python
POST /api/v1/voice-analysis/analyze
Content-Type: multipart/form-data

Request:
- audio_file: File
- student_id: int
- assessment_id: int (optional)
- prompt_id: int (optional)

Response:
{
    "analysis_id": 1,
    "transcript": "...",
    "audio_features": {...},
    "emotion_scores": {...},
    "text_analysis": {...},
    "processing_time_ms": 8500
}
```

---

### PHASE 3b.7: Configuration & Constants (15 mins)

**Goal**: Setup configuration và constants

**Tasks**:

- [ ] 7.1. Create `core/config.py`

  - Database URL
  - File storage path
  - Model paths
  - API settings

- [ ] 7.2. Create `core/constants.py`
  - Voice prompts in Vietnamese
  - Gender baselines
  - Emotion thresholds
  - Keyword lists

**Success Criteria**:

- ✅ Configuration loaded from .env
- ✅ Constants accessible

---

### PHASE 3b.8: Testing & Integration (30 mins)

**Goal**: Test toàn bộ voice service

**Tasks**:

- [ ] 8.1. Create test script

  - Test audio processing
  - Test gender normalization
  - Test emotion detection
  - Test API endpoints

- [ ] 8.2. Test with real audio samples

  - Male voice sample
  - Female voice sample
  - Verify normalization works

- [ ] 8.3. Integration test with ai-service
  - Call voice-service from ai-service
  - Verify data flow

**Success Criteria**:

- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Gender normalization verified

---

## 📊 Implementation Order

**PRIORITY 1** (Start immediately):

1. ✅ Phase 3b.1: Structure Setup (30 mins)
2. ✅ Phase 3b.2: Audio Processing (45 mins)

**PRIORITY 2** (Core functionality): 3. ✅ Phase 3b.3: Speech-to-Text (30 mins) 4. ✅ Phase 3b.4: Emotion Detection (45 mins)

**PRIORITY 3** (Enhancement): 5. ✅ Phase 3b.5: Text Analysis (30 mins) 6. ✅ Phase 3b.6: API Endpoints (45 mins)

**PRIORITY 4** (Finalization): 7. ✅ Phase 3b.7: Configuration (15 mins) 8. ✅ Phase 3b.8: Testing (30 mins)

**Total Estimated Time**: ~4 hours

---

## 🚀 Execution Strategy

### Step-by-Step Approach:

1. **Setup structure first** → Có foundation để build
2. **Audio processing next** → Core của voice analysis
3. **Add Whisper** → Transcription cần thiết
4. **Implement emotion** → Main feature
5. **Add text analysis** → Enhancement
6. **Build APIs** → User interface
7. **Configure & test** → Validation

### Incremental Testing:

- Test sau mỗi phase
- Verify output format
- Check performance

---

## ✅ Success Criteria for Phase 3b

- [ ] Voice service runs on port 8001
- [ ] Audio features extraction working
- [ ] Gender normalization implemented
- [ ] Whisper Vietnamese transcription working
- [ ] Emotion detection with hybrid approach
- [ ] Text analysis for Vietnamese
- [ ] POST /analyze endpoint functional
- [ ] GET /prompts endpoint functional
- [ ] File upload handling secure
- [ ] Error handling comprehensive
- [ ] All tests passing

---

## 📝 Next Steps After Phase 3b

**Phase 3c: AI Service Integration**

- Update assessments endpoint to accept `voice_analysis_id`
- Fetch voice data from voice-service
- Enhance Gemini prompt with voice insights
- Combined GAD-7 + voice analysis

**Phase 3d: Frontend Integration**

- Voice recording component
- Audio upload progress
- Results visualization

---

## 🎯 Let's Start!

**Beginning with Phase 3b.1: Structure Setup**

Ready to execute? 🚀
