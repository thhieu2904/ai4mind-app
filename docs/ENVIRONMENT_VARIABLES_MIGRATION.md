# 🌐 Environment Variables Migration Plan

**Date**: October 2, 2025  
**Purpose**: Convert hardcoded URLs to environment variables for cloud deployment

---

## 📋 Current Issues

### **Hardcoded Values Found:**

1. **ai-service/app/core/config.py**:

   - `VOICE_SERVICE_URL: str = "http://localhost:8001"` ✅ Already using env var
   - `CORS_ORIGINS` hardcoded list with localhost

2. **voice-service/app/core/config.py**:

   - `AI_SERVICE_URL: str = "http://localhost:8000"` ✅ Already using env var

3. **ai-service/app/api/v1/endpoints/combined_assessment.py**:
   - Uses `settings.VOICE_SERVICE_URL` ✅ Already correct
   - Has fallback to `"http://localhost:8001"` ⚠️ Should remove fallback for production

---

## 🎯 Migration Strategy

### **Phase 1: Update Config Classes** ✅ (Already Done)

Both services already read from environment variables:

- ✅ `VOICE_SERVICE_URL` in ai-service
- ✅ `AI_SERVICE_URL` in voice-service
- ✅ `DATABASE_URL` in both services
- ✅ `SUPABASE_PROJECT_URL` in ai-service

### **Phase 2: Fix CORS Origins**

**Current (Hardcoded):**

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001"
]
```

**Target (From Environment):**

```python
CORS_ORIGINS: List[str] = []  # Will be parsed from env
```

**Environment Variable Format:**

```bash
# .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://ai4mind.com
```

### **Phase 3: Remove Fallback Values**

**Current:**

```python
VOICE_SERVICE_URL = settings.VOICE_SERVICE_URL or "http://localhost:8001"
```

**Target:**

```python
VOICE_SERVICE_URL = settings.VOICE_SERVICE_URL
```

Add validation to ensure required variables are set.

### **Phase 4: Add Service URLs**

New environment variables needed:

```bash
# Service URLs (Internal - Docker network)
AI_SERVICE_URL=http://ai-service:8000
VOICE_SERVICE_URL=http://voice-service:8001

# Service URLs (External - Public)
AI_SERVICE_PUBLIC_URL=https://api.ai4mind.com
VOICE_SERVICE_PUBLIC_URL=https://voice.ai4mind.com

# Frontend URL
FRONTEND_URL=https://ai4mind.com
CORS_ORIGINS=http://localhost:3000,https://ai4mind.com
```

---

## 📝 Implementation Checklist

### **1. Update ai-service/app/core/config.py**

```python
class Settings(BaseSettings):
    # ... existing fields ...

    # Microservices URLs
    VOICE_SERVICE_URL: str  # REQUIRED - no default

    # Frontend & CORS
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"  # Comma-separated

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
```

### **2. Update voice-service/app/core/config.py**

```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str  # REQUIRED

    # AI Service
    AI_SERVICE_URL: str  # REQUIRED - no default

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
```

### **3. Update ai-service/app/main.py**

**Current:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    ...
)
```

**New:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Use property
    ...
)
```

### **4. Update ai-service/app/api/v1/endpoints/combined_assessment.py**

**Current:**

```python
VOICE_SERVICE_URL = settings.VOICE_SERVICE_URL or "http://localhost:8001"
```

**New:**

```python
# Validate at module load time
if not settings.VOICE_SERVICE_URL:
    raise ValueError("VOICE_SERVICE_URL environment variable is required")

VOICE_SERVICE_URL = settings.VOICE_SERVICE_URL
```

### **5. Update .env.example**

```bash
# ============================================
# SERVICE URLS (REQUIRED for Production)
# ============================================

# AI Service URL (for voice-service to call back)
# Development: http://localhost:8000
# Docker: http://ai-service:8000
# Production: https://api.ai4mind.com
AI_SERVICE_URL=http://localhost:8000

# Voice Service URL (for ai-service to call)
# Development: http://localhost:8001
# Docker: http://voice-service:8001
# Production: https://voice.ai4mind.com
VOICE_SERVICE_URL=http://localhost:8001

# Frontend URL
# Development: http://localhost:3000
# Production: https://ai4mind.com
FRONTEND_URL=http://localhost:3000

# CORS Allowed Origins (comma-separated, no spaces)
# Development: http://localhost:3000,http://localhost:3001
# Production: https://ai4mind.com,https://www.ai4mind.com
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# ============================================
# DATABASE (REQUIRED)
# ============================================

# Supabase Database URL
SUPABASE_DATABASE_URL=postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres

# ============================================
# SUPABASE (REQUIRED)
# ============================================

SUPABASE_PROJECT_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# ============================================
# GEMINI AI (REQUIRED)
# ============================================

GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-1.5-flash

# ============================================
# JWT (REQUIRED for Production)
# ============================================

JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# REDIS (Optional - for rate limiting)
# ============================================

REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# ============================================
# SERVER CONFIG (Optional)
# ============================================

# Environment: development, staging, production
ENVIRONMENT=development
DEBUG=true

# Server ports (usually set by Docker/Cloud)
# AI_SERVICE_PORT=8000
# VOICE_SERVICE_PORT=8001

# File storage
UPLOAD_DIR=../shared/audio-files
MAX_FILE_SIZE=52428800
```

### **6. Create docker-compose.yml (for reference)**

```yaml
version: "3.8"

services:
  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    container_name: ai4mind-ai-service
    ports:
      - "8000:8000"
    environment:
      # Service URLs (Internal Docker network)
      - VOICE_SERVICE_URL=http://voice-service:8001
      - AI_SERVICE_URL=http://ai-service:8000

      # Frontend & CORS
      - FRONTEND_URL=${FRONTEND_URL:-http://localhost:3000}
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000}

      # Database
      - SUPABASE_DATABASE_URL=${SUPABASE_DATABASE_URL}

      # Supabase
      - SUPABASE_PROJECT_URL=${SUPABASE_PROJECT_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}

      # Gemini
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=${GEMINI_MODEL:-gemini-1.5-flash}

      # JWT
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}

      # Environment
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - voice-service
    networks:
      - ai4mind-network
    restart: unless-stopped

  voice-service:
    build:
      context: ./voice-service
      dockerfile: Dockerfile
    container_name: ai4mind-voice-service
    ports:
      - "8001:8001"
    environment:
      # Service URLs (Internal Docker network)
      - AI_SERVICE_URL=http://ai-service:8000

      # Database
      - DATABASE_URL=${SUPABASE_DATABASE_URL}

      # Whisper
      - WHISPER_MODEL=base

      # Environment
      - ENVIRONMENT=production
    volumes:
      - voice-storage:/app/storage
    networks:
      - ai4mind-network
    restart: unless-stopped

networks:
  ai4mind-network:
    driver: bridge

volumes:
  voice-storage:
```

---

## 🚀 Deployment Scenarios

### **Scenario 1: Local Development**

```bash
# .env
VOICE_SERVICE_URL=http://localhost:8001
AI_SERVICE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### **Scenario 2: Docker Compose**

```bash
# .env
VOICE_SERVICE_URL=http://voice-service:8001
AI_SERVICE_URL=http://ai-service:8000
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

### **Scenario 3: Kubernetes**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai4mind-config
data:
  VOICE_SERVICE_URL: "http://voice-service.default.svc.cluster.local:8001"
  AI_SERVICE_URL: "http://ai-service.default.svc.cluster.local:8000"
  FRONTEND_URL: "https://ai4mind.com"
  CORS_ORIGINS: "https://ai4mind.com,https://www.ai4mind.com"
```

### **Scenario 4: Cloud (Azure/AWS/GCP)**

```bash
# .env (in cloud secrets manager)
VOICE_SERVICE_URL=https://voice-api-internal.azurewebsites.net
AI_SERVICE_URL=https://ai-api-internal.azurewebsites.net
FRONTEND_URL=https://ai4mind.com
CORS_ORIGINS=https://ai4mind.com,https://www.ai4mind.com
```

---

## ✅ Validation Checklist

After migration, verify:

- [ ] No hardcoded `localhost` in Python code
- [ ] No hardcoded `127.0.0.1` in Python code
- [ ] No hardcoded ports in Python code
- [ ] All service URLs read from environment
- [ ] CORS origins read from environment
- [ ] `.env.example` has all required variables
- [ ] Docker compose uses environment variables
- [ ] Services can communicate in Docker network
- [ ] Health checks pass in all deployment scenarios
- [ ] Test with different environments (dev/staging/prod)

---

## 🔧 Testing Commands

### **Test Local:**

```bash
export VOICE_SERVICE_URL=http://localhost:8001
export AI_SERVICE_URL=http://localhost:8000
python -m uvicorn app.main:app --reload
```

### **Test Docker:**

```bash
docker-compose up --build
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### **Test Service Communication:**

```bash
# From ai-service, call voice-service
curl -X POST http://localhost:8000/api/v1/assessments/submit-with-voice \
  -H "Authorization: Bearer $TOKEN" \
  -F "answers=[1,2,3,4,5,6,7]" \
  -F "audio_file=@test.wav" \
  -F "gender=male"
```

---

## 📦 Migration Steps

1. ✅ **Audit code** - Find all hardcoded URLs (Done above)
2. 🔄 **Update config.py files** - Add parsing for CORS_ORIGINS
3. 🔄 **Update main.py** - Use cors_origins_list property
4. 🔄 **Remove fallbacks** - Remove `or "localhost"` patterns
5. 🔄 **Update .env.example** - Document all variables
6. 🔄 **Create docker-compose.yml** - For container deployment
7. ✅ **Test locally** - Verify services work
8. ✅ **Test Docker** - Verify container communication
9. ✅ **Test Cloud** - Deploy to staging environment
10. ✅ **Update docs** - Update README with new env vars

---

## 🎯 Priority

**HIGH**: Must complete before cloud deployment

- Remove localhost fallbacks
- Add CORS environment parsing
- Create docker-compose.yml
- Update .env.example

**MEDIUM**: Improve deployment experience

- Add validation for required variables
- Create Kubernetes manifests
- Add health check endpoints

**LOW**: Nice to have

- Add environment variable documentation
- Create deployment scripts
- Add monitoring configuration

---

**Status**: Ready to implement  
**Estimated Time**: 2-3 hours  
**Breaking Changes**: Yes - `.env` file must be updated
