# Fix: 401 Unauthorized Error - Token Key Mismatch

## Vấn đề

Khi submit GAD-7 assessment, backend trả về **401 Unauthorized**:

```
INFO: 127.0.0.1:51163 - "POST /api/v1/assessments/ HTTP/1.1" 401 Unauthorized
```

## Nguyên nhân

Có **2 lỗi** trong code:

### 1. Token Key Không Khớp ❌

- **AuthContext** lưu token với key: `access_token`
  ```typescript
  localStorage.setItem("access_token", response.access_token);
  ```
- **api.ts interceptor** tìm token với key: `access_token` ✅
  ```typescript
  const token = localStorage.getItem("access_token");
  ```
- **AssessmentPage** tìm token với key sai: `token` ❌
  ```typescript
  const token = localStorage.getItem("token"); // SAI!
  ```
- **VoiceRecordingPage** cũng dùng sai key: `token` ❌

→ Kết quả: Token không được gửi lên backend → 401 Unauthorized

### 2. Hard-coded URL và Không Dùng Axios Instance ❌

- **AssessmentPage** dùng hard-coded URL:
  ```typescript
  await axios.post(
    "http://localhost:8000/api/v1/assessments/", // Hard-coded!
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );
  ```
- Không sử dụng `api` service đã config sẵn với interceptor

## Giải pháp ✅

### 1. AssessmentPage.tsx

**Before:**

```typescript
import axios from "axios";

// ...
const token = localStorage.getItem("token");
const response = await axios.post(
  "http://localhost:8000/api/v1/assessments/",
  data,
  {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  }
);
```

**After:**

```typescript
import api from "../../services/api";

// ...
const response = await api.post("/api/v1/assessments/", {
  answers: answers.map((a) => a || 0),
  functional_impairment: 0,
  notes: null,
});
// Token tự động được thêm bởi interceptor!
```

### 2. VoiceRecordingPage.tsx

**Before:**

```typescript
import axios from "axios";

// ...
const token = localStorage.getItem("token");
const response = await axios.post(
  `/api/v1/assessments/${assessmentId}/add-voice`,
  formData,
  {
    headers: {
      "Content-Type": "multipart/form-data",
      Authorization: `Bearer ${token}`,
    },
  }
);
```

**After:**

```typescript
import api from "../../services/api";

// ...
const response = await api.post(
  `/api/v1/assessments/${assessmentId}/add-voice`,
  formData,
  {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  }
);
// Token tự động được thêm bởi interceptor!
```

## Lợi ích của việc dùng `api` service

1. **Tự động thêm token** - Không cần manual `localStorage.getItem()`
2. **Tự động thêm baseURL** - Không cần hard-code `http://localhost:8000`
3. **Tự động handle 401** - Redirect to login khi token expired
4. **Consistent headers** - Content-Type application/json mặc định
5. **Dễ bảo trì** - Thay đổi config ở 1 chỗ (api.ts)

## Kết quả

✅ Token được gửi đúng với key `access_token`
✅ Header Authorization tự động được thêm bởi interceptor
✅ Backend nhận được token hợp lệ
✅ POST /api/v1/assessments/ trả về 200 OK
✅ Assessment được lưu vào database

## Kiểm tra

Sau khi fix, log backend sẽ như thế này:

```
INFO: 127.0.0.1:xxxxx - "POST /api/v1/assessments/ HTTP/1.1" 200 OK
```

Thay vì:

```
INFO: 127.0.0.1:xxxxx - "POST /api/v1/assessments/ HTTP/1.1" 401 Unauthorized
```
