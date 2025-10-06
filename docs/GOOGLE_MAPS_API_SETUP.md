# 🗝️ HƯỚNG DẪN LẤY GOOGLE MAPS API KEY

## 🎯 Bước 1: Truy cập Google Cloud Console

1. Vào: https://console.cloud.google.com/
2. Đăng nhập bằng Gmail của bạn
3. Tạo project mới hoặc chọn project có sẵn

## 🎯 Bước 2: Enable APIs

1. Vào **APIs & Services** → **Library**
2. Tìm và enable 3 APIs sau:
   - ✅ **Maps JavaScript API** (bắt buộc - cho map)
   - ✅ **Geocoding API** (optional - cho search địa chỉ)
   - ✅ **Distance Matrix API** (optional - tính khoảng cách chính xác)

## 🎯 Bước 3: Tạo API Key

1. Vào **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **API Key**
3. Copy API Key (dạng: `AIzaSyC...`)
4. Click **Restrict Key** (recommended):
   - **Application restrictions:** HTTP referrers
   - **Website restrictions:**
     - `http://localhost:5173/*`
     - `http://localhost:3000/*`
     - `https://yourdomain.com/*` (production)
   - **API restrictions:**
     - Maps JavaScript API
     - Geocoding API
     - Distance Matrix API

## 🎯 Bước 4: Thêm vào Project

### Backend: `ai-service/.env`

```env
# Google Maps API (optional - nếu cần geocoding ở backend)
GOOGLE_MAPS_API_KEY=AIzaSyC...your-key-here
```

### Frontend: `frontend/.env`

```env
# Google Maps API (required)
VITE_GOOGLE_MAPS_API_KEY=AIzaSyC...your-key-here
```

## 💰 Chi phí (FREE TIER)

Google Maps cung cấp **$200 credit/tháng** miễn phí:

| API                     | Free Monthly Quota | Price sau khi hết quota |
| ----------------------- | ------------------ | ----------------------- |
| **Maps JavaScript API** | 28,000 loads       | $7 per 1,000 loads      |
| **Geocoding API**       | 40,000 requests    | $5 per 1,000 requests   |
| **Distance Matrix API** | 40,000 elements    | $5 per 1,000 elements   |

**Ước tính cho project:**

- 500 users × 10 map views/tháng = 5,000 loads
- **Cost: $0** (trong free tier)

## ⚠️ LƯU Ý QUAN TRỌNG

### ✅ Nên làm:

- Restrict API key (HTTP referrers + API restrictions)
- Set budget alerts trong Google Cloud
- Monitor usage trong Console

### ❌ Không nên:

- Commit API key vào Git (thêm `.env` vào `.gitignore`)
- Public API key không restrict
- Share API key với người khác

## 🔐 Bảo mật API Key

**File `.gitignore` cần có:**

```
# Environment variables
.env
.env.local
.env.production
```

**File `.env.example` để team biết:**

```env
# Google Maps API Key
VITE_GOOGLE_MAPS_API_KEY=your-api-key-here
```

## 🎯 Xác nhận Setup thành công

Sau khi có API key, test bằng cách:

1. **Test trong browser console:**

```javascript
// Vào https://developers.google.com/maps/documentation/javascript/examples/map-simple
// Thay YOUR_API_KEY bằng key của bạn
```

2. **Test trong app:**

```typescript
// Map component sẽ load và hiển thị bản đồ
// Nếu lỗi → Check console để xem error message
```

## 🆘 Troubleshooting

### Lỗi: "This API key is not authorized to use this service"

→ Chưa enable API trong Google Cloud Console

### Lỗi: "RefererNotAllowedMapError"

→ Chưa add localhost vào HTTP referrers

### Lỗi: "ApiNotActivatedMapError"

→ Chưa enable Maps JavaScript API

---

**⏱️ Thời gian setup: 5-10 phút**

Xong rồi báo tôi nhé! 🚀
