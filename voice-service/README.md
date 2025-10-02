# Voice Analysis Service

Microservice for voice recording analysis with gender-aware emotion detection.

## Features

- 🎙️ Audio feature extraction (pitch, energy, speech rate)
- 🗣️ Vietnamese speech-to-text (Whisper)
- 😊 Emotion detection (anxiety, sadness, anger, neutral)
- 📝 Text analysis & sentiment
- ⚖️ Gender-aware normalization
- 🔗 Integration with ai-service

## Tech Stack

- FastAPI
- OpenAI Whisper (Vietnamese STT)
- librosa (audio processing)
- NumPy, SoundFile

## Installation

```bash
cd voice-service
pip install -r requirements.txt
```

## Configuration

Create `.env` file:

```
DATABASE_URL=postgresql://...
AI_SERVICE_URL=http://localhost:8000
FILE_STORAGE_PATH=./storage/audio
WHISPER_MODEL=base
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### Health Check

```
GET /health
```

### Analyze Voice

```
POST /api/v1/voice-analysis/analyze
Content-Type: multipart/form-data

Parameters:
- audio_file: File (WAV/MP3/M4A)
- student_id: int
- assessment_id: int (optional)
- prompt_id: int (optional)
```

### Get Prompts

```
GET /api/v1/voice-analysis/prompts
```

## Gender Normalization

Voice pitch varies significantly by gender:

- Male: 85-180 Hz
- Female: 165-255 Hz

We normalize features to avoid bias in emotion detection.

## Architecture

```
voice-service/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── core/
│   │   ├── config.py             # Configuration
│   │   └── constants.py          # Prompts, baselines
│   ├── api/v1/endpoints/
│   │   ├── analyze.py            # POST /analyze
│   │   └── prompts.py            # GET /prompts
│   ├── services/
│   │   ├── audio_processor.py    # librosa features
│   │   ├── whisper_service.py    # Speech-to-text
│   │   ├── emotion_classifier.py # Emotion detection
│   │   └── text_analyzer.py      # Vietnamese NLP
│   └── utils/
│       ├── file_handler.py       # File operations
│       └── gender_normalizer.py  # Normalization
└── requirements.txt
```

## Testing

```bash
python -m pytest tests/
```
