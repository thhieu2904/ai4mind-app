# AI4Mind - Voice Analysis Service

Voice processing microservice sử dụng Whisper và emotion detection.

## 🚀 Setup

### 1. Tạo Conda Environment

```powershell
# Sử dụng Python 3.10 cho tương thích ML libraries
conda create -n ai4mind-voice python=3.10 -y
conda activate ai4mind-voice
```

### 2. Cài Dependencies

```powershell
pip install -r requirements.txt
```

**⚠️ Lưu ý:** PyTorch installation có thể mất 5-10 phút.

### 3. Download Whisper Models

```powershell
# Download base model (khuyến nghị cho development)
python -c "import whisper; whisper.load_model('base')"

# Các models khác:
# tiny - Fastest, least accurate
# base - Good balance (khuyến nghị)
# small - Better accuracy
# medium - High accuracy, slower
# large - Best accuracy, slowest
```

### 4. Chạy Server

```powershell
uvicorn app.main:app --reload --port 8001
```

## 📖 API Documentation

Sau khi chạy server, truy cập:

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🎤 Main Endpoints

### Transcribe Audio

```
POST /api/v1/transcribe
- Upload audio file
- Returns transcription text
```

### Analyze Emotion

```
POST /api/v1/analyze
- Upload audio file
- Returns emotion scores
```

## 🧪 Testing

```powershell
# Run tests
pytest

# Test với audio file mẫu
curl -X POST http://localhost:8001/api/v1/transcribe \
  -F "file=@test_audio.wav"
```

## 📁 Structure

```
voice-analysis/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   ├── models/              # ML model wrappers
│   ├── processors/          # Audio processing
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   └── main.py              # FastAPI app
├── models/                  # Pretrained model files
├── tests/                   # Test files
├── requirements.txt
└── Dockerfile
```

## 🎯 Supported Formats

Audio formats:

- WAV
- MP3
- M4A
- FLAC

Max file size: 50MB

## 🔧 Configuration

Environment variables:

- `WHISPER_MODEL` - Model size (default: base)
- `MAX_FILE_SIZE` - Max upload size (default: 50MB)
- `DEBUG` - Debug mode (default: False)

## 🚀 Performance Tips

1. **Model Selection:**

   - Development: `base` model
   - Production: `small` hoặc `medium`

2. **GPU Acceleration:**

   - Cài CUDA-enabled PyTorch nếu có GPU
   - https://pytorch.org/get-started/locally/

3. **Caching:**
   - Models được cache sau lần load đầu tiên
   - Audio features có thể cache với Redis
