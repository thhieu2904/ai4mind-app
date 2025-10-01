# AI4Mind - Frontend

React + TypeScript + Vite frontend cho AI4Mind platform.

## 🚀 Setup

### 1. Kiểm tra Node.js

```powershell
node --version  # Cần >= 18.x
npm --version
```

Nếu chưa có, download từ: https://nodejs.org/

### 2. Cài Dependencies

```powershell
cd frontend
npm install
```

### 3. Configuration

```powershell
# Copy environment template
Copy-Item ..\.env.example .env

# Chỉnh VITE_API_URL nếu cần
# VITE_API_URL=http://localhost:8000
```

### 4. Chạy Development Server

```powershell
npm run dev
```

Truy cập: http://localhost:3000

## 📦 Available Scripts

```powershell
# Development
npm run dev              # Start dev server

# Production
npm run build            # Build for production
npm run preview          # Preview production build

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking
npm run format           # Format code with Prettier

# Testing (sẽ thêm sau)
npm test                 # Run tests
```

## 📁 Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── common/      # Shared components
│   │   ├── auth/        # Auth components
│   │   ├── student/     # Student features
│   │   ├── parent/      # Parent features
│   │   ├── counselor/   # Counselor features
│   │   └── admin/       # Admin features
│   ├── contexts/        # React contexts
│   ├── hooks/           # Custom hooks
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── package.json
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config
└── README.md
```

## 🎨 UI Library

Project sử dụng **Material-UI (MUI)**:
- https://mui.com/material-ui/

Các components chính:
- `Button`, `TextField`, `Card`, `Dialog`
- `AppBar`, `Drawer`, `Menu`
- `DataGrid`, `Chart`

## 🔌 API Integration

### API Client Setup

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Example Service

```typescript
// src/services/authService.ts
import api from './api';

export const login = async (email: string, password: string) => {
  const response = await api.post('/api/v1/auth/login', {
    email,
    password,
  });
  return response.data;
};
```

## 🎯 Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AI4Mind
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

## 🧪 Testing

```powershell
# Sẽ setup sau với Vitest
npm test
```

## 🚀 Deployment

```powershell
# Build production
npm run build

# Output in dist/ folder
# Deploy dist/ to hosting service
```

## 📝 Code Style

- **ESLint:** Code linting
- **Prettier:** Code formatting
- **TypeScript:** Type safety

Run before commit:
```powershell
npm run lint
npm run format
npm run type-check
```

## 💡 Tips

1. **Hot Reload:** Code changes auto-reload browser
2. **React DevTools:** Install browser extension
3. **TypeScript:** Use types cho type safety
4. **Component Organization:** Nhỏ gọn, reusable
