"""
Medical Center Service
Business logic cho medical centers: tìm kiếm, tính khoảng cách, filter
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import math
from uuid import UUID

from app.models.medical_center import MedicalCenter
from app.schemas.medical_center import (
    MedicalCenterCreate,
    MedicalCenterUpdate,
    MedicalCenterResponse,
    NearbyRequest
)


class MedicalCenterService:
    """Service xử lý logic liên quan đến medical centers"""

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Tính khoảng cách giữa 2 điểm trên bề mặt trái đất sử dụng công thức Haversine
        
        Args:
            lat1, lon1: Vĩ độ và kinh độ điểm 1
            lat2, lon2: Vĩ độ và kinh độ điểm 2
            
        Returns:
            Khoảng cách tính bằng km
            
        Reference:
            https://en.wikipedia.org/wiki/Haversine_formula
        """
        # Bán kính trái đất (km)
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return round(distance, 2)  # Làm tròn 2 chữ số thập phân

    def get_all_centers(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        services: Optional[List[str]] = None
    ) -> List[MedicalCenter]:
        """
        Lấy danh sách tất cả medical centers
        
        Args:
            db: Database session
            skip: Số records bỏ qua (pagination)
            limit: Số records tối đa trả về
            services: Lọc theo dịch vụ (optional)
            
        Returns:
            List các medical centers
        """
        query = db.query(MedicalCenter)
        
        # Filter by services nếu có
        if services and len(services) > 0:
            # Tìm centers có ít nhất 1 trong các services
            # PostgreSQL ARRAY overlap operator: &&
            query = query.filter(MedicalCenter.services.overlap(services))
        
        return query.offset(skip).limit(limit).all()

    def get_center_by_id(self, db: Session, center_id: UUID) -> Optional[MedicalCenter]:
        """
        Lấy medical center theo ID
        
        Args:
            db: Database session
            center_id: UUID của center
            
        Returns:
            MedicalCenter object hoặc None nếu không tìm thấy
        """
        return db.query(MedicalCenter).filter(MedicalCenter.id == center_id).first()

    def get_nearby_centers(
        self, 
        db: Session, 
        request: NearbyRequest
    ) -> List[MedicalCenterResponse]:
        """
        Tìm các medical centers gần vị trí hiện tại
        
        Args:
            db: Database session
            request: NearbyRequest với lat, lng, radius, services, limit
            
        Returns:
            List các MedicalCenterResponse đã sắp xếp theo khoảng cách
        """
        # Lấy tất cả centers (hoặc filter by services)
        all_centers = self.get_all_centers(
            db=db, 
            skip=0, 
            limit=1000,  # Lấy nhiều để tính distance
            services=request.services
        )
        
        # Tính distance cho mỗi center
        centers_with_distance = []
        for center in all_centers:
            distance = self.calculate_distance(
                request.latitude,
                request.longitude,
                float(center.latitude),
                float(center.longitude)
            )
            
            # Chỉ lấy centers trong bán kính
            if distance <= request.radius:
                # Convert to response schema và thêm distance
                center_dict = center.to_dict()
                center_dict['distance'] = distance
                centers_with_distance.append(MedicalCenterResponse(**center_dict))
        
        # Sắp xếp theo khoảng cách (gần nhất trước)
        centers_with_distance.sort(key=lambda x: x.distance)
        
        # Giới hạn số lượng kết quả
        return centers_with_distance[:request.limit]

    def create_center(self, db: Session, center: MedicalCenterCreate) -> MedicalCenter:
        """
        Tạo medical center mới
        
        Args:
            db: Database session
            center: MedicalCenterCreate schema
            
        Returns:
            MedicalCenter đã tạo
        """
        db_center = MedicalCenter(**center.model_dump())
        db.add(db_center)
        db.commit()
        db.refresh(db_center)
        return db_center

    def update_center(
        self, 
        db: Session, 
        center_id: UUID, 
        center: MedicalCenterUpdate
    ) -> Optional[MedicalCenter]:
        """
        Cập nhật medical center
        
        Args:
            db: Database session
            center_id: UUID của center cần update
            center: MedicalCenterUpdate schema
            
        Returns:
            MedicalCenter đã update hoặc None nếu không tìm thấy
        """
        db_center = self.get_center_by_id(db, center_id)
        if not db_center:
            return None
        
        # Update chỉ các fields không None
        update_data = center.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_center, field, value)
        
        db.commit()
        db.refresh(db_center)
        return db_center

    def delete_center(self, db: Session, center_id: UUID) -> bool:
        """
        Xóa medical center
        
        Args:
            db: Database session
            center_id: UUID của center cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu không tìm thấy
        """
        db_center = self.get_center_by_id(db, center_id)
        if not db_center:
            return False
        
        db.delete(db_center)
        db.commit()
        return True


# Singleton instance
medical_center_service = MedicalCenterService()
