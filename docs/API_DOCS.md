# 📡 Voice Analysis API Documentation

## Base URL

```
http://localhost:8001
```

## Authentication

Currently no authentication (will be added in Phase 4)

---

## Endpoints

### 1. Health Check

Check if service is running.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "service": "Voice Analysis Service",
  "version": "1.0.0",
  "timestamp": "2025-10-01T10:30:00",
  "whisper_model": "base"
}
```

---

### 2. Get Voice Prompts

Get Vietnamese recording prompts for users.

**Endpoint:** `GET /api/v1/voice-analysis/prompts`

**Response:**

```json
{
  "prompts": [
    {
      "id": 1,
      "text": "Hãy chia sẻ về cảm xúc của bạn trong tuần qua. Bạn đang cảm thấy thế nào?",
      "duration_estimate": 15,
      "category": "daily"
    },
    {
      "id": 2,
      "text": "Gần đây có điều gì khiến bạn lo lắng không? Hãy kể về nó.",
      "duration_estimate": 15,
      "category": "emotion"
    }
  ],
  "total": 5
}
```

---

### 3. Analyze Voice Recording

**Main endpoint:** Analyze audio file for emotions, transcript, and psychological markers.

**Endpoint:** `POST /api/v1/voice-analysis/analyze`

**Content-Type:** `multipart/form-data`

**Request Parameters:**

| Parameter   | Type    | Required | Description                               |
| ----------- | ------- | -------- | ----------------------------------------- |
| `file`      | File    | ✅       | Audio file (WAV, MP3, M4A, max 10MB)      |
| `user_id`   | Integer | ✅       | User identifier                           |
| `gender`    | String  | ✅       | User gender: `male`, `female`, or `other` |
| `prompt_id` | Integer | ❌       | Optional recording prompt ID              |

**Example Request (cURL):**

```bash
curl -X POST http://localhost:8001/api/v1/voice-analysis/analyze \
  -F "file=@recording.wav" \
  -F "user_id=123" \
  -F "gender=female" \
  -F "prompt_id=1"
```

**Example Request (Python):**

```python
import requests

url = "http://localhost:8001/api/v1/voice-analysis/analyze"

files = {
    'file': open('recording.wav', 'rb')
}

data = {
    'user_id': 123,
    'gender': 'female',
    'prompt_id': 1
}

response = requests.post(url, files=files, data=data)
result = response.json()
```

**Example Request (JavaScript/Fetch):**

```javascript
const formData = new FormData();
formData.append("file", audioFile); // File object from <input type="file">
formData.append("user_id", "123");
formData.append("gender", "female");
formData.append("prompt_id", "1");

const response = await fetch(
  "http://localhost:8001/api/v1/voice-analysis/analyze",
  {
    method: "POST",
    body: formData,
  }
);

const result = await response.json();
```

**Success Response (200 OK):**

```json
{
  "analysis_id": "voice_a1b2c3d4e5f6",
  "user_id": 123,
  "timestamp": "2025-10-01T10:30:00",

  "audio_features": {
    "pitch_mean": 220.5,
    "pitch_std": 45.2,
    "pitch_min": 180.0,
    "pitch_max": 280.0,
    "energy_mean": 0.15,
    "energy_std": 0.08,
    "speech_rate": 3.8,
    "pause_count": 5,
    "pause_duration": 2.5,
    "voice_stability": 0.65,
    "duration": 15.5
  },

  "normalized_features": {
    "pitch_z_score": 0.233,
    "pitch_deviation": 0.233,
    "pitch_variability": 0.205,
    "energy_relative": 1.12,
    "speech_rate": 3.8,
    "pause_ratio": 0.161,
    "voice_stability": 0.65,
    "severity": "normal"
  },

  "transcript": {
    "transcript": "Tôi đang cảm thấy lo lắng về công việc. Không biết mình có làm tốt được không.",
    "language": "vi",
    "duration": 15.5,
    "confidence": 0.92,
    "word_count": 14
  },

  "emotion_result": {
    "primary_emotion": "anxiety",
    "intensity": "moderate",
    "confidence": 0.78,
    "emotion_scores": [
      {
        "emotion": "anxiety",
        "confidence": 0.78,
        "intensity": "moderate",
        "contributing_factors": [
          "High pitch (Z=1.8)",
          "Fast speech (5.2 syl/s)",
          "Frequent pauses (35%)"
        ]
      },
      {
        "emotion": "neutral",
        "confidence": 0.5,
        "intensity": "mild",
        "contributing_factors": ["Normal energy"]
      },
      {
        "emotion": "sadness",
        "confidence": 0.25,
        "intensity": "low",
        "contributing_factors": []
      },
      {
        "emotion": "anger",
        "confidence": 0.1,
        "intensity": "low",
        "contributing_factors": []
      }
    ],
    "summary": "Primary emotion: ANXIETY (moderate intensity, 78% confidence) | Key indicators: High pitch, Fast speech, Frequent pauses",
    "contributing_factors": [
      "High pitch (Z=1.8)",
      "Fast speech (5.2 syl/s)",
      "Frequent pauses (35%)"
    ]
  },

  "text_analysis": {
    "sentiment": -0.67,
    "emotion_keywords": {
      "anxiety": {
        "count": 3,
        "keywords": ["lo lắng", "không biết", "không chắc"]
      },
      "sadness": {
        "count": 0,
        "keywords": []
      },
      "anger": {
        "count": 0,
        "keywords": []
      },
      "positive": {
        "count": 0,
        "keywords": []
      }
    },
    "psychological_markers": {
      "self_reference": {
        "count": 3,
        "normalized": 21.43,
        "keywords": ["tôi", "mình", "tôi"]
      },
      "uncertainty": {
        "count": 2,
        "normalized": 14.29,
        "keywords": ["không biết", "không chắc"]
      },
      "negation": {
        "count": 2,
        "normalized": 14.29,
        "keywords": ["không", "không"]
      },
      "intensity": {
        "count": 0,
        "normalized": 0.0,
        "keywords": []
      }
    },
    "text_stats": {
      "word_count": 14,
      "sentence_count": 2,
      "char_count": 89,
      "avg_word_length": 6.36,
      "avg_sentence_length": 7.0
    },
    "dominant_emotion": "anxiety",
    "summary": "Sentiment: negative (-0.67) | Dominant emotion: anxiety (3 keywords) | Markers: high self-focus, uncertainty"
  },

  "gender": "female",
  "audio_duration": 15.5,
  "processing_time": 3.42
}
```

**Error Responses:**

**400 Bad Request** - Invalid input

```json
{
  "error": "Invalid file format",
  "detail": "Invalid file format. Allowed: .wav, .mp3, .m4a, .flac, .ogg",
  "timestamp": "2025-10-01T10:30:00"
}
```

**413 Payload Too Large** - File too large

```json
{
  "error": "File too large",
  "detail": "File size exceeds 10MB limit",
  "timestamp": "2025-10-01T10:30:00"
}
```

**500 Internal Server Error** - Processing failed

```json
{
  "error": "Processing failed",
  "detail": "Voice analysis failed: [error details]",
  "timestamp": "2025-10-01T10:30:00"
}
```

---

## Response Field Descriptions

### Audio Features (Raw)

| Field             | Type    | Description       | Unit             |
| ----------------- | ------- | ----------------- | ---------------- |
| `pitch_mean`      | Float   | Average pitch     | Hz               |
| `pitch_std`       | Float   | Pitch variation   | Hz               |
| `pitch_min/max`   | Float   | Pitch range       | Hz               |
| `energy_mean`     | Float   | Average energy    | 0-1              |
| `speech_rate`     | Float   | Speaking speed    | syllables/second |
| `pause_count`     | Integer | Number of pauses  | count            |
| `voice_stability` | Float   | Voice consistency | 0-1              |

### Normalized Features (Gender-Aware)

| Field               | Type   | Description                          | Interpretation                                |
| ------------------- | ------ | ------------------------------------ | --------------------------------------------- |
| `pitch_z_score`     | Float  | Pitch deviation from gender baseline | ±0-1: normal, ±1-2: moderate, ±2+: severe     |
| `pitch_variability` | Float  | Normalized pitch variation           | <0.1: monotone, 0.1-0.25: normal, >0.25: high |
| `energy_relative`   | Float  | Energy relative to baseline          | 0.8-1.2: normal, <0.8: low, >1.2: high        |
| `severity`          | String | Overall deviation severity           | normal/mild/moderate/severe                   |

### Emotion Result

| Field                  | Type   | Description           |
| ---------------------- | ------ | --------------------- | --------------------------------- |
| `primary_emotion`      | String | Main detected emotion | anxiety/sadness/anger/neutral     |
| `intensity`            | String | Emotion strength      | low/moderate/high/severe          |
| `confidence`           | Float  | Detection confidence  | 0.0-1.0                           |
| `contributing_factors` | Array  | Key indicators        | e.g., "High pitch", "Fast speech" |

### Text Analysis

| Field                   | Type   | Description             | Range                              |
| ----------------------- | ------ | ----------------------- | ---------------------------------- |
| `sentiment`             | Float  | Overall sentiment       | -1.0 (negative) to +1.0 (positive) |
| `emotion_keywords`      | Object | Detected emotion words  | Count + list                       |
| `psychological_markers` | Object | Mental state indicators | Self-focus, uncertainty, etc.      |

---

## Rate Limits (Future)

- **Development**: No limit
- **Production**: 10 requests/minute per user

---

## Best Practices

### 1. Audio File Preparation

- **Format**: WAV 16kHz mono (best quality)
- **Duration**: 10-30 seconds (optimal)
- **Quality**: Clear speech, minimal background noise
- **Size**: < 10MB

### 2. Gender Field

- **Critical**: Affects pitch normalization (±50% difference!)
- **Options**: `male`, `female`, `other`
- **Default**: `other` (if unknown)

### 3. Error Handling

```javascript
try {
  const response = await analyzeVoice(audioFile);

  if (response.status === 200) {
    // Process result
    console.log("Emotion:", response.emotion_result.primary_emotion);
  }
} catch (error) {
  if (error.status === 400) {
    console.error("Invalid input:", error.detail);
  } else if (error.status === 413) {
    console.error("File too large");
  } else {
    console.error("Server error:", error);
  }
}
```

### 4. Processing Time

- Typical: 3-5 seconds
- Depends on:
  - Audio duration
  - Whisper model size
  - Server load

---

## WebSocket Support (Future)

Real-time streaming analysis (Phase 4)

```javascript
const ws = new WebSocket("ws://localhost:8001/ws/voice-analysis");

ws.onopen = () => {
  // Send audio chunks
  audioStream.on("data", (chunk) => {
    ws.send(chunk);
  });
};

ws.onmessage = (event) => {
  const partial_result = JSON.parse(event.data);
  console.log("Partial transcript:", partial_result.text);
};
```

---

## Examples

### Full Workflow Example

```python
import requests
import json

# 1. Get prompts
prompts_response = requests.get('http://localhost:8001/api/v1/voice-analysis/prompts')
prompts = prompts_response.json()['prompts']

# 2. User records audio with prompt
prompt = prompts[0]
print(f"User prompt: {prompt['text']}")

# 3. Send recording for analysis
files = {'file': open('user_recording.wav', 'rb')}
data = {
    'user_id': 123,
    'gender': 'female',
    'prompt_id': prompt['id']
}

analysis_response = requests.post(
    'http://localhost:8001/api/v1/voice-analysis/analyze',
    files=files,
    data=data
)

result = analysis_response.json()

# 4. Process results
print(f"\n📊 Analysis Results:")
print(f"Emotion: {result['emotion_result']['primary_emotion']} ({result['emotion_result']['intensity']})")
print(f"Confidence: {result['emotion_result']['confidence']:.0%}")
print(f"Transcript: {result['transcript']['transcript']}")
print(f"Sentiment: {result['text_analysis']['sentiment']:.2f}")

# 5. Send to AI service for further processing
# (Integration with ai-service)
```

---

## Testing with cURL

```bash
# Health check
curl http://localhost:8001/health

# Get prompts
curl http://localhost:8001/api/v1/voice-analysis/prompts | json_pp

# Analyze voice (replace with your audio file)
curl -X POST http://localhost:8001/api/v1/voice-analysis/analyze \
  -F "file=@test.wav" \
  -F "user_id=1" \
  -F "gender=female" \
  | json_pp
```

---

## Interactive Documentation

Visit: **http://localhost:8001/docs**

FastAPI automatic interactive API docs (Swagger UI)
