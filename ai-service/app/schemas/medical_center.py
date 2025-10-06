"""
Medical Center Schemas
Pydantic schemas cho validation và serialization
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID


class MedicalCenterBase(BaseModel):
    """Base schema với các trường chung"""
    name: str = Field(..., min_length=1, max_length=255, description="Tên trung tâm y tế")
    address: str = Field(..., min_length=1, description="Địa chỉ đầy đủ")
    latitude: float = Field(..., ge=-90, le=90, description="Vĩ độ (-90 đến 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Kinh độ (-180 đến 180)")
    phone: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    email: Optional[str] = Field(None, max_length=100, description="Email")
    website: Optional[str] = Field(None, max_length=255, description="Website")
    services: List[str] = Field(default_factory=list, description="Danh sách dịch vụ")
    opening_hours: Dict[str, str] = Field(default_factory=dict, description="Giờ mở cửa")
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    image_url: Optional[str] = Field(None, description="URL hình ảnh")

    @validator('services')
    def validate_services(cls, v):
        """Validate services không rỗng"""
        if not v or len(v) == 0:
            raise ValueError("Phải có ít nhất 1 dịch vụ")
        return v

    @validator('opening_hours')
    def validate_opening_hours(cls, v):
        """Validate opening_hours format"""
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if v:
            for day in v.keys():
                if day.lower() not in valid_days:
                    raise ValueError(f"Ngày '{day}' không hợp lệ. Chỉ chấp nhận: {', '.join(valid_days)}")
        return v


class MedicalCenterCreate(MedicalCenterBase):
    """Schema để tạo mới medical center"""
    pass


class MedicalCenterUpdate(BaseModel):
    """Schema để cập nhật medical center (tất cả fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    services: Optional[List[str]] = None
    opening_hours: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class MedicalCenterInDB(MedicalCenterBase):
    """Schema cho dữ liệu từ database"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class MedicalCenterResponse(MedicalCenterInDB):
    """
    Schema cho API response
    Có thêm trường distance (tính toán runtime, không lưu DB)
    """
    distance: Optional[float] = Field(None, description="Khoảng cách tính từ vị trí hiện tại (km)")

    class Config:
        from_attributes = True


class NearbyRequest(BaseModel):
    """Schema cho request tìm kiếm centers gần"""
    latitude: float = Field(..., ge=-90, le=90, description="Vĩ độ của vị trí hiện tại")
    longitude: float = Field(..., ge=-180, le=180, description="Kinh độ của vị trí hiện tại")
    radius: Optional[float] = Field(50.0, ge=0.1, le=500, description="Bán kính tìm kiếm (km), mặc định 50km")
    services: Optional[List[str]] = Field(None, description="Lọc theo dịch vụ cụ thể")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Số lượng kết quả tối đa")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 9.9345,
                "longitude": 106.3420,
                "radius": 50.0,
                "services": ["Tư vấn Tâm lý", "Khám Tâm thần"],
                "limit": 10
            }
        }


class NearbyResponse(BaseModel):
    """Schema cho response của nearby search"""
    centers: List[MedicalCenterResponse]
    total: int = Field(..., description="Tổng số centers tìm thấy")
    user_location: Dict[str, float] = Field(..., description="Vị trí người dùng")

    class Config:
        json_schema_extra = {
            "example": {
                "centers": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Bệnh viện Đa khoa Trà Vinh",
                        "address": "Số 1, Đường Nguyễn Đáng, Phường 4, TP. Trà Vinh",
                        "latitude": 9.9345,
                        "longitude": 106.3420,
                        "phone": "0294.3862.901",
                        "services": ["Khoa Tâm thần", "Tư vấn Tâm lý"],
                        "distance": 2.5
                    }
                ],
                "total": 1,
                "user_location": {"latitude": 9.9345, "longitude": 106.3420}
            }
        }
