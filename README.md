# 🧠 AI4Mind - AI-Powered Mental Health Support Platform

<div align="center">

![AI4Mind Banner](https://img.shields.io/badge/AI4Mind-Mental%20Health%20Platform-blue?style=for-the-badge&logo=brain&logoColor=white)

**🎯 Early detection of stress and anxiety through AI-powered emotion analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg?style=flat-square&logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6.svg?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

[🚀 Live Demo](#) · [📖 Documentation](#-tài-liệu-hướng-dẫn) · [🐛 Report Bug](#) · [✨ Request Feature](#)

</div>

---

## 🌟 Về Dự Án

**AI4Mind** là nền tảng **open-source** hỗ trợ sức khỏe tâm thần cho học sinh/sinh viên, sử dụng **AI và Machine Learning** để phát hiện sớm các vấn đề tâm lý thông qua:

- 🎤 **Phân tích giọng nói đa chiều** - Nhận diện cảm xúc qua âm điệu, tốc độ nói, năng lượng giọng nói
- 💬 **Tư vấn AI thông minh** - Chatbot hỗ trợ 24/7 với Google Gemini 2.0 Flash
- 📊 **Đánh giá tâm lý chuẩn y khoa** - Bài test GAD-7 (General Anxiety Disorder)
- 🔒 **Bảo mật tuyệt đối** - RBAC, consent management, và mã hóa dữ liệu nhạy cảm
- 📈 **Theo dõi tiến trình trực quan** - Dashboard với charts và insights thông minh

### 🎯 Giải Quyết Vấn Đề Gì?

Theo WHO, **1/7 thanh thiên niên (14-29 tuổi)** gặp vấn đề về sức khỏe tâm thần, nhưng hầu hết không được phát hiện sớm. AI4Mind giúp:

✅ **Học sinh** tự nhận biết tình trạng tâm lý và được hỗ trợ kịp thời  
✅ **Phụ huynh** theo dõi sức khỏe tinh thần của con (với sự đồng ý)  
✅ **Tư vấn viên** làm việc hiệu quả hơn với công cụ AI hỗ trợ  
✅ **Nhà nghiên cứu** có dữ liệu để cải thiện chăm sóc sức khỏe tâm thần

---

## 📋 Mục Lục

- [🌟 Về Dự Án](#-về-dự-án)
- [✨ Tính Năng Nổi Bật](#-tính-năng-nổi-bật)
- [🏗️ Kiến Trúc Hệ Thống](#️-kiến-trúc-hệ-thống)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Bắt Đầu Nhanh](#-bắt-đầu-nhanh)
- [📦 Cài Đặt Chi Tiết](#-cài-đặt-chi-tiết)
- [🎭 Phân Quyền & Use Cases](#-phân-quyền--use-cases)
- [📸 Screenshots](#-screenshots)
- [� Testing](#-testing)
- [📊 Project Structure](#-project-structure)
- [🚀 Deployment](#-deployment)
- [�🤝 Đóng Góp](#-đóng-góp)
- [📈 Roadmap](#-roadmap)
- [📄 License](#-license)
- [📞 Liên Hệ](#-liên-hệ)

---

## ✨ Tính Năng Nổi Bật

### 🎤 Voice Emotion Analysis (Phân Tích Cảm Xúc Qua Giọng Nói)

<details>
<summary><b>🔍 Xem chi tiết công nghệ</b></summary>

**Hybrid Architecture** - Kết hợp tốt nhất của cả hai thế giới:

```
📥 Audio Input (MP3/WAV/OGG)
    ↓
🎙️ Deepgram API → Transcription (Vietnamese/English)
    ↓
🔊 Librosa → Feature Extraction
    │ ├─ Pitch (cao độ giọng nói)
    │ ├─ Energy (năng lượng âm thanh)
    │ ├─ Speaking Rate (tốc độ nói)
    │ └─ Pause patterns (mẫu im lặng)
    ↓
🧠 Custom ML Model → Emotion Classification
    │ ├─ 😊 Happy
    │ ├─ 😢 Sad
    │ ├─ 😰 Anxious
    │ ├─ 😠 Angry
    │ └─ 😐 Neutral
    ↓
📊 Results + Transcription
```

**Tại sao không dùng Whisper?**

- ✅ Deepgram API: Nhanh hơn 5-10x, hỗ trợ tiếng Việt tốt hơn
- ✅ Memory-efficient: <512MB (vs 2GB+ với Whisper)
- ✅ Cost-effective: Free tier 45h/month
- ✅ Our value-add: Custom emotion model trained on Vietnamese data

</details>

### 💬 AI Counselor Chatbot

- 🤖 **Powered by Google Gemini 2.0 Flash** - Mô hình AI tiên tiến nhất
- 🧠 **Context-Aware** - Hiểu lịch sử chat và tình trạng tâm lý của user
- 🎯 **Evidence-Based** - Câu trả lời dựa trên CBT (Cognitive Behavioral Therapy)
- 🔒 **Private & Secure** - Dữ liệu chat được mã hóa end-to-end
- 🌍 **Multilingual** - Hỗ trợ tiếng Việt và tiếng Anh

### 📊 Mental Health Assessments

| Assessment | Mục đích              | Thời gian |
| ---------- | --------------------- | --------- |
| **GAD-7**  | Đánh giá mức độ lo âu | ~2 phút   |
| **PHQ-9**  | Đánh giá trầm cảm     | ~3 phút   |
| **PSS-10** | Đo lường stress       | ~3 phút   |

Tất cả bài test đều có **độ tin cậy cao** và được sử dụng trong y học lâm sàng.

### 👥 Role-Based Access Control (RBAC)

```
🎓 Student
  ├─ Take assessments & voice analysis
  ├─ Chat with AI counselor
  ├─ View personal progress
  └─ Grant/revoke access to Parents & Counselors

👨‍👩‍👧 Parent
  ├─ View child's progress (with consent)
  ├─ Receive alerts for concerning patterns
  └─ NO access to sensitive details (chat logs, recordings)

👨‍⚕️ Counselor
  ├─ Manage assigned students
  ├─ View detailed reports (with consent)
  ├─ Add counseling notes
  └─ Track student progress over time

👨‍💼 Admin
  ├─ User management (CRUD)
  ├─ Export reports (Excel/CSV)
  ├─ View system analytics
  └─ Audit logs

👨‍🔬 Researcher
  ├─ Access anonymized data
  ├─ Statistical analysis tools
  └─ Export datasets for research
```

---

## 📚 Tài liệu hướng dẫn

> **🎯 MỚI BẮT ĐẦU?** Đọc [GETTING_STARTED.md](./GETTING_STARTED.md) trước!

| Tài liệu                   | Mục đích                    | Link                                       |
| -------------------------- | --------------------------- | ------------------------------------------ |
| **Getting Started**        | Điểm bắt đầu, roadmap       | [📖 Đọc](./GETTING_STARTED.md)             |
| **Setup Guide**            | Hướng dẫn setup từng bước   | [🚀 Bắt đầu](./SETUP_GUIDE.md)             |
| **Architecture**           | Kiến trúc hệ thống chi tiết | [🏗️ Xem](./ARCHITECTURE.md)                |
| **Conda Environments**     | Quản lý Python environments | [🐍 Hướng dẫn](./CONDA_ENVIRONMENTS.md)    |
| **Services Communication** | Cách services tương tác     | [🔗 Chi tiết](./SERVICES_COMMUNICATION.md) |
| **Changelog**              | Lịch sử thay đổi            | [📝 Xem](./CHANGELOG.md)                   |

---

## �️ Kiến Trúc Hệ Thống

<div align="center">

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React + TypeScript<br/>Vite + Material-UI]
    end

    subgraph "API Gateway"
        AG[AI Service<br/>FastAPI + Python 3.11]
    end

    subgraph "Microservices"
        VS[Voice Service<br/>Librosa + Deepgram API]
    end

    subgraph "AI/ML Layer"
        GEMINI[Google Gemini 2.0 Flash<br/>Conversational AI]
        ML[Custom ML Model<br/>Emotion Classification]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Supabase)]
        STORAGE[File Storage<br/>Supabase Storage]
        CACHE[Redis Cache<br/>Session Management]
    end

    subgraph "External Services"
        DG[Deepgram API<br/>Speech-to-Text]
    end

    FE -->|REST API| AG
    AG -->|HTTP| VS
    AG -->|API Call| GEMINI
    VS -->|API Call| DG
    VS -->|Feature Extraction| ML
    AG -->|ORM/SQLAlchemy| DB
    AG -->|Upload/Download| STORAGE
    AG -->|Cache| CACHE

    style FE fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    style AG fill:#009688,stroke:#333,stroke-width:2px
    style VS fill:#FF6B6B,stroke:#333,stroke-width:2px
    style GEMINI fill:#4285F4,stroke:#333,stroke-width:2px
    style DB fill:#336791,stroke:#333,stroke-width:2px
    style STORAGE fill:#3ECF8E,stroke:#333,stroke-width:2px
```

</div>

### 📡 Services Communication

| Service           | Port | Tech Stack                     | Responsibility                      |
| ----------------- | ---- | ------------------------------ | ----------------------------------- |
| **Frontend**      | 3000 | React 18 + TypeScript + Vite   | UI/UX, State Management             |
| **AI Service**    | 8000 | FastAPI + SQLAlchemy + Alembic | API Gateway, Auth, Business Logic   |
| **Voice Service** | 8001 | FastAPI + Librosa + Deepgram   | Audio Processing, Emotion Detection |
| **Database**      | 5432 | PostgreSQL 14 (Supabase)       | Data Persistence, RLS               |
| **Cache**         | 6379 | Redis                          | Session, Rate Limiting              |

### 🔐 Security Features

- 🔑 **JWT Authentication** - Access & Refresh tokens
- 🛡️ **Row-Level Security (RLS)** - PostgreSQL policies
- 🔐 **Bcrypt Password Hashing** - Salt rounds: 12
- 🚫 **Rate Limiting** - Redis-based throttling
- ✅ **Input Validation** - Pydantic schemas
- 🔒 **HTTPS Only** - TLS 1.3
- 🕵️ **Audit Logging** - Track all sensitive operations

---

## 🛠️ Tech Stack

<div align="center">

### Frontend

![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Material-UI](https://img.shields.io/badge/MUI-5.14-007FFF?style=for-the-badge&logo=mui&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-6.20-CA4245?style=for-the-badge&logo=react-router&logoColor=white)
![TanStack Query](https://img.shields.io/badge/TanStack_Query-5.12-FF4154?style=for-the-badge&logo=react-query&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.5-FF6384?style=for-the-badge&logo=chart.js&logoColor=white)

### Backend

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.13-6BA81E?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-2.5-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

### AI/ML

![Google Gemini](https://img.shields.io/badge/Gemini_2.0-Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Librosa](https://img.shields.io/badge/Librosa-0.10-FF1493?style=for-the-badge)
![Deepgram](https://img.shields.io/badge/Deepgram-API-000000?style=for-the-badge)
![NumPy](https://img.shields.io/badge/NumPy-1.24-013243?style=for-the-badge&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-1.11-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)

### Database & Storage

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-2.0-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-5.0-DC382D?style=for-the-badge&logo=redis&logoColor=white)

### DevOps & Tools

![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deploy-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deploy-000000?style=for-the-badge&logo=vercel&logoColor=white)

</div>

---

## � Bắt Đầu Nhanh

### � Prerequisites

```bash
# Required
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 5.0+ (optional, for caching)

# Recommended
- Conda (for environment management)
- Docker & Docker Compose (for containerized setup)
```

### ⚡ Quick Start (Docker)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai4mind-app.git
cd ai4mind-app

# 2. Copy environment file
cp .env.example .env
# Edit .env with your credentials (API keys, database URL, etc.)

# 3. Run with Docker Compose
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# AI Service API: http://localhost:8000/docs
# Voice Service API: http://localhost:8001/docs
```

---

## 📦 Cài Đặt Chi Tiết

### 🐍 Setup với Conda (Recommended)

<details>
<summary><b>📖 Xem hướng dẫn chi tiết</b></summary>

#### AI Service

```powershell
# Tạo environment
conda create -n ai4mind-ai-service python=3.11 -y
conda activate ai4mind-ai-service

# Cài đặt dependencies
cd ai-service
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Chạy development server
uvicorn app.main:app --reload --port 8000
```

#### Voice Service

```powershell
# Tạo environment
conda create -n ai4mind-voice-service python=3.11 -y
conda activate ai4mind-voice-service

# Cài đặt dependencies
cd voice-service
pip install -r requirements.txt

# Chạy service
uvicorn app.main:app --reload --port 8001
```

#### Frontend

```powershell
# Cài đặt dependencies
cd frontend
npm install

# Chạy development server
npm run dev
```

</details>

### 🐳 Setup với Docker

<details>
<summary><b>📖 Xem hướng dẫn chi tiết</b></summary>

#### Build images

```bash
# Build all services
docker-compose build

# Hoặc build từng service
docker-compose build ai-service
docker-compose build voice-service
docker-compose build frontend
```

#### Run services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Database migrations

```bash
# Run migrations
docker-compose exec ai-service alembic upgrade head

# Create new migration
docker-compose exec ai-service alembic revision --autogenerate -m "Description"
```

</details>

### 🗄️ Database Setup

<details>
<summary><b>📖 Supabase Setup</b></summary>

1. Tạo project trên [Supabase](https://supabase.com)
2. Copy **Project URL** và **anon/service_role keys**
3. Chạy SQL scripts trong thư mục `database/`:

   ```sql
   -- 1. Create base tables (auto from Alembic)
   -- 2. Setup RLS policies
   \i database/rls_policies.sql

   -- 3. Create counselor tables
   \i database/create_counselor_chat_tables.sql

   -- 4. Add medical centers
   \i database/create_medical_centers_table.sql
   ```

4. Enable Row Level Security cho tất cả tables

</details>

### 🔑 Environment Variables

<details>
<summary><b>📖 Required Environment Variables</b></summary>

#### AI Service (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai4mind
SUPABASE_PROJECT_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Services
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Microservices
VOICE_SERVICE_URL=http://localhost:8001

# CORS
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,https://ai4mind.vercel.app

# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

#### Voice Service (.env)

```bash
# Database (same as AI Service)
DATABASE_URL=postgresql://user:password@localhost:5432/ai4mind

# Deepgram API
DEEPGRAM_API_KEY=your-deepgram-api-key

# AI Service URL (for callbacks)
AI_SERVICE_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
DEBUG=True
```

#### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_VOICE_SERVICE_URL=http://localhost:8001
```

</details>

---

## 🎭 Phân Quyền & Use Cases

### 🎓 Student Journey

```mermaid
graph LR
    A[Đăng ký] -->|Email verification| B[Login]
    B --> C[Làm bài test GAD-7]
    C --> D[Upload voice recording]
    D --> E[Xem kết quả phân tích]
    E --> F[Chat với AI Counselor]
    F --> G[Grant access cho Parent/Counselor]
    G --> H[Theo dõi tiến trình]
    H --> I[Làm lại test định kỳ]
```

### 👨‍👩‍👧 Parent Journey

```mermaid
graph LR
    A[Login] --> B[Request access from Student]
    B -->|Được chấp thuận| C[View Student Dashboard]
    C --> D[Xem lịch sử GAD-7 scores]
    D --> E[Nhận alerts nếu có]
    E --> F[Liên hệ Counselor]
```

### 👨‍⚕️ Counselor Journey

```mermaid
graph LR
    A[Login] --> B[View assigned students]
    B --> C[Request detailed access]
    C -->|Được chấp thuận| D[View full reports]
    D --> E[Analyze voice recordings]
    E --> F[Add counseling notes]
    F --> G[Track progress over time]
```

---

## 📸 Screenshots

<div align="center">

### 🏠 Dashboard

<img src="docs/images/dashboard.png" alt="Student Dashboard" width="800"/>

_Real-time mental health tracking với beautiful charts_

### 💬 AI Counselor Chat

<img src="docs/images/chat.png" alt="AI Chat Interface" width="800"/>

_Context-aware AI chatbot powered by Gemini 2.0_

### 📊 Assessment Results

<img src="docs/images/assessment.png" alt="GAD-7 Assessment" width="800"/>

_Detailed GAD-7 results với recommendations_

### 🎤 Voice Analysis

<img src="docs/images/voice-analysis.png" alt="Voice Emotion Analysis" width="800"/>

_Real-time emotion detection from voice recordings_

</div>

---

## 🧪 Testing

### Backend Tests

```bash
# AI Service tests
cd ai-service
pytest tests/ -v --cov=app --cov-report=html

# Voice Service tests
cd voice-service
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Tests

```bash
# Run all integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Manual API Testing

Use the provided Postman collection:

```bash
# Import collection
postman/AI4Mind.postman_collection.json

# Import environment
postman/AI4Mind.postman_environment.json
```

---

## 📊 Project Structure

```
ai4mind-app/
├── 📁 ai-service/              # API Gateway (FastAPI)
│   ├── app/
│   │   ├── api/v1/endpoints/  # REST API endpoints
│   │   ├── core/              # Config, security, dependencies
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic layer
│   │   └── utils/             # Helper functions
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit & integration tests
│   └── requirements.txt
│
├── 📁 voice-service/          # Voice Analysis Service
│   ├── app/
│   │   ├── api/               # Voice analysis endpoints
│   │   ├── core/              # Config & dependencies
│   │   ├── models/            # ML models & processors
│   │   └── utils/             # Audio processing utilities
│   └── requirements.txt
│
├── 📁 frontend/               # React + TypeScript UI
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React Context providers
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API service layer
│   │   └── types/             # TypeScript type definitions
│   └── package.json
│
├── 📁 database/               # SQL scripts & migrations
│   ├── rls_policies.sql       # Row Level Security
│   ├── create_counselor_chat_tables.sql
│   └── create_medical_centers_table.sql
│
├── 📁 scripts/                # Utility scripts
│   ├── init-db.py             # Database initialization
│   ├── seed-data.py           # Seed test data
│   └── generate_secrets.py   # Generate JWT secrets
│
├── 📁 docs/                   # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   ├── API.md                 # API documentation
│   └── DEPLOYMENT.md          # Deployment guide
│
├── docker-compose.yml         # Docker orchestration
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🚀 Deployment

### 🌐 Render.com (Recommended)

<details>
<summary><b>📖 Xem hướng dẫn deploy</b></summary>

1. **Fork repository** về GitHub của bạn

2. **Connect Render** với GitHub repo

3. **Deploy services** theo thứ tự:

   ```
   1. PostgreSQL Database (Supabase hoặc Render PostgreSQL)
   2. Redis (Render Redis hoặc external)
   3. Voice Service (Web Service)
   4. AI Service (Web Service)
   ```

4. **Configure environment variables** theo `render.yaml`

5. **Run migrations**:

   ```bash
   # Từ Render Shell
   alembic upgrade head
   ```

6. **Verify health checks**:
   - AI Service: `https://your-app.onrender.com/health`
   - Voice Service: `https://voice-service.onrender.com/health`

</details>

### ☁️ Vercel (Frontend)

<details>
<summary><b>📖 Xem hướng dẫn deploy</b></summary>

1. Import project từ GitHub

2. Configure build settings:

   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

3. Add environment variables:

   ```
   VITE_API_URL=https://your-api.onrender.com/api/v1
   VITE_VOICE_SERVICE_URL=https://voice-service.onrender.com
   ```

4. Deploy!

</details>

### 🐳 Docker Production

<details>
<summary><b>📖 Xem hướng dẫn deploy</b></summary>

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run with production config
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL with Let's Encrypt
docker-compose -f docker-compose.prod.yml exec nginx certbot --nginx
```

</details>

---

## 🤝 Đóng Góp

Chúng tôi luôn chào đón mọi đóng góp! 🎉

### 🐛 Báo lỗi

- Tạo [Issue](https://github.com/thhieu2904/ai4mind-app/issues) với label `bug`
- Mô tả chi tiết: môi trường, steps to reproduce, expected vs actual behavior

### ✨ Đề xuất tính năng

- Tạo [Issue](https://github.com/thhieu2904/ai4mind-app/issues) với label `enhancement`
- Giải thích use case và lợi ích của tính năng

### 🔧 Pull Request Process

1. **Fork** repo và tạo branch mới từ `main`

   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Commit** với clear messages

   ```bash
   git commit -m "feat: Add amazing feature"
   ```

3. **Push** lên branch

   ```bash
   git push origin feature/amazing-feature
   ```

4. Tạo **Pull Request** với mô tả chi tiết

### 📝 Coding Standards

- **Backend**: Follow [PEP 8](https://peps.python.org/pep-0008/), use `black` formatter
- **Frontend**: Follow [Airbnb Style Guide](https://github.com/airbnb/javascript), use `prettier`
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)
- **Documentation**: Update docs for all new features

---

## 📈 Roadmap

### ✅ Phase 1: MVP (Completed)

- [x] User authentication & RBAC
- [x] GAD-7 assessment
- [x] Voice emotion analysis
- [x] AI chatbot with Gemini
- [x] Basic dashboard

### 🚧 Phase 2: Enhancement (In Progress)

- [ ] PHQ-9 assessment (depression)
- [ ] PSS-10 assessment (stress)
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] Export reports (PDF/Excel)

### 🔮 Phase 3: Advanced Features (Planned)

- [ ] Mobile app (React Native)
- [ ] Real-time video counseling
- [ ] Group therapy sessions
- [ ] Gamification & rewards
- [ ] Multi-language support (English, Vietnamese, etc.)

### 🎯 Phase 4: AI Enhancement (Future)

- [ ] Custom emotion detection model
- [ ] Predictive analytics (risk assessment)
- [ ] Personalized intervention recommendations
- [ ] Integration with wearables (heart rate, sleep data)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 AI4Mind Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- **Google Gemini** - AI chatbot capabilities
- **Deepgram** - Speech-to-text transcription
- **Supabase** - Database & storage infrastructure
- **Material-UI** - Beautiful React components
- **FastAPI** - High-performance Python web framework
- **Open Source Community** - For all the amazing libraries we use

---

## 📞 Liên Hệ

<div align="center">

**AI4Mind Team**

[![GitHub](https://img.shields.io/badge/GitHub-thhieu2904-181717?style=for-the-badge&logo=github)](https://github.com/thhieu2904)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:your.email@example.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/yourprofile)

**⭐ Nếu dự án này hữu ích, đừng quên star repo nhé! ⭐**

[🔝 Back to top](#-ai4mind---ai-powered-mental-health-support-platform)

</div>

---

<div align="center">

**Made with ❤️ for better mental health**

_"Technology should serve humanity, especially those who need it most."_

</div>
