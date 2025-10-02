"""
Students API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user_student
from app.models.student import Student
from app.schemas.student import StudentResponse

router = APIRouter()


@router.get("/me", response_model=StudentResponse)
def get_current_student_profile(
    current_student: Student = Depends(get_current_user_student),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated student's profile
    
    **Authentication**: Required (student role only)
    
    **Returns**: Student profile with all details
    """
    return current_student


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_by_id(
    student_id: int,
    current_student: Student = Depends(get_current_user_student),
    db: Session = Depends(get_db)
):
    """
    Get student profile by ID
    
    **Authentication**: Required (student role only)
    
    **Access Control**:
    - Students can only view their own profile
    - Counselors can view assigned students (TODO: implement assignment check)
    - Admins can view all students
    
    **Returns**: Student profile
    """
    # Check access permission
    from app.api.dependencies import check_student_access
    check_student_access(student_id=student_id, current_student=current_student, db=db)
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    return student
