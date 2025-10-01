# 🎙️ Voice Analysis Service - Architecture & Design

**Branch**: `voice-analysis`  
**Date**: 01/10/2025  
**Status**: 📋 Planning Phase

---

## 🎯 Mục tiêu tổng quan

Xây dựng microservice phân tích giọng nói để tăng cường độ chính xác của đánh giá tâm lý GAD-7 thông qua:

1. **Audio features** → Phát hiện cảm xúc từ đặc trưng âm thanh
2. **Speech-to-text** → Phân tích nội dung ngữ nghĩa
3. **Combined analysis** → Tích hợp với GAD-7 cho kết quả tốt hơn

---

## 📊 Yêu cầu chức năng

### 1. Ghi âm giọng nói (Frontend)

```
[User Interface]
- Nút "Ghi âm" với microphone icon
- Timer hiển thị thời lượng (max 60s)
- Câu hỏi định hướng: "Hãy chia sẻ về cảm xúc của bạn trong tuần qua"
- Preview audio trước khi gửi
- Support formats: WAV, MP3, M4A
```

### 2. Phân tích 2 luồng song song

#### Luồng A: Audio Feature Extraction → Emotion Detection

```python
Input: Audio file (WAV/MP3)

Processing Pipeline:
1. Load audio → librosa
2. Extract features:
   - Pitch (F0) - cao độ giọng
   - Energy/Intensity - năng lượng
   - Speech rate - tốc độ nói
   - Zero-crossing rate - độ biến thiên
   - MFCCs - đặc trưng mel-frequency
   - Spectral features - phổ tần số

3. Emotion classification:
   - Happy/Joy
   - Sad/Depressed
   - Anxious/Stressed
   - Angry/Frustrated
   - Neutral/Calm

Output:
{
  "emotion_scores": {
    "anxiety": 0.75,
    "sadness": 0.60,
    "neutral": 0.20,
    "anger": 0.10
  },
  "dominant_emotion": "anxiety",
  "confidence": 0.85,
  "audio_features": {
    "pitch_mean": 210.5,  # Hz
    "pitch_std": 45.2,
    "energy_mean": 0.65,
    "speech_rate": "fast",  # slow/normal/fast
    "pause_count": 12,
    "voice_stability": 0.45  # 0-1, lower = more unstable
  }
}
```

#### Luồng B: Speech-to-Text → Semantic Analysis

```python
Input: Audio file

Processing Pipeline:
1. Transcribe → OpenAI Whisper (Vietnamese)
2. Text analysis:
   - Keyword detection (lo lắng, sợ hãi, buồn, stress...)
   - Sentiment analysis
   - Topic extraction
   - Repetition detection (obsessive thoughts)

Output:
{
  "transcript": "Tuần này em cảm thấy rất lo lắng về...",
  "language": "vi",
  "duration_seconds": 45,
  "word_count": 120,
  "sentiment": {
    "polarity": -0.6,  # -1 to 1
    "subjectivity": 0.8  # 0 to 1
  },
  "keywords_detected": [
    {"word": "lo lắng", "count": 5, "weight": 0.8},
    {"word": "stress", "count": 3, "weight": 0.6}
  ],
  "psychological_markers": {
    "negative_words": 15,
    "positive_words": 3,
    "self_reference": 8,  # "tôi", "em", "mình"
    "uncertainty": 6  # "có thể", "không chắc"
  }
}
```

### 3. Câu hỏi định hướng (Prompts)

**Mục đích**: Hướng user nói về tâm trạng trong 30-60s

**Danh sách prompts:**

```typescript
const voicePrompts = [
  {
    id: 1,
    text: "Hãy chia sẻ về cảm xúc của bạn trong tuần qua. Bạn đang cảm thấy thế nào?",
    duration: 60,
    category: "general",
  },
  {
    id: 2,
    text: "Gần đây có điều gì khiến bạn lo lắng không? Hãy kể về nó.",
    duration: 45,
    category: "anxiety_focused",
  },
  {
    id: 3,
    text: "Kể về một ngày gần đây của bạn, từ khi thức dậy đến khi đi ngủ.",
    duration: 60,
    category: "daily_routine",
  },
  {
    id: 4,
    text: "Nếu bạn phải mô tả tâm trạng hiện tại bằng một màu sắc, đó sẽ là màu gì và tại sao?",
    duration: 45,
    category: "metaphorical",
  },
];
```

### 4. Tích hợp với GAD-7

**Flow tổng hợp:**

```
Step 1: Student làm GAD-7 assessment
        ↓
Step 2: (Optional) Upload voice recording
        ↓
Step 3: voice-analysis service phân tích
        ↓ (send to ai-service)
Step 4: ai-service combine data:
        - GAD-7 scores (objective)
        - Voice emotions (physiological)
        - Text content (subjective)
        ↓
Step 5: Enhanced Gemini prompt
        ↓
Step 6: Comprehensive analysis result
```

---

## ⚠️ VẤN ĐỀ GIỚI TÍNH (CRITICAL)

### Phân tích vấn đề

**Đặc trưng âm thanh khác biệt theo giới tính:**

| Feature     | Nam           | Nữ             | Impact                      |
| ----------- | ------------- | -------------- | --------------------------- |
| Pitch (F0)  | 85-180 Hz     | 165-255 Hz     | **HIGH** - Cơ bản của giọng |
| Formants    | Thấp hơn      | Cao hơn        | **MEDIUM** - Resonance khác |
| Intensity   | Cao hơn (avg) | Thấp hơn (avg) | **LOW** - Overlap nhiều     |
| Speech rate | Chậm hơn      | Nhanh hơn      | **LOW** - Không rõ ràng     |

**Rủi ro nếu KHÔNG normalize:**

```python
# Example bias without gender normalization:
male_voice = {
    "pitch_mean": 120,  # Hz
    "emotion": "calm"
}

female_voice = {
    "pitch_mean": 220,  # Hz
    "emotion": "anxious" ❌ FALSE POSITIVE!
    # Thực tế cũng calm nhưng pitch cao tự nhiên
}
```

### ✅ GIẢI PHÁP: Thêm Gender Field

**Cần update Student model:**

```python
class Student(Base):
    # ... existing fields ...

    # ADD THIS:
    gender = Column(String(10), nullable=True)  # 'male', 'female', 'other', 'prefer_not_to_say'

    # Relationships...
```

**Benefits:**

1. ✅ Normalize audio features theo baseline giới tính
2. ✅ Tăng độ chính xác emotion detection
3. ✅ Giảm false positives
4. ✅ Hỗ trợ personalized analysis
5. ✅ Research insights (gender differences in anxiety)

**Migration script:**

```sql
-- Add gender column to students table
ALTER TABLE students
ADD COLUMN gender VARCHAR(10) DEFAULT 'prefer_not_to_say';

-- Add check constraint
ALTER TABLE students
ADD CONSTRAINT check_gender
CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say'));
```

**Frontend form update:**

```typescript
// Add to student profile form
<RadioGroup label="Giới tính (tùy chọn)">
  <Radio value="male">Nam</Radio>
  <Radio value="female">Nữ</Radio>
  <Radio value="other">Khác</Radio>
  <Radio value="prefer_not_to_say">Không muốn tiết lộ</Radio>
</RadioGroup>
```

**Voice analysis normalization:**

```python
def normalize_audio_features(features: dict, gender: str) -> dict:
    """Normalize audio features based on gender"""

    # Gender-specific baselines
    baselines = {
        "male": {"pitch_mean": 130, "pitch_std": 40},
        "female": {"pitch_mean": 210, "pitch_std": 45},
        "other": {"pitch_mean": 170, "pitch_std": 50},  # Average
        "prefer_not_to_say": {"pitch_mean": 170, "pitch_std": 50}
    }

    baseline = baselines.get(gender, baselines["prefer_not_to_say"])

    # Normalize pitch to z-score
    normalized_pitch = (features["pitch_mean"] - baseline["pitch_mean"]) / baseline["pitch_std"]

    # Use normalized value for emotion detection
    return {
        **features,
        "normalized_pitch": normalized_pitch,
        "pitch_deviation": abs(normalized_pitch)  # How much deviation from normal
    }
```

---

## 🏗️ Kiến trúc Microservice

### Service Structure

```
ai4mind-app/
├── ai-service/              # Existing FastAPI service
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── assessments.py
│   │   │   └── voice.py  # NEW: Voice integration endpoint
│   │   └── services/
│   │       └── gemini_service.py
│   └── .env
│
└── voice-service/           # NEW: Voice analysis microservice
    ├── app/
    │   ├── main.py
    │   ├── api/
    │   │   └── v1/
    │   │       └── endpoints/
    │   │           ├── analyze.py    # POST /analyze
    │   │           └── prompts.py    # GET /prompts
    │   ├── models/
    │   │   ├── voice_analysis.py  # SQLAlchemy model
    │   │   └── audio_processing.py
    │   ├── services/
    │   │   ├── whisper_service.py     # Speech-to-text
    │   │   ├── audio_features.py      # Feature extraction
    │   │   └── emotion_classifier.py  # Emotion detection
    │   └── ml_models/
    │       ├── emotion_model.pkl      # Pre-trained model
    │       └── model_loader.py
    ├── requirements.txt
    ├── Dockerfile
    └── .env
```

### Database Schema

**New table: `voice_analyses`**

```sql
CREATE TABLE voice_analyses (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    assessment_id INTEGER REFERENCES assessments(id) ON DELETE SET NULL,

    -- File info
    audio_file_path VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER,
    duration_seconds FLOAT,
    format VARCHAR(10),  -- 'wav', 'mp3', 'm4a'

    -- Prompt used
    prompt_id INTEGER,
    prompt_text TEXT,

    -- Transcription
    transcript TEXT,
    language VARCHAR(10) DEFAULT 'vi',
    word_count INTEGER,

    -- Audio features (JSONB for flexibility)
    audio_features JSONB,  -- {pitch_mean, energy, speech_rate, etc.}

    -- Emotion analysis
    emotion_scores JSONB,  -- {anxiety: 0.75, sadness: 0.60, ...}
    dominant_emotion VARCHAR(50),
    confidence FLOAT,

    -- Text analysis
    sentiment_score FLOAT,  -- -1 to 1
    keywords JSONB,  -- [{word, count, weight}, ...]
    psychological_markers JSONB,

    -- Gender-normalized features
    gender_used VARCHAR(10),  -- For normalization reference
    normalized_features JSONB,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    error_message TEXT,

    -- Indexes
    INDEX idx_student_id (student_id),
    INDEX idx_assessment_id (assessment_id),
    INDEX idx_created_at (created_at),
    INDEX idx_dominant_emotion (dominant_emotion)
);
```

### API Contracts

**Voice Service → AI Service Communication**

**1. POST /api/v1/voice-analysis/analyze**

```typescript
// Request (multipart/form-data)
{
  student_id: number
  audio_file: File
  prompt_id?: number
  assessment_id?: number  // Optional link to GAD-7
}

// Response
{
  analysis_id: number
  transcript: string
  emotion_analysis: {
    dominant_emotion: string
    confidence: number
    scores: {
      anxiety: number
      sadness: number
      anger: number
      neutral: number
    }
  }
  audio_features: {
    pitch_mean: number
    pitch_std: number
    energy_mean: number
    speech_rate: string
    pause_count: number
    voice_stability: number
  }
  text_analysis: {
    sentiment: number
    keywords: Array<{word: string, count: number, weight: number}>
    psychological_markers: {
      negative_words: number
      positive_words: number
      self_reference: number
      uncertainty: number
    }
  }
  duration_seconds: number
  processing_time_ms: number
}
```

**2. GET /api/v1/voice-analysis/prompts**

```typescript
// Response
{
  prompts: Array<{
    id: number;
    text: string;
    duration_seconds: number;
    category: string;
    language: string;
  }>;
}
```

**3. GET /api/v1/voice-analysis/{analysis_id}**

```typescript
// Response: Same as analyze endpoint + metadata
{
  id: number
  student_id: number
  assessment_id?: number
  created_at: string
  // ... all analysis data
}
```

**AI Service Integration Endpoint**

**POST /api/v1/assessments/ (Enhanced)**

```typescript
// Request
{
  answers: number[]  // GAD-7 answers
  functional_impairment?: number
  notes?: string
  voice_analysis_id?: number  // NEW: Link to voice analysis
}

// If voice_analysis_id provided:
// 1. Fetch voice analysis from voice-service
// 2. Enhance Gemini prompt with voice data
// 3. Return comprehensive analysis
```

---

## 🤖 ML Models & Tools

### 1. Speech-to-Text: OpenAI Whisper

```python
# Why Whisper?
✅ Best Vietnamese support
✅ Open-source & free
✅ Multiple model sizes (tiny → large)
✅ High accuracy (~95% for Vietnamese)
✅ Easy integration

# Model selection
- Development: whisper-base (74M params)
- Production: whisper-medium (769M params)
- High accuracy: whisper-large (1550M params)

# Installation
pip install openai-whisper
```

### 2. Audio Feature Extraction: librosa

```python
# Why librosa?
✅ Industry standard for audio analysis
✅ Comprehensive feature extraction
✅ Well-documented
✅ Good performance

# Key features to extract
- pitch (F0) - fundamental frequency
- MFCCs - mel-frequency cepstral coefficients
- Spectral features - centroid, bandwidth, rolloff
- Energy/RMS - root mean square energy
- Zero-crossing rate
- Chroma features

# Installation
pip install librosa soundfile
```

### 3. Emotion Detection: Custom Model

**Option A: Transfer Learning (Recommended)**

```python
# Base: Pre-trained emotion model
# Dataset: RAVDESS, CREMA-D, IEMOCAP
# Fine-tune: Vietnamese audio samples (if available)

# Architecture
- Input: MFCC features (40 coefficients)
- CNN layers for feature learning
- LSTM for temporal patterns
- Dense layers for classification
- Output: 5 emotions (anxiety, sadness, anger, joy, neutral)

# Libraries
import tensorflow as tf
from tensorflow.keras import layers, models
```

**Option B: Rule-based + ML Hybrid**

```python
def detect_emotion_hybrid(features, gender):
    """
    Combine rule-based and ML prediction
    """
    # Rule-based indicators
    rules_score = {
        "anxiety": 0.0,
        "sadness": 0.0,
        "anger": 0.0,
        "neutral": 0.0
    }

    # Anxiety indicators
    if features["speech_rate"] == "fast":
        rules_score["anxiety"] += 0.3
    if features["pitch_std"] > threshold:
        rules_score["anxiety"] += 0.2
    if features["pause_count"] > 15:
        rules_score["anxiety"] += 0.2

    # ML prediction
    ml_score = emotion_model.predict(features)

    # Weighted combination
    final_score = 0.4 * rules_score + 0.6 * ml_score

    return final_score
```

### 4. Sentiment Analysis: PhoBERT (Vietnamese)

```python
# For text analysis after transcription
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "vinai/phobert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Fine-tune for Vietnamese sentiment
# Dataset: UIT-VSFC (Vietnamese Students' Feedback Corpus)
```

---

## 📐 Gender Normalization Algorithm

```python
class GenderAwareAudioAnalyzer:
    """
    Audio analyzer với gender normalization
    """

    # Gender-specific baselines (from research)
    BASELINES = {
        "male": {
            "pitch_mean": 130,  # Hz
            "pitch_std": 40,
            "pitch_range": (85, 180),
            "formant_f1": 730,
            "formant_f2": 1090
        },
        "female": {
            "pitch_mean": 210,
            "pitch_std": 45,
            "pitch_range": (165, 255),
            "formant_f1": 850,
            "formant_f2": 2050
        },
        "other": {  # Use average
            "pitch_mean": 170,
            "pitch_std": 50,
            "pitch_range": (85, 255),
            "formant_f1": 790,
            "formant_f2": 1570
        }
    }

    def normalize_features(self, features: dict, gender: str) -> dict:
        """
        Normalize audio features based on gender baseline

        Args:
            features: Raw audio features
            gender: 'male', 'female', 'other', 'prefer_not_to_say'

        Returns:
            Normalized features for fair emotion comparison
        """
        # Default to 'other' if not specified
        if gender == 'prefer_not_to_say':
            gender = 'other'

        baseline = self.BASELINES[gender]

        # Z-score normalization for pitch
        pitch_z = (features["pitch_mean"] - baseline["pitch_mean"]) / baseline["pitch_std"]

        # Relative deviation (more interpretable)
        pitch_deviation = abs(pitch_z)  # 0 = normal, >2 = abnormal

        # Pitch variability (independent of gender)
        pitch_cv = features["pitch_std"] / features["pitch_mean"]  # Coefficient of variation

        # Energy normalization (less gender-dependent)
        energy_relative = features["energy_mean"] / features["energy_max"]

        return {
            "pitch_z_score": pitch_z,
            "pitch_deviation": pitch_deviation,
            "pitch_variability": pitch_cv,
            "energy_relative": energy_relative,
            "speech_rate": features["speech_rate"],
            "pause_count": features["pause_count"],
            # Keep original for reference
            "raw_pitch_mean": features["pitch_mean"],
            "gender_baseline": gender
        }

    def detect_emotion_with_normalization(self, raw_features, gender):
        """
        Emotion detection using normalized features
        """
        # Normalize first
        normalized = self.normalize_features(raw_features, gender)

        # Use normalized features for emotion detection
        emotion_scores = {
            "anxiety": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "neutral": 1.0
        }

        # Anxiety indicators (gender-neutral after normalization)
        if normalized["pitch_deviation"] > 1.5:  # 1.5 SD from normal
            emotion_scores["anxiety"] += 0.3

        if normalized["pitch_variability"] > 0.25:  # High variation
            emotion_scores["anxiety"] += 0.2

        if raw_features["pause_count"] > 15:
            emotion_scores["anxiety"] += 0.2

        if raw_features["speech_rate"] == "fast":
            emotion_scores["anxiety"] += 0.2

        # Sadness indicators
        if normalized["pitch_z_score"] < -1.0:  # Lower than normal
            emotion_scores["sadness"] += 0.3

        if normalized["energy_relative"] < 0.3:  # Low energy
            emotion_scores["sadness"] += 0.3

        if raw_features["speech_rate"] == "slow":
            emotion_scores["sadness"] += 0.2

        # Normalize scores to sum to 1
        total = sum(emotion_scores.values())
        emotion_scores = {k: v/total for k, v in emotion_scores.items()}

        return {
            "scores": emotion_scores,
            "dominant": max(emotion_scores, key=emotion_scores.get),
            "confidence": max(emotion_scores.values()),
            "normalized_features": normalized
        }
```

---

## 🔄 Integration Flow (Detailed)

### Scenario 1: GAD-7 + Voice Analysis

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. User fills GAD-7 questionnaire                          │
│     answers: [2, 2, 2, 1, 2, 2, 1] → Score: 12             │
│                                                              │
│  2. [Optional] Voice recording prompt appears                │
│     "Bạn có muốn chia sẻ thêm qua giọng nói không?"        │
│                                                              │
│  3. If YES:                                                  │
│     → Show prompt: "Hãy chia sẻ cảm xúc trong tuần qua"   │
│     → Record audio (max 60s)                                │
│     → Upload to voice-service                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ VOICE-SERVICE (FastAPI - Port 8001)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  POST /api/v1/voice-analysis/analyze                        │
│                                                              │
│  4. Receive audio file                                       │
│     → Save to storage: /shared/audio-files/{id}.wav        │
│     → Create voice_analysis record (status: processing)     │
│                                                              │
│  5. PARALLEL PROCESSING:                                     │
│                                                              │
│     ┌─────────────────────┐  ┌──────────────────────┐     │
│     │ LUỒNG A:            │  │ LUỒNG B:              │     │
│     │ Audio Features      │  │ Speech-to-Text        │     │
│     └─────────────────────┘  └──────────────────────┘     │
│              │                         │                    │
│              ↓                         ↓                    │
│     • Load audio (librosa)    • Whisper transcribe         │
│     • Extract pitch           • Get Vietnamese text        │
│     • Extract energy          • Word count                 │
│     • Calculate speech rate   • Duration                   │
│     • Count pauses            │                            │
│     • Get MFCCs              │                            │
│              │                         │                    │
│              ↓                         ↓                    │
│     • Fetch student.gender    • PhoBERT sentiment         │
│     • Normalize features      • Keyword extraction         │
│     • Detect emotions         • Psych markers             │
│              │                         │                    │
│              └─────────┬───────────────┘                   │
│                        ↓                                     │
│  6. Combine results                                         │
│     {                                                        │
│       transcript: "...",                                     │
│       emotion_scores: {...},                                │
│       audio_features: {...},                                │
│       text_analysis: {...}                                  │
│     }                                                        │
│                                                              │
│  7. Update voice_analysis record (status: completed)        │
│                                                              │
│  8. Return analysis_id to frontend                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND continues...                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  9. Submit GAD-7 + voice_analysis_id to ai-service          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ AI-SERVICE (FastAPI - Port 8000)                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  POST /api/v1/assessments/                                  │
│  {                                                           │
│    answers: [2,2,2,1,2,2,1],                               │
│    voice_analysis_id: 123                                   │
│  }                                                           │
│                                                              │
│  10. Fetch voice analysis from voice-service                │
│      GET http://voice-service:8001/api/v1/voice-analysis/123│
│                                                              │
│  11. Build ENHANCED Gemini prompt:                          │
│      ┌──────────────────────────────────────────┐          │
│      │ GAD-7 Data:                              │          │
│      │   Score: 12/21 (moderate anxiety)        │          │
│      │   Answers: [2,2,2,1,2,2,1]              │          │
│      │                                           │          │
│      │ Voice Analysis:                           │          │
│      │   Transcript: "Tuần này em cảm thấy...  │          │
│      │   Emotion: anxiety (75%), sadness (60%)  │          │
│      │   Audio: fast speech, high pitch var     │          │
│      │   Text: 15 negative words, 8 self-refs  │          │
│      │                                           │          │
│      │ Request: Phân tích tổng hợp...          │          │
│      └──────────────────────────────────────────┘          │
│                                                              │
│  12. Send to Gemini AI                                      │
│                                                              │
│  13. Get comprehensive analysis (Vietnamese)                │
│      - Phân tích: "Dựa vào kết quả GAD-7 và giọng nói..." │
│      - Khuyến nghị: [1. ..., 2. ..., 3. ...]              │
│                                                              │
│  14. Save assessment to database                            │
│                                                              │
│  15. Return to frontend                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND displays results                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  • GAD-7 score: 12/21 (Moderate)                           │
│  • Voice emotion: Anxiety detected                          │
│  • Comprehensive AI analysis                                │
│  • Personalized recommendations                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 TODO: Implementation Checklist

### Phase 3a: Database & Models (1 day)

- [ ] Add `gender` field to Student model
- [ ] Create migration script for students table
- [ ] Create `voice_analyses` table schema
- [ ] Run migrations on dev database
- [ ] Update seed data script với gender values

### Phase 3b: Voice Service Setup (2 days)

- [ ] Create voice-service/ directory structure
- [ ] Setup FastAPI application
- [ ] Install dependencies (whisper, librosa, transformers)
- [ ] Create database models
- [ ] Implement file upload handling
- [ ] Setup storage for audio files

### Phase 3c: Audio Processing (2 days)

- [ ] Implement Whisper speech-to-text
- [ ] Implement librosa feature extraction
- [ ] Create gender normalization logic
- [ ] Implement emotion detection (hybrid approach)
- [ ] Add PhoBERT sentiment analysis
- [ ] Create keyword extraction

### Phase 3d: API Endpoints (1 day)

- [ ] POST /analyze endpoint
- [ ] GET /prompts endpoint
- [ ] GET /{analysis_id} endpoint
- [ ] Add error handling
- [ ] Add request validation
- [ ] Add response formatting

### Phase 3e: AI Service Integration (1 day)

- [ ] Add voice integration endpoint to ai-service
- [ ] Implement voice data fetching
- [ ] Enhance Gemini prompt template
- [ ] Test combined analysis
- [ ] Update assessment response schema

### Phase 3f: Testing (1 day)

- [ ] Unit tests for audio processing
- [ ] Integration tests for API endpoints
- [ ] Test gender normalization accuracy
- [ ] Test voice + GAD-7 combination
- [ ] Load testing for audio processing

### Phase 3g: Frontend (2 days)

- [ ] Voice recording component
- [ ] Prompt display
- [ ] Audio upload progress
- [ ] Results visualization
- [ ] Gender selection in profile

**Total Estimated Time: 10 days (2 weeks)**

---

## 🎯 Success Metrics

1. **Accuracy**

   - Whisper transcription: >90% accuracy
   - Emotion detection: >75% accuracy
   - Combined analysis: >80% user satisfaction

2. **Performance**

   - Audio processing: <10 seconds for 60s audio
   - Voice analysis API: <15 seconds total
   - Combined assessment: <20 seconds total

3. **Quality**
   - Gender bias reduction: <10% difference between genders
   - False positive rate: <15%
   - User completion rate: >60% opt-in for voice

---

## 📚 References & Research

1. **Audio Feature Research:**

   - "Speech Emotion Recognition: A Review" (IEEE, 2020)
   - "Gender Differences in Acoustic Parameters" (JASA, 2019)

2. **Vietnamese NLP:**

   - PhoBERT: Pre-trained language model for Vietnamese
   - UIT-VSFC: Vietnamese sentiment corpus

3. **Clinical Psychology:**
   - GAD-7 validation studies
   - Voice biomarkers for anxiety detection

---

**Next Steps:**

1. ✅ Review and approve architecture
2. ⚠️ **CRITICAL: Add gender field to Student model**
3. 🔨 Begin implementation (voice-service setup)
