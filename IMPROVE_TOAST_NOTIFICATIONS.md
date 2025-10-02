# Fix: Replace Alert with Toast Notifications

## Problem

VoiceRecordingPage uses `alert()` which:

- ❌ Blocks UI (user must click OK)
- ❌ Looks ugly and unprofessional
- ❌ Cannot be styled
- ❌ Interrupts user flow

## Solution: Use React Toast Library

### Option 1: react-toastify (Recommended)

#### Install

```bash
cd frontend
npm install react-toastify
```

#### Setup in App.tsx

```tsx
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  return (
    <>
      <ToastContainer
        position="top-center"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
      {/* Your app routes */}
    </>
  );
}
```

#### Update VoiceRecordingPage.tsx

**Replace:**

```tsx
import React, { useState, useRef, useEffect } from "react";
```

**With:**

```tsx
import React, { useState, useRef, useEffect } from "react";
import { toast } from "react-toastify";
```

**Replace all alerts:**

```tsx
// ❌ Before
alert("Không thể truy cập microphone. Vui lòng cho phép quyền truy cập.");

// ✅ After
toast.error(
  "Không thể truy cập microphone. Vui lòng cho phép quyền truy cập.",
  {
    position: "top-center",
    autoClose: 4000,
  }
);
```

**All replacements:**

```tsx
// Line 53
toast.warning("Dữ liệu không hợp lệ. Vui lòng làm bài đánh giá GAD-7 trước.");

// Line 96
toast.error("Không thể truy cập microphone. Vui lòng cho phép quyền truy cập.");

// Line 122
toast.info("Vui lòng ghi âm trước khi phân tích.");

// Line 127
toast.warning("Thời lượng ghi âm quá ngắn. Vui lòng ghi âm ít nhất 5 giây.");

// Line 173
toast.error(errorMessage);
```

### Option 2: Custom Toast Component (Lightweight)

Create `frontend/src/components/Toast/Toast.tsx`:

```tsx
import React, { useEffect } from "react";
import "./Toast.css";

interface ToastProps {
  message: string;
  type: "success" | "error" | "warning" | "info";
  onClose: () => void;
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({
  message,
  type,
  onClose,
  duration = 3000,
}) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`toast toast-${type}`}>
      <span className="toast-icon">
        {type === "success" && "✓"}
        {type === "error" && "✕"}
        {type === "warning" && "⚠"}
        {type === "info" && "ℹ"}
      </span>
      <span className="toast-message">{message}</span>
    </div>
  );
};

export default Toast;
```

Create `frontend/src/components/Toast/Toast.css`:

```css
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  min-width: 300px;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 9999;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.toast-success {
  background: #10b981;
  color: white;
}

.toast-error {
  background: #ef4444;
  color: white;
}

.toast-warning {
  background: #f59e0b;
  color: white;
}

.toast-info {
  background: #3b82f6;
  color: white;
}

.toast-icon {
  font-size: 20px;
  font-weight: bold;
}

.toast-message {
  flex: 1;
  font-size: 14px;
}
```

Use in VoiceRecordingPage:

```tsx
import Toast from "../../components/Toast/Toast";

const VoiceRecordingPage: React.FC = () => {
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error" | "warning" | "info";
  } | null>(null);

  const showToast = (
    message: string,
    type: "success" | "error" | "warning" | "info"
  ) => {
    setToast({ message, type });
  };

  // Replace alerts:
  // alert("Error") → showToast("Error", 'error')

  return (
    <MainLayout>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      {/* Rest of component */}
    </MainLayout>
  );
};
```

## Recommendation

**Use react-toastify** - It's:

- ✅ Battle-tested
- ✅ Feature-rich (progress bar, dismiss, stack)
- ✅ Accessible
- ✅ Easy to implement
- ✅ Beautiful default styles
- ✅ Only ~10KB gzipped

## Benefits

| Feature          | alert()            | Toast       |
| ---------------- | ------------------ | ----------- |
| **Blocking**     | ❌ YES             | ✅ NO       |
| **Styling**      | ❌ Browser default | ✅ Custom   |
| **UX**           | ❌ Poor            | ✅ Great    |
| **Auto-dismiss** | ❌ Manual          | ✅ Auto     |
| **Position**     | ❌ Center only     | ✅ Anywhere |
| **Stack**        | ❌ One at a time   | ✅ Multiple |
| **Progress**     | ❌ NO              | ✅ YES      |

## Implementation Steps

1. Install react-toastify
2. Add ToastContainer to App.tsx
3. Replace all alerts in VoiceRecordingPage
4. Test all error cases
5. Customize styles if needed

This will make the app feel much more modern and professional! 🎉
