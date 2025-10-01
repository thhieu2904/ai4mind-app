# AI4Mind - AI Service (API Gateway)

Backend API Gateway cho AI4Mind platform.

## 🚀 Setup

### 1. Tạo Conda Environment

```powershell
conda create -n ai4mind-ai-service python=3.11 -y
conda activate ai4mind-ai-service
```

### 2. Cài Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configuration

```powershell
# Copy .env từ root project
Copy-Item ..\.env .env

# Hoặc tạo .env mới
Copy-Item ..\.env.example .env
# Sau đó edit .env với các giá trị thật
```

### 4. Database Migration

```powershell
# Init Alembic (chỉ lần đầu)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 5. Chạy Server

```powershell
uvicorn app.main:app --reload --port 8000
```

## 📖 API Documentation

Sau khi chạy server, truy cập:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## 📁 Structure

```
ai-service/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   ├── core/                # Config, security
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   └── main.py              # FastAPI app
├── alembic/                 # Database migrations
├── tests/                   # Test files
├── requirements.txt
└── Dockerfile
```

## 🔑 Environment Variables

Required:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT tokens
- `GEMINI_API_KEY` - Google Gemini API key

Optional:

- `REDIS_URL` - Redis connection (default: localhost:6379)
- `VOICE_SERVICE_URL` - Voice analysis service URL
- `DEBUG` - Debug mode (default: False)

## 🔗 Services

This service communicates with:

- **Database:** PostgreSQL (Supabase)
- **Cache:** Redis
- **Voice Analysis:** HTTP client to voice service
- **External API:** Google Gemini AI
