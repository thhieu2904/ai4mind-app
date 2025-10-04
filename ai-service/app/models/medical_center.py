"""
Medical Center Model
Lưu thông tin các trung tâm y tế hỗ trợ sức khỏe tâm thần
"""
from sqlalchemy import Column, String, Text, DECIMAL, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.models import Base


class MedicalCenter(Base):
    """
    Model cho bảng medical_centers
    Lưu thông tin các trung tâm y tế (bệnh viện, phòng khám, trung tâm tư vấn)
    """
    __tablename__ = "medical_centers"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Thông tin cơ bản
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # Tọa độ địa lý (để tính khoảng cách)
    latitude = Column(DECIMAL(10, 8), nullable=False)  # -90.00000000 đến 90.00000000
    longitude = Column(DECIMAL(11, 8), nullable=False)  # -180.00000000 đến 180.00000000
    
    # Thông tin liên hệ
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Dịch vụ cung cấp (array of strings)
    # Ví dụ: ['Khám Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Nội trú']
    services = Column(ARRAY(Text), nullable=False, default=list)
    
    # Giờ mở cửa (JSON)
    # Format: {"monday": "08:00-17:00", "tuesday": "08:00-17:00", ...}
    opening_hours = Column(JSONB, nullable=False, default=dict)
    
    # Hình ảnh
    image_url = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<MedicalCenter(id={self.id}, name='{self.name}', address='{self.address[:50]}...')>"

    def to_dict(self):
        """
        Convert model to dictionary
        Useful for serialization
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "address": self.address,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "services": self.services,
            "opening_hours": self.opening_hours,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
