# 🧠 AI4Mind - Mental Health Support Platform

> **Nền tảng mã nguồn mở nhằm phát hiện sớm các dấu hiệu của stress và lo âu thông qua phân tích cảm xúc trong văn bản và giọng nói.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng chính](#-tính-năng-chính)
- [Kiến trúc hệ thống](#️-kiến-trúc-hệ-thống)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Phân quyền người dùng](#-phân-quyền-người-dùng)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Contributing](#-contributing)

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

## 🎯 Giới thiệu

**AI4Mind** là nền tảng hỗ trợ sức khỏe tâm thần dành cho học sinh/sinh viên, sử dụng AI để:

- 🔍 **Phát hiện sớm** dấu hiệu stress, lo âu qua test GAD-7
- 🎤 **Phân tích giọng nói** để nhận diện cảm xúc và mức độ căng thẳng
- 💬 **Tư vấn AI** với Gemini API cung cấp gợi ý hỗ trợ
- 📊 **Theo dõi tiến trình** với biểu đồ trực quan
- 🔒 **Bảo mật & riêng tư** với RBAC và consent management

### Mục tiêu dự án

1. Giúp học sinh **tự nhận biết** tình trạng tâm lý của mình
2. Hỗ trợ **phụ huynh** theo dõi sức khỏe tinh thần của con
3. Cung cấp công cụ cho **tư vấn viên** làm việc hiệu quả
4. Tạo **dữ liệu nghiên cứu** về sức khỏe tâm thần học sinh

---

## ✨ Tính năng chính

### 👨‍🎓 Dành cho Học sinh

- ✅ Test đánh giá GAD-7 (General Anxiety Disorder)
- 🎙️ Upload voice recording để phân tích cảm xúc
- 📈 Xem biểu đồ tiến trình cá nhân
- 🤖 Nhận tư vấn từ AI (Gemini)
- 🔐 Quản lý quyền truy cập (cho phép Parent/Counselor xem data)

### 👨‍👩‍👧 Dành cho Phụ huynh

- 👀 Xem tiến trình học tập và tinh thần của con (với sự đồng ý)
- 📊 Theo dõi lịch sử test GAD-7
- 🔔 Nhận thông báo khi có dấu hiệu bất thường
- ❌ **Không** truy cập được chi tiết nhạy cảm

### 👨‍⚕️ Dành cho Tư vấn viên

- 📋 Quản lý danh sách học sinh được phân công
- 📊 Xem báo cáo chi tiết (với consent)
- 📝 Ghi chú buổi tư vấn
- 📈 Theo dõi tiến triển học sinh

### 👨‍💼 Dành cho Admin

- 👥 Quản lý users (CRUD)
- 📊 Xuất báo cáo Excel tổng hợp
- 🔍 Xem audit logs
- ⚙️ Cấu hình hệ thống

### 👨‍🔬 Dành cho Researcher

- 📊 Truy cập dữ liệu đã ẩn danh
- 📈 Thống kê và phân tích
- 📥 Export dataset cho nghiên cứu

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐
│   FRONTEND  │  React + TypeScript + Vite
│   :3000     │
└──────┬──────┘
       │ REST API
       ▼
┌─────────────────────────────────┐
│   AI-SERVICE (API Gateway)      │  FastAPI
│   :8000                          │
│  • Authentication & RBAC         │
│  • Business Logic                │
│  • Request Routing               │
│  • Gemini AI Integration         │
└───┬──────────┬──────────┬────────┘
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌───────────┐ ┌─────────┐
│Database│ │   VOICE   │ │ Gemini  │
│Supabase│ │  ANALYSIS │ │   API   │
│        │ │   :8001   │ │         │
└────────┘ └───────────┘ └─────────┘
```

**Pattern:** API Gateway - AI-Service là trung tâm điều phối toàn bộ requests

📖 **Chi tiết:** Xem [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 🛠 Tech Stack

### Backend

- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0 + Alembic
- **Database:** PostgreSQL 15 (Supabase)
- **Cache:** Redis 7
- **Auth:** JWT (python-jose)
- **AI:** Google Gemini API
- **Export:** openpyxl, pandas

### Frontend

- **Framework:** React 18 + TypeScript
- **Build:** Vite
- **UI:** Material-UI / Ant Design
- **State:** React Context + React Query
- **HTTP:** Axios
- **Charts:** Recharts

### Voice Analysis

- **Speech-to-Text:** OpenAI Whisper
- **Audio:** librosa, pydub
- **ML:** PyTorch, transformers

### DevOps

- **Container:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana (optional)

---

## 🚀 Quick Start

### Yêu cầu hệ thống

- **Docker** & **Docker Compose**
- **Python** 3.11+
- **Node.js** 18+
- **Make** (optional, cho convenience commands)

### 1️⃣ Clone repository

```bash
git clone https://github.com/thhieu2904/ai4mind-app.git
cd ai4mind-app
```

### 2️⃣ Setup môi trường

```bash
# Copy .env template
cp .env.example .env

# Edit .env và điền thông tin:
# - SUPABASE_DATABASE_URL
# - GEMINI_API_KEY
# - JWT_SECRET_KEY
```

### 3️⃣ Khởi động dự án

#### Option A: Sử dụng Make (Khuyến nghị)

```bash
# Setup và tạo thư mục cần thiết
make setup

# Khởi động tất cả services
make dev

# Chạy migrations
make migrate

# Seed dữ liệu test (optional)
make seed
```

#### Option B: Sử dụng Docker Compose

```bash
# Khởi động services
docker-compose up -d

# Chạy migrations
docker-compose exec ai-service alembic upgrade head
```

### 4️⃣ Truy cập ứng dụng

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Voice Analysis Docs:** http://localhost:8001/docs

### 5️⃣ Tài khoản test (sau khi seed)

| Role      | Email                    | Password     |
| --------- | ------------------------ | ------------ |
| Admin     | admin@ai4mind.edu.vn     | admin123     |
| Student   | student@ai4mind.edu.vn   | student123   |
| Counselor | counselor@ai4mind.edu.vn | counselor123 |

---

## 👥 Phân quyền người dùng

| Role           | Quyền truy cập                                                       |
| -------------- | -------------------------------------------------------------------- |
| **Student**    | Xem & chỉnh sửa profile, làm test, upload voice, cấp/thu hồi consent |
| **Parent**     | Xem profile con, xem lịch sử test (với consent), nhận thông báo      |
| **Counselor**  | Xem dữ liệu học sinh (với consent), tạo sessions, ghi notes          |
| **Admin**      | Quản lý users, export báo cáo Excel, xem audit logs                  |
| **Researcher** | Xem dữ liệu ẩn danh, export dataset nghiên cứu                       |

📖 **Chi tiết:** Xem [ARCHITECTURE.md - RBAC Section](./ARCHITECTURE.md#-hệ-thống-phân-quyền-rbac---updated)

---

## 📚 API Documentation

### Swagger UI (Interactive)

- **Backend:** http://localhost:8000/docs
- **Voice Service:** http://localhost:8001/docs

### Main Endpoints

#### Authentication

```
POST   /api/v1/auth/register     - Đăng ký
POST   /api/v1/auth/login        - Đăng nhập
POST   /api/v1/auth/refresh      - Refresh token
POST   /api/v1/auth/logout       - Đăng xuất
```

#### Students

```
GET    /api/v1/students/me                    - Profile của tôi
GET    /api/v1/students/me/assessments        - Lịch sử test
POST   /api/v1/students/me/assessments        - Làm bài test mới
POST   /api/v1/students/me/voice-analysis     - Upload voice
POST   /api/v1/students/consent               - Cấp/thu hồi quyền
```

#### Parents

```
GET    /api/v1/parents/children               - Danh sách con
GET    /api/v1/parents/children/:id/progress  - Tiến trình con
```

#### Admin

```
GET    /api/v1/admin/users                    - Danh sách users
POST   /api/v1/admin/users                    - Tạo user
GET    /api/v1/reports/export/admin           - Export Excel
```

---

## 💻 Development

### Cấu trúc thư mục

```
ai4mind-app/
├── ai-service/         # API Gateway (FastAPI)
├── voice-analysis/     # Voice processing service
├── frontend/           # React frontend
├── shared/             # Shared storage (audio, exports)
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── docker-compose.yml  # Docker orchestration
```

### Makefile Commands

```bash
make help              # Xem tất cả commands
make setup             # Setup project
make dev               # Start development
make test              # Run all tests
make logs              # Show logs
make migrate           # Run DB migrations
make clean             # Clean up
```

### Testing

```bash
# All tests
make test

# Backend only
make test-backend

# Frontend only
make test-frontend

# With coverage
make test-coverage
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type checking
make type-check
```

---

## 🔐 Security

### Best Practices

- ✅ JWT Authentication với refresh tokens
- ✅ Password hashing với bcrypt
- ✅ Role-based access control (RBAC)
- ✅ Consent management system
- ✅ Audit logging
- ✅ Rate limiting
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (ORM)
- ✅ CORS configuration
- ✅ Data encryption at rest

### Environment Variables

**QUAN TRỌNG:** Không bao giờ commit file `.env` vào Git!

```bash
# ✅ Được commit
.env.example

# ❌ KHÔNG commit
.env
.env.local
```

---

## 📊 Database Schema

### Core Tables

- `users` - Người dùng
- `student_profiles` - Profile học sinh
- `parent_profiles` - Profile phụ huynh
- `counselor_profiles` - Profile tư vấn viên
- `parent_student_links` - Liên kết parent-student
- `assessments` - Kết quả test GAD-7
- `voice_analyses` - Kết quả phân tích giọng nói
- `consent_records` - Quản lý consent
- `audit_logs` - Nhật ký audit

📖 **Chi tiết:** Xem [ARCHITECTURE.md - Database Schema](./ARCHITECTURE.md#️-database-schema---updated)

---

## 🤝 Contributing

Chúng tôi hoan nghênh mọi đóng góp!

### Quy trình đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

### Code Style

- **Python:** Follow PEP 8, use `black` & `isort`
- **TypeScript:** Follow Airbnb style guide
- **Commits:** Use [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📝 License

Dự án này được phát hành dưới giấy phép [MIT License](LICENSE).

---

## 👨‍💻 Team

- **Project Lead:** [Your Name]
- **Backend:** [Contributors]
- **Frontend:** [Contributors]
- **ML/AI:** [Contributors]

---

## 📧 Contact

- **Email:** contact@ai4mind.edu.vn
- **GitHub Issues:** [Report bugs here](https://github.com/thhieu2904/ai4mind-app/issues)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Google Gemini](https://ai.google.dev/) - AI analysis
- [Supabase](https://supabase.com/) - Database hosting
- [React](https://reactjs.org/) - Frontend framework

---

**⭐ Nếu dự án hữu ích, hãy cho chúng tôi một star!**
