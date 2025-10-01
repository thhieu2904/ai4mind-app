# AI4Mind - Development Roadmap

## 📅 PHASE 1: CORE BACKEND (2-3 tuần)

### Week 1: Authentication & User Management ✅ (Partially Done)

- [x] Database models created
- [x] Database initialized with Supabase
- [x] Test data seeded
- [ ] **TODO: Implement Authentication Endpoints**
  - `POST /api/v1/auth/register` - Đăng ký (Student/Parent)
  - `POST /api/v1/auth/login` - Login (trả về JWT token)
  - `GET /api/v1/auth/me` - Get current user
  - `POST /api/v1/auth/refresh` - Refresh token
  - `POST /api/v1/auth/logout` - Logout
- [ ] **TODO: JWT Middleware**
  - Create dependency `get_current_user(token: str)`
  - Role checking decorator `@require_role("student")`

### Week 2: Assessment & AI Chat

- [ ] **Assessment Endpoints**

  - `POST /api/v1/assessments` - Submit GAD-7 assessment
    - Validate answers (7 questions, 0-3 each)
    - Calculate total score
    - Call Gemini to analyze → save analysis
    - Return result + recommendations
  - `GET /api/v1/assessments` - Get assessment history
  - `GET /api/v1/assessments/{id}` - Get specific assessment
  - `GET /api/v1/assessments/stats` - Get statistics (trend over time)

- [ ] **Chat Endpoints** ✅ (Gemini service ready)
  - `POST /api/v1/conversations` - Create new conversation
  - `GET /api/v1/conversations` - List conversations
  - `GET /api/v1/conversations/{id}` - Get conversation with messages
  - `POST /api/v1/conversations/{id}/messages` - Send message
    - Get conversation history
    - Call `gemini_service.chat(message, history)`
    - Save both user message & AI response
    - Update `last_message_at`
  - `DELETE /api/v1/conversations/{id}` - Delete conversation

### Week 3: Parent Consent & Counselor Access

- [ ] **Parent Consent Endpoints**

  - `POST /api/v1/consents` - Parent request access
  - `GET /api/v1/consents` - Student view pending requests
  - `PUT /api/v1/consents/{id}` - Approve/reject request
  - `GET /api/v1/students/{id}/assessments` - Parent view (if approved)

- [ ] **Counselor Endpoints**
  - `GET /api/v1/counselor/students` - List all students
  - `GET /api/v1/counselor/students?severity=severe` - Filter by severity
  - `GET /api/v1/counselor/students/{id}` - View student detail
  - `GET /api/v1/counselor/dashboard` - Statistics dashboard

---

## 📅 PHASE 2: VOICE ANALYSIS (1-2 tuần)

### Week 4: Voice Service Implementation

- [ ] **Voice Analysis Endpoints** (in voice-analysis service)

  - `POST /api/v1/voice/transcribe` - Upload audio → transcribe
    - Validate file (wav, mp3, m4a, max 50MB)
    - Save to `shared/audio-files/`
    - Load Whisper model
    - Transcribe → return text
  - `POST /api/v1/voice/analyze` - Full analysis
    - Transcribe
    - Emotion detection (optional, can skip for MVP)
    - Return results

- [ ] **Integration with AI Service**
  - AI service calls voice service via HTTP
  - `POST /api/v1/conversations/{id}/voice-message`
    - Upload audio
    - Call voice service
    - Save transcription to voice_analyses table
    - Create message with transcribed text
    - Get Gemini response
    - Return both transcription & AI response

---

## 📅 PHASE 3: FRONTEND (3-4 tuần)

### Week 5-6: Core UI Components

- [ ] **Authentication Pages**

  - `/login` - Login form
  - `/register` - Register (choose Student/Parent)
  - Protected routes with JWT token

- [ ] **Student Dashboard**
  - `/dashboard` - Overview (recent assessments, conversations)
  - `/assessment` - Take GAD-7 test
  - `/assessment/results` - View results with Gemini analysis
  - `/assessment/history` - Historical data with chart
  - `/chat` - List conversations
  - `/chat/{id}` - Chat interface with Gemini
  - `/profile` - Edit profile, manage parent consents

### Week 7: Voice & Advanced Features

- [ ] **Voice Recording**

  - Record audio in browser (`MediaRecorder API`)
  - Upload to backend
  - Display transcription + AI response

- [ ] **Parent Portal**

  - `/parent/dashboard` - View children (with consent)
  - `/parent/child/{id}` - View child's assessment history
  - `/parent/reports` - Download Excel reports

- [ ] **Counselor Portal**
  - `/counselor/dashboard` - Statistics overview
  - `/counselor/students` - Student list with filters
  - `/counselor/student/{id}` - Detailed view
  - `/counselor/reports` - Export data

### Week 8: Admin Panel

- [ ] **Admin Dashboard**
  - `/admin/users` - User management
  - `/admin/counselors` - Manage counselors
  - `/admin/system` - System settings
  - `/admin/reports` - Platform-wide statistics

---

## 📅 PHASE 4: POLISH & DEPLOY (1-2 tuần)

### Week 9: Testing & Bug Fixes

- [ ] **Testing**

  - Unit tests for backend services
  - Integration tests for API endpoints
  - E2E tests for critical user flows
  - Load testing (can system handle 100 concurrent users?)

- [ ] **Security Audit**
  - SQL injection prevention (SQLAlchemy handles this)
  - XSS prevention (React handles this)
  - CSRF tokens
  - Rate limiting (prevent API abuse)
  - Input validation

### Week 10: Deployment

- [ ] **Backend Deployment**

  - Docker containers for ai-service & voice-analysis
  - Deploy to cloud (Railway, Render, or DigitalOcean)
  - Setup environment variables
  - Database migration to production

- [ ] **Frontend Deployment**

  - Build production bundle (`npm run build`)
  - Deploy to Vercel/Netlify
  - Setup custom domain

- [ ] **Monitoring**
  - Setup error tracking (Sentry)
  - Setup analytics (Google Analytics)
  - Setup uptime monitoring (UptimeRobot)

---

## 🎯 MVP (Minimum Viable Product) Scope

**Để có MVP chạy được, cần hoàn thành:**

### ✅ Must Have (MVP Core)

1. ✅ Database setup (DONE)
2. ✅ Gemini integration (DONE)
3. [ ] Authentication (login/register)
4. [ ] GAD-7 assessment (take test, view results)
5. [ ] AI chat (basic conversation)
6. [ ] Student dashboard (view assessments + chat)

### 🟡 Should Have (MVP+)

7. [ ] Voice transcription (Whisper)
8. [ ] Parent consent system
9. [ ] Counselor portal (view students)
10. [ ] Assessment history chart

### 🔵 Nice to Have (Post-MVP)

11. [ ] Voice emotion detection
12. [ ] Admin dashboard
13. [ ] Excel export for parents
14. [ ] Email notifications
15. [ ] Mobile responsive design

---

## 📊 ESTIMATED TIMELINE

```
┌─────────────────────────────────────────────────────────┐
│  MVP Core: 4-5 weeks                                    │
├─────────────────────────────────────────────────────────┤
│  Week 1-3: Backend APIs (auth, assessment, chat)        │
│  Week 4-5: Frontend (login, dashboard, assessment, chat)│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Full Product: 8-10 weeks                               │
├─────────────────────────────────────────────────────────┤
│  Week 1-3: Backend Core                                 │
│  Week 4:   Voice Analysis                               │
│  Week 5-8: Frontend (all features)                      │
│  Week 9:   Testing & Bug Fixes                          │
│  Week 10:  Deployment                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 TECHNICAL STACK SUMMARY

### Backend

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (Supabase)
- **AI**: Google Gemini 2.0 Flash
- **Voice**: OpenAI Whisper
- **Auth**: JWT tokens
- **Cache**: Redis (optional)

### Frontend

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **State**: React Query (server state)
- **Routing**: React Router v6
- **HTTP**: Axios

### DevOps

- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Hosting**: Railway/Render (backend), Vercel (frontend)
- **Monitoring**: Sentry (errors), Analytics

---

## 💡 NEXT IMMEDIATE STEPS

**Nếu bắt đầu code ngay, làm theo thứ tự này:**

### 1. **Setup API Structure** (1-2h)

```bash
cd ai-service
mkdir -p app/api/v1/endpoints
touch app/api/v1/endpoints/{auth,assessments,conversations,consents,counselor}.py
```

### 2. **Implement Auth Endpoints** (3-4h)

- Create `auth.py` with login/register
- Test with Postman/Thunder Client
- Get JWT token working

### 3. **Implement Assessment Endpoints** (2-3h)

- Create `assessments.py`
- Integrate with Gemini service (already done!)
- Test submitting GAD-7

### 4. **Implement Chat Endpoints** (2-3h)

- Create `conversations.py`
- Use existing `gemini_service.chat()`
- Test conversation flow

### 5. **Start Frontend** (after backend works)

- Create login page
- Create dashboard
- Create assessment form
- Create chat UI

---

## 📝 SUCCESS METRICS

**How to know if project is successful:**

### Technical Metrics

- ✅ All API endpoints return < 500ms
- ✅ 0 critical security vulnerabilities
- ✅ 95%+ uptime
- ✅ Handle 100+ concurrent users

### User Metrics

- 🎯 50+ students signed up in first month
- 🎯 200+ assessments completed
- 🎯 1000+ AI conversations
- 🎯 10+ counselors registered
- 🎯 4.0+ star rating from students

### Impact Metrics

- 💚 30% of students report reduced anxiety
- 💚 Students rate AI chatbot 4/5 helpful
- 💚 Counselors find platform saves time
- 💚 Parents feel more connected

---

## 🚨 RISKS & MITIGATION

### Risk 1: Gemini API Cost

- **Mitigation**: Use free tier (Gemini 2.0 Flash is free up to 1500 RPM)
- **Alternative**: Switch to Gemini 1.5 Flash if needed

### Risk 2: Voice Analysis Slow

- **Mitigation**: Use smaller Whisper model (base)
- **Alternative**: Background job processing

### Risk 3: Student Privacy Concerns

- **Mitigation**: Strong consent system, clear privacy policy
- **Alternative**: Allow students to delete their data anytime

### Risk 4: Low Adoption

- **Mitigation**: Partnership with university counseling center
- **Alternative**: Marketing campaign, student ambassadors

---

## 🎓 LEARNING OUTCOMES

**By completing this project, you'll learn:**

1. ✅ **Backend Development**: FastAPI, SQLAlchemy, PostgreSQL
2. ✅ **AI Integration**: Gemini API, Whisper, prompt engineering
3. ✅ **Authentication**: JWT, bcrypt, role-based access control
4. ✅ **Microservices**: API Gateway pattern, service-to-service communication
5. ✅ **Frontend**: React, TypeScript, Material-UI
6. ✅ **DevOps**: Docker, CI/CD, cloud deployment
7. ✅ **Database Design**: Normalization, relationships, indexes
8. ✅ **API Design**: RESTful principles, error handling, validation

---

**Ready to start? Suggest we begin with Authentication endpoints! 🚀**
