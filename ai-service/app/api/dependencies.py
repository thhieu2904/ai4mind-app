"""
API Dependencies
Reusable security checks and authorization helpers
"""
from typing import Optional, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent, ParentConsent
from app.models.voice_analysis import VoiceAnalysis


def get_parent_profile(db: Session, user_id: int) -> Optional[Parent]:
    """Get parent profile for the current authenticated user."""
    return db.query(Parent).filter(Parent.user_id == user_id).first()


def get_parent_student_ids(db: Session, parent_id: int) -> Set[int]:
    """Return student IDs that parent can access via emergency contact or approved consent."""
    emergency_contact_ids = {
        student_id
        for (student_id,) in db.query(Student.id)
        .filter(Student.emergency_contact_parent_id == parent_id)
        .all()
    }

    consent_ids = {
        student_id
        for (student_id,) in db.query(ParentConsent.student_id)
        .filter(
            ParentConsent.parent_id == parent_id,
            ParentConsent.is_approved == 1,
        )
        .all()
    }

    return emergency_contact_ids.union(consent_ids)


async def get_current_user_student(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Student:
    """
    Get current user's student profile
    
    Security: Ensures user is a student and has valid profile
    
    Raises:
        HTTPException 403: If user is not a student
        HTTPException 404: If student profile not found
    
    Returns:
        Student: Current user's student profile
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this resource"
        )
    
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return student


async def check_student_access(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Student:
    """
    Check if current user has access to a specific student's data
    
    Access rules:
    - Students: Can only access their own data
    - Counselors: Can access assigned students (TODO: implement assignments)
    - Admins: Can access all students
    - Parents: Can access their children (TODO: implement parent-child relationship)
    
    Args:
        student_id: Target student ID
        current_user: Current authenticated user
        db: Database session
    
    Raises:
        HTTPException 403: If access denied
        HTTPException 404: If student not found
    
    Returns:
        Student: Target student profile
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Admin can access all
    if current_user.role == UserRole.ADMIN:
        return student
    
    # Student can only access their own data
    if current_user.role == UserRole.STUDENT:
        if student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own data"
            )
        return student
    
    # Counselor access (TODO: check assignments table)
    if current_user.role == UserRole.COUNSELOR:
        # For now, allow counselors to access all students
        # TODO: Implement student_counselor_assignments table check
        return student
    
    # Parent access
    if current_user.role == UserRole.PARENT:
        parent = get_parent_profile(db=db, user_id=current_user.id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent profile not found"
            )

        accessible_student_ids = get_parent_student_ids(db=db, parent_id=parent.id)
        if student.id not in accessible_student_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access linked children"
            )

        return student
    
    # Default: deny
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


async def check_voice_analysis_ownership(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> VoiceAnalysis:
    """
    Check if current user has access to a specific voice analysis
    
    Security: CRITICAL ownership check
    - Students: Can only access their own analyses
    - Counselors: Can access assigned students' analyses
    - Admins: Can access all analyses
    
    Args:
        analysis_id: Voice analysis ID
        current_user: Current authenticated user
        db: Database session
    
    Raises:
        HTTPException 403: If access denied
        HTTPException 404: If analysis not found or access denied
    
    Returns:
        VoiceAnalysis: Voice analysis record with ownership verified
    """
    # Students: Filter by ownership
    if current_user.role == UserRole.STUDENT:
        analysis = db.query(VoiceAnalysis).join(Student).filter(
            VoiceAnalysis.id == analysis_id,
            Student.user_id == current_user.id  # CRITICAL: Ownership check
        ).first()
        
        if not analysis:
            # Don't reveal if not found or access denied (security)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice analysis not found or access denied"
            )
        
        return analysis
    
    # Admin: Access all
    if current_user.role == UserRole.ADMIN:
        analysis = db.query(VoiceAnalysis).filter(
            VoiceAnalysis.id == analysis_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice analysis not found"
            )
        
        return analysis
    
    # Counselor: Access assigned students' analyses
    if current_user.role == UserRole.COUNSELOR:
        # TODO: Implement assignment check
        # For now, allow access to all
        analysis = db.query(VoiceAnalysis).filter(
            VoiceAnalysis.id == analysis_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice analysis not found"
            )
        
        return analysis
    
    # Default: deny
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


def get_pagination_params(
    page: int = 1,
    page_size: int = 10
) -> dict:
    """
    Validate and return pagination parameters
    
    Args:
        page: Page number (starting from 1)
        page_size: Items per page (1-100)
    
    Returns:
        dict: {skip, limit, page, page_size}
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )
    
    skip = (page - 1) * page_size
    
    return {
        "skip": skip,
        "limit": page_size,
        "page": page,
        "page_size": page_size
    }
