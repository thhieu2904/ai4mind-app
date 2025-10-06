"""
Medical Centers API Endpoints
Các endpoints để quản lý và tìm kiếm trung tâm y tế
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.medical_center import (
    MedicalCenterResponse,
    MedicalCenterCreate,
    MedicalCenterUpdate,
    NearbyRequest,
    NearbyResponse
)
from app.services.medical_center_service import medical_center_service

router = APIRouter()


@router.get("/", response_model=List[MedicalCenterResponse])
async def get_medical_centers(
    skip: int = Query(0, ge=0, description="Số records bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Số records tối đa"),
    services: Optional[str] = Query(None, description="Lọc theo dịch vụ (phân cách bởi dấu phẩy)"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả medical centers
    
    - **skip**: Pagination offset (mặc định 0)
    - **limit**: Số records tối đa (mặc định 20, max 100)
    - **services**: Lọc theo dịch vụ, ví dụ: "Tư vấn Tâm lý,Khám Tâm thần"
    """
    # Parse services từ string sang list
    services_list = None
    if services:
        services_list = [s.strip() for s in services.split(",")]
    
    centers = medical_center_service.get_all_centers(
        db=db,
        skip=skip,
        limit=limit,
        services=services_list
    )
    
    # Convert to response schema (không có distance)
    return [
        MedicalCenterResponse(
            **center.to_dict(),
            distance=None
        ) for center in centers
    ]


@router.get("/{center_id}", response_model=MedicalCenterResponse)
async def get_medical_center(
    center_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của 1 medical center
    
    - **center_id**: UUID của center
    """
    center = medical_center_service.get_center_by_id(db=db, center_id=center_id)
    
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy medical center với ID: {center_id}"
        )
    
    return MedicalCenterResponse(
        **center.to_dict(),
        distance=None
    )


@router.post("/nearby", response_model=NearbyResponse)
async def get_nearby_centers(
    request: NearbyRequest,
    db: Session = Depends(get_db)
):
    """
    Tìm các medical centers gần vị trí hiện tại
    
    - **latitude**: Vĩ độ của vị trí hiện tại
    - **longitude**: Kinh độ của vị trí hiện tại
    - **radius**: Bán kính tìm kiếm (km), mặc định 50km
    - **services**: Lọc theo dịch vụ cụ thể (optional)
    - **limit**: Số lượng kết quả tối đa (mặc định 10)
    
    **Ví dụ:**
    ```json
    {
        "latitude": 9.9345,
        "longitude": 106.3420,
        "radius": 50.0,
        "services": ["Tư vấn Tâm lý", "Khám Tâm thần"],
        "limit": 10
    }
    ```
    
    **Response:**
    Danh sách centers đã sắp xếp theo khoảng cách (gần nhất trước)
    """
    centers_with_distance = medical_center_service.get_nearby_centers(
        db=db,
        request=request
    )
    
    return NearbyResponse(
        centers=centers_with_distance,
        total=len(centers_with_distance),
        user_location={
            "latitude": request.latitude,
            "longitude": request.longitude
        }
    )


@router.post("/", response_model=MedicalCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_center(
    center: MedicalCenterCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo medical center mới
    
    **Chỉ dành cho admin** (TODO: thêm authentication)
    """
    db_center = medical_center_service.create_center(db=db, center=center)
    
    return MedicalCenterResponse(
        **db_center.to_dict(),
        distance=None
    )


@router.put("/{center_id}", response_model=MedicalCenterResponse)
async def update_medical_center(
    center_id: UUID,
    center: MedicalCenterUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin medical center
    
    **Chỉ dành cho admin** (TODO: thêm authentication)
    """
    db_center = medical_center_service.update_center(
        db=db,
        center_id=center_id,
        center=center
    )
    
    if not db_center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy medical center với ID: {center_id}"
        )
    
    return MedicalCenterResponse(
        **db_center.to_dict(),
        distance=None
    )


@router.delete("/{center_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_center(
    center_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Xóa medical center
    
    **Chỉ dành cho admin** (TODO: thêm authentication)
    """
    success = medical_center_service.delete_center(db=db, center_id=center_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy medical center với ID: {center_id}"
        )
    
    return None
