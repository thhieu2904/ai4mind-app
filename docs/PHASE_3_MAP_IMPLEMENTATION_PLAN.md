# 🗺️ PHASE 3: MAP INTEGRATION - KẾ HOẠCH CHI TIẾT

## 📋 OVERVIEW

**Tính năng:** Bản đồ hiển thị trung tâm y tế/tư vấn gần nhất  
**Thời gian:** 4-6 giờ  
**Độ phức tạp:** ⭐⭐ (2/5)  
**Giá trị cho user:** ⭐⭐⭐⭐⭐ (5/5)

---

## 🎯 USER STORY

**Là một sinh viên**, tôi muốn:

- Tìm trung tâm tư vấn/y tế gần vị trí của tôi
- Xem trên bản đồ để dễ tìm đường
- Biết khoảng cách, địa chỉ, số điện thoại
- Lọc theo loại dịch vụ (tư vấn tâm lý, khám bệnh, khẩn cấp)

**Để:** Dễ dàng tìm kiếm hỗ trợ trực tiếp khi cần thiết

---

## 🗄️ STEP 1: DATABASE SCHEMA

### File: `database/create_medical_centers.sql`

```sql
-- Medical Centers Table
CREATE TABLE medical_centers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'hospital', 'clinic', 'counseling_center'
    address TEXT NOT NULL,
    district VARCHAR(100),
    city VARCHAR(100) NOT NULL DEFAULT 'Hồ Chí Minh',
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    services TEXT[], -- Array: ['tư vấn tâm lý', 'điều trị lo âu', ...]
    opening_hours JSONB, -- {"mon": "8:00-17:00", "tue": "8:00-17:00", ...}
    description TEXT,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_medical_centers_location ON medical_centers(latitude, longitude);
CREATE INDEX idx_medical_centers_city ON medical_centers(city);
CREATE INDEX idx_medical_centers_type ON medical_centers(type);
CREATE INDEX idx_medical_centers_active ON medical_centers(is_active);

-- Sample data (TP.HCM)
INSERT INTO medical_centers (name, type, address, district, city, phone, latitude, longitude, services, opening_hours) VALUES
('Bệnh viện Tâm thần TP.HCM', 'hospital', '766 Võ Văn Kiệt, P.1, Q.5', 'Quận 5', 'Hồ Chí Minh', '028 3855 5527', 10.7545, 106.6646, ARRAY['tư vấn tâm lý', 'điều trị trầm cảm', 'điều trị lo âu'],
'{"mon": "7:30-16:30", "tue": "7:30-16:30", "wed": "7:30-16:30", "thu": "7:30-16:30", "fri": "7:30-16:30", "sat": "7:30-11:30"}'),

('Trung tâm Tư vấn Sức khỏe Tâm thần - Bệnh viện Đại học Y Dược', 'counseling_center', '215 Hồng Bàng, P.11, Q.5', 'Quận 5', 'Hồ Chí Minh', '028 3855 4269', 10.7558, 106.6617, ARRAY['tư vấn tâm lý', 'trị liệu tâm lý'],
'{"mon": "7:00-16:00", "tue": "7:00-16:00", "wed": "7:00-16:00", "thu": "7:00-16:00", "fri": "7:00-16:00", "sat": "7:00-11:00"}'),

('Phòng khám Tâm lý Dr.Smile', 'clinic', '12 Nguyễn Văn Cừ, P.Nguyễn Cư Trinh, Q.1', 'Quận 1', 'Hồ Chí Minh', '0909 123 456', 10.7626, 106.6898, ARRAY['tư vấn tâm lý cá nhân', 'tư vấn học đường'],
'{"mon": "8:00-20:00", "tue": "8:00-20:00", "wed": "8:00-20:00", "thu": "8:00-20:00", "fri": "8:00-20:00", "sat": "8:00-17:00"}'),

('Trung tâm Tư vấn Tâm lý Trẻ - Đại học Sư Phạm', 'counseling_center', '280 An Dương Vương, P.4, Q.5', 'Quận 5', 'Hồ Chí Minh', '028 3835 3271', 10.7529, 106.6513, ARRAY['tư vấn tâm lý sinh viên', 'trị liệu nhóm'],
'{"mon": "8:00-17:00", "tue": "8:00-17:00", "wed": "8:00-17:00", "thu": "8:00-17:00", "fri": "8:00-17:00"}'),

('Bệnh viện Chợ Rẫy - Khoa Tâm thần', 'hospital', '201B Nguyễn Chí Thanh, P.12, Q.5', 'Quận 5', 'Hồ Chí Minh', '028 3855 4137', 10.7549, 106.6592, ARRAY['khám tâm thần', 'cấp cứu tâm thần', 'điều trị nội trú'],
'{"mon": "6:30-16:30", "tue": "6:30-16:30", "wed": "6:30-16:30", "thu": "6:30-16:30", "fri": "6:30-16:30", "sat": "6:30-11:30"}');
```

---

## 🔧 STEP 2: BACKEND IMPLEMENTATION

### 2.1. Model: `ai-service/app/models/medical_center.py`

```python
"""
Medical Center Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, ARRAY, JSON
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class MedicalCenter(Base):
    """Medical centers và counseling centers"""
    __tablename__ = "medical_centers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # hospital, clinic, counseling_center
    address = Column(Text, nullable=False)
    district = Column(String(100))
    city = Column(String(100), nullable=False, default='Hồ Chí Minh')
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    services = Column(ARRAY(Text))  # List of services
    opening_hours = Column(JSON)  # {"mon": "8:00-17:00", ...}
    description = Column(Text)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MedicalCenter {self.name}>"
```

### 2.2. Schema: `ai-service/app/schemas/medical_center.py`

```python
"""
Medical Center Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class MedicalCenterBase(BaseModel):
    """Base schema"""
    name: str
    type: str = Field(..., description="hospital, clinic, counseling_center")
    address: str
    district: Optional[str] = None
    city: str = "Hồ Chí Minh"
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    latitude: float
    longitude: float
    services: Optional[List[str]] = []
    opening_hours: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class MedicalCenterResponse(MedicalCenterBase):
    """Response schema với distance"""
    id: int
    is_active: bool
    distance: Optional[float] = Field(None, description="Distance in km")
    created_at: datetime

    class Config:
        from_attributes = True


class MedicalCenterWithDistance(MedicalCenterResponse):
    """Schema khi tính distance"""
    distance: float = Field(..., description="Distance in km from user location")


class NearbyRequest(BaseModel):
    """Request để tìm centers gần"""
    latitude: float = Field(..., description="User latitude")
    longitude: float = Field(..., description="User longitude")
    radius: Optional[float] = Field(10, description="Search radius in km")
    type: Optional[str] = Field(None, description="Filter by type")
    limit: Optional[int] = Field(20, description="Max results")
```

### 2.3. Service: `ai-service/app/services/medical_center_service.py`

```python
"""
Medical Center Service - Distance calculation
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from app.models.medical_center import MedicalCenter
from app.schemas.medical_center import MedicalCenterWithDistance


class MedicalCenterService:
    """Service xử lý logic cho medical centers"""

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between 2 points using Haversine formula
        Returns distance in kilometers
        """
        # Radius of Earth in kilometers
        R = 6371.0

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        return round(distance, 2)

    @staticmethod
    def get_nearby_centers(
        db: Session,
        user_lat: float,
        user_lon: float,
        radius: float = 10,
        center_type: Optional[str] = None,
        limit: int = 20
    ) -> List[MedicalCenterWithDistance]:
        """
        Get medical centers within radius, sorted by distance
        """
        # Query centers
        query = db.query(MedicalCenter).filter(MedicalCenter.is_active == True)

        if center_type:
            query = query.filter(MedicalCenter.type == center_type)

        centers = query.all()

        # Calculate distance and filter by radius
        centers_with_distance = []
        for center in centers:
            distance = MedicalCenterService.calculate_distance(
                user_lat, user_lon,
                float(center.latitude), float(center.longitude)
            )

            if distance <= radius:
                center_dict = {
                    "id": center.id,
                    "name": center.name,
                    "type": center.type,
                    "address": center.address,
                    "district": center.district,
                    "city": center.city,
                    "phone": center.phone,
                    "email": center.email,
                    "website": center.website,
                    "latitude": float(center.latitude),
                    "longitude": float(center.longitude),
                    "services": center.services,
                    "opening_hours": center.opening_hours,
                    "description": center.description,
                    "image_url": center.image_url,
                    "is_active": center.is_active,
                    "distance": distance,
                    "created_at": center.created_at
                }
                centers_with_distance.append(MedicalCenterWithDistance(**center_dict))

        # Sort by distance
        centers_with_distance.sort(key=lambda x: x.distance)

        return centers_with_distance[:limit]
```

### 2.4. API Endpoints: `ai-service/app/api/v1/endpoints/medical_centers.py`

```python
"""
Medical Centers API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.medical_center import MedicalCenter
from app.schemas.medical_center import (
    MedicalCenterResponse,
    MedicalCenterWithDistance,
    NearbyRequest
)
from app.services.medical_center_service import MedicalCenterService

router = APIRouter()


@router.get("/", response_model=List[MedicalCenterResponse])
def get_medical_centers(
    type: Optional[str] = Query(None, description="Filter by type"),
    city: Optional[str] = Query("Hồ Chí Minh", description="Filter by city"),
    limit: int = Query(50, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get list of medical centers

    - **type**: Filter by type (hospital, clinic, counseling_center)
    - **city**: Filter by city
    - **limit**: Max results (default 50, max 100)
    """
    query = db.query(MedicalCenter).filter(MedicalCenter.is_active == True)

    if type:
        query = query.filter(MedicalCenter.type == type)

    if city:
        query = query.filter(MedicalCenter.city == city)

    centers = query.offset(skip).limit(limit).all()

    return [MedicalCenterResponse.model_validate(c) for c in centers]


@router.get("/{center_id}", response_model=MedicalCenterResponse)
def get_medical_center(
    center_id: int,
    db: Session = Depends(get_db)
):
    """Get medical center by ID"""
    center = db.query(MedicalCenter).filter(MedicalCenter.id == center_id).first()

    if not center:
        raise HTTPException(status_code=404, detail="Medical center not found")

    return MedicalCenterResponse.model_validate(center)


@router.post("/nearby", response_model=List[MedicalCenterWithDistance])
def get_nearby_centers(
    request: NearbyRequest,
    db: Session = Depends(get_db)
):
    """
    Get medical centers near user location

    - **latitude**: User's latitude
    - **longitude**: User's longitude
    - **radius**: Search radius in km (default 10)
    - **type**: Filter by type (optional)
    - **limit**: Max results (default 20)
    """
    service = MedicalCenterService()

    centers = service.get_nearby_centers(
        db=db,
        user_lat=request.latitude,
        user_lon=request.longitude,
        radius=request.radius,
        center_type=request.type,
        limit=request.limit
    )

    return centers
```

### 2.5. Register Router: `ai-service/app/api/v1/api.py`

```python
# Thêm import
from app.api.v1.endpoints import medical_centers

# Thêm router
api_router.include_router(medical_centers.router, prefix="/medical-centers", tags=["Medical Centers"])
```

### 2.6. Update Models Init: `ai-service/app/models/__init__.py`

```python
from app.models.medical_center import MedicalCenter
```

---

## 🎨 STEP 3: FRONTEND IMPLEMENTATION

### 3.1. Install Dependencies

```bash
cd frontend
npm install @react-google-maps/api
```

### 3.2. Environment Variables: `frontend/.env`

```env
VITE_GOOGLE_MAPS_API_KEY=your_api_key_here
```

### 3.3. Service: `frontend/src/services/medicalCenterService.ts`

```typescript
/**
 * Medical Center Service - API client
 */
import api from "./api";

export interface MedicalCenter {
  id: number;
  name: string;
  type: "hospital" | "clinic" | "counseling_center";
  address: string;
  district?: string;
  city: string;
  phone?: string;
  email?: string;
  website?: string;
  latitude: number;
  longitude: number;
  services?: string[];
  opening_hours?: Record<string, string>;
  description?: string;
  image_url?: string;
  distance?: number;
  created_at: string;
}

export interface NearbyRequest {
  latitude: number;
  longitude: number;
  radius?: number;
  type?: string;
  limit?: number;
}

/**
 * Get all medical centers
 */
export const getMedicalCenters = async (
  type?: string,
  city?: string
): Promise<MedicalCenter[]> => {
  const params: any = {};
  if (type) params.type = type;
  if (city) params.city = city;

  const response = await api.get<MedicalCenter[]>("/api/v1/medical-centers", {
    params,
  });
  return response.data;
};

/**
 * Get medical center by ID
 */
export const getMedicalCenter = async (id: number): Promise<MedicalCenter> => {
  const response = await api.get<MedicalCenter>(
    `/api/v1/medical-centers/${id}`
  );
  return response.data;
};

/**
 * Get nearby medical centers
 */
export const getNearbyMedicalCenters = async (
  request: NearbyRequest
): Promise<MedicalCenter[]> => {
  const response = await api.post<MedicalCenter[]>(
    "/api/v1/medical-centers/nearby",
    request
  );
  return response.data;
};
```

### 3.4. Map Component: `frontend/src/components/MedicalCenterMap/MedicalCenterMap.tsx`

[Xem file đầy đủ trong implementation guide tiếp theo]

### 3.5. Map Page: `frontend/src/pages/MedicalCenterMapPage/MedicalCenterMapPage.tsx`

[Xem file đầy đủ trong implementation guide tiếp theo]

---

## 📝 STEP-BY-STEP CHECKLIST

### ✅ Backend (2-3 giờ)

- [ ] 1.1. Tạo SQL script (`create_medical_centers.sql`)
- [ ] 1.2. Run SQL trên Supabase/local DB
- [ ] 1.3. Tạo Model (`medical_center.py`)
- [ ] 1.4. Tạo Schema (`medical_center.py` in schemas)
- [ ] 1.5. Tạo Service (`medical_center_service.py`)
- [ ] 1.6. Tạo API endpoints (`medical_centers.py`)
- [ ] 1.7. Register router trong `api.py`
- [ ] 1.8. Update models `__init__.py`
- [ ] 1.9. Test API với Postman/Swagger

### ✅ Frontend (2-3 giờ)

- [ ] 2.1. Lấy Google Maps API key
- [ ] 2.2. Install `@react-google-maps/api`
- [ ] 2.3. Add API key vào `.env`
- [ ] 2.4. Tạo `medicalCenterService.ts`
- [ ] 2.5. Tạo Map component
- [ ] 2.6. Tạo Map page
- [ ] 2.7. Add route trong `App.tsx`
- [ ] 2.8. Add button trong Dashboard
- [ ] 2.9. Test trên browser

---

## 🎯 SUCCESS CRITERIA

✅ User có thể:

- Xem bản đồ với markers của các trung tâm
- Click marker để xem thông tin
- Xem list view dưới map
- Filter theo loại trung tâm
- Thấy khoảng cách từ vị trí hiện tại
- Click để call hoặc xem website

---

Sẵn sàng bắt đầu implement? 🚀
