# 🚀 Voice Service Deployment Guide

## 📋 Prerequisites

### System Requirements

- Python 3.10 or higher
- 4GB+ RAM (8GB recommended for Whisper)
- 2GB+ disk space for Whisper models
- FFmpeg (for audio processing)

### Install FFmpeg

**Windows** (PowerShell as Administrator):

```powershell
choco install ffmpeg
# or download from: https://ffmpeg.org/download.html
```

**macOS**:

```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian)**:

```bash
sudo apt-get update
sudo apt-get install ffmpeg libsndfile1
```

---

## 🔧 Installation

### 1. Clone Repository

```bash
cd ai4mind-app/voice-service
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# If pip install fails for some packages, try:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Download Whisper Model (Optional - auto-downloads on first use)

```bash
# Pre-download Whisper model to avoid delay on first request
python -c "import whisper; whisper.load_model('base')"
```

---

## ⚙️ Configuration

### 1. Create `.env` File

```bash
cp .env.example .env  # or create manually
```

### 2. Configure Environment Variables

Edit `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai4mind

# Service Configuration
PORT=8001
HOST=0.0.0.0
DEBUG=false

# Whisper Settings
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
WHISPER_LANGUAGE=vi  # Vietnamese

# File Storage
FILE_STORAGE_PATH=./storage/audio
MAX_FILE_SIZE_MB=10

# AI Service Integration
AI_SERVICE_URL=http://localhost:8000

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

### 3. Create Storage Directory

```bash
mkdir -p storage/audio/temp
mkdir -p storage/audio/permanent
```

---

## 🚀 Running the Service

### Development Mode

```bash
# Start with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Or use Python
python -m uvicorn app.main:app --reload --port 8001
```

### Production Mode

```bash
# Start with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4

# With Gunicorn (recommended for production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Check Service Health

```bash
# Health check
curl http://localhost:8001/health

# API documentation
open http://localhost:8001/docs
```

---

## 🧪 Testing

### 1. Run Component Tests

```bash
# Test all components
python test_integration.py

# Expected output: 5/5 tests passed
```

### 2. Test API Endpoints

**Get Voice Prompts:**

```bash
curl http://localhost:8001/api/v1/voice-analysis/prompts
```

**Analyze Voice (with audio file):**

```bash
curl -X POST http://localhost:8001/api/v1/voice-analysis/analyze \
  -F "file=@test_audio.wav" \
  -F "user_id=1" \
  -F "gender=female"
```

### 3. Interactive API Testing

Visit: http://localhost:8001/docs

---

## 📊 Monitoring

### View Logs

```bash
# Follow logs in real-time
tail -f logs/voice-service.log

# Filter errors only
tail -f logs/voice-service.log | grep ERROR
```

### Performance Metrics

- **Typical response time**: 3-5 seconds (audio 10-15 seconds)
- **Whisper transcription**: 1-2 seconds
- **Feature extraction**: 0.5-1 second
- **Emotion classification**: < 0.1 second

---

## 🐳 Docker Deployment (Optional)

### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download Whisper model
RUN python -c "import whisper; whisper.load_model('base')"

# Expose port
EXPOSE 8001

# Run service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. Build and Run

```bash
# Build image
docker build -t voice-service:latest .

# Run container
docker run -d \
  -p 8001:8001 \
  -v $(pwd)/storage:/app/storage \
  -e DATABASE_URL="postgresql://..." \
  --name voice-service \
  voice-service:latest
```

---

## 🔒 Security Considerations

### 1. File Upload Security

- Maximum file size: 10MB (configurable)
- Allowed formats: WAV, MP3, M4A, FLAC
- Temporary files automatically deleted
- File validation before processing

### 2. API Security (TODO - Phase 4)

- [ ] Add JWT authentication
- [ ] Rate limiting (10 requests/minute per user)
- [ ] Request validation
- [ ] CORS configuration

### 3. Data Privacy

- Audio files stored temporarily (deleted after processing)
- No audio storage by default
- GDPR compliance: user can request data deletion

---

## 🐛 Troubleshooting

### Issue: "FFmpeg not found"

**Solution:**

```bash
# Install FFmpeg (see Prerequisites section)
# Verify installation
ffmpeg -version
```

### Issue: "Whisper model download timeout"

**Solution:**

```bash
# Pre-download manually
python -c "import whisper; whisper.load_model('base')"

# Or use smaller model
# In .env: WHISPER_MODEL=tiny
```

### Issue: "CUDA out of memory" (GPU)

**Solution:**

```bash
# Force CPU mode (in code)
# whisper.load_model('base', device='cpu')

# Or use smaller model
WHISPER_MODEL=tiny
```

### Issue: "Port 8001 already in use"

**Solution:**

```bash
# Find and kill process
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows

# Or change port in .env
PORT=8002
```

---

## 📈 Performance Optimization

### 1. Whisper Model Selection

| Model  | Size  | Speed  | Accuracy   | Recommendation       |
| ------ | ----- | ------ | ---------- | -------------------- |
| tiny   | 39M   | ⚡⚡⚡ | ⭐⭐       | Development only     |
| base   | 74M   | ⚡⚡   | ⭐⭐⭐     | **Recommended**      |
| small  | 244M  | ⚡     | ⭐⭐⭐⭐   | High accuracy        |
| medium | 769M  | 🐌     | ⭐⭐⭐⭐⭐ | Vietnamese optimized |
| large  | 1550M | 🐌🐌   | ⭐⭐⭐⭐⭐ | Best but slow        |

### 2. Use GPU (if available)

```python
# Automatically uses GPU if available
# Requires: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Cache Whisper Model

```python
# Model loaded once at startup (already implemented)
# Reused for all requests
```

---

## 🔄 Integration with AI Service

### 1. Send Analysis Results to AI Service

```python
import httpx

async def send_to_ai_service(analysis_result):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AI_SERVICE_URL}/api/voice-analysis",
            json=analysis_result
        )
    return response.json()
```

### 2. Database Integration

- Voice analysis results stored in PostgreSQL
- Linked to user sessions
- Historical analysis tracking

---

## 📚 Next Steps

1. ✅ Deploy voice service
2. ⏳ Integrate with frontend
3. ⏳ Add authentication
4. ⏳ Set up monitoring (Prometheus + Grafana)
5. ⏳ Load testing
6. ⏳ Production deployment (Docker + Kubernetes)

---

## 🆘 Support

**Issues or questions?**

- Check logs: `logs/voice-service.log`
- API docs: http://localhost:8001/docs
- Integration tests: `python test_integration.py`

**Common Commands:**

```bash
# Restart service
uvicorn app.main:app --reload --port 8001

# Check service status
curl http://localhost:8001/health

# View recent logs
tail -n 100 logs/voice-service.log

# Test single component
python -m app.services.emotion_classifier
```
