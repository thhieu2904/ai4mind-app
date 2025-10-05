"""
Dashboard endpoints - Welcome card and summary data
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Any

from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.models.student import Student
from app.models.assessment import Assessment
from app.schemas.dashboard import DashboardWelcomeData

router = APIRouter()


# Emotion severity to Vietnamese text mapping
EMOTION_MAP = {
    "minimal": "Tích cực",
    "mild": "Bình thường",
    "moderate": "Lo âu",
    "severe": "Căng thẳng"
}


@router.get("/welcome", response_model=DashboardWelcomeData)
async def get_dashboard_welcome_data(
    current_user: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get simplified dashboard welcome card data
    
    Returns:
    - User name
    - Days since registration (from User.created_at)
    - Latest emotion (from most recent Assessment.severity_level)
    - Total assessments count
    - Whether user has recent assessment (within 7 days)
    
    Requires:
    - STUDENT role
    """
    
    # Get student profile
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # 1. Calculate days since registration
    days_since_registration = 0
    if current_user.created_at:
        delta = datetime.utcnow() - current_user.created_at.replace(tzinfo=None)
        days_since_registration = delta.days
    
    # 2. Get latest assessment (most recent by created_at)
    latest_assessment = db.query(Assessment).filter(
        Assessment.student_id == student.id
    ).order_by(desc(Assessment.created_at)).first()
    
    # 3. Extract emotion data from latest assessment
    latest_emotion_severity = None
    latest_emotion_text = None
    latest_emotion_date = None
    has_recent_assessment = False
    
    if latest_assessment:
        latest_emotion_severity = latest_assessment.severity_level
        latest_emotion_text = EMOTION_MAP.get(
            latest_assessment.severity_level,
            "Chưa xác định"
        )
        latest_emotion_date = latest_assessment.created_at
        
        # Check if assessment is within 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        has_recent_assessment = (
            latest_assessment.created_at.replace(tzinfo=None) >= seven_days_ago
        )
    
    # 4. Count total assessments
    total_assessments = db.query(Assessment).filter(
        Assessment.student_id == student.id
    ).count()
    
    return DashboardWelcomeData(
        user_name=current_user.full_name,
        days_since_registration=days_since_registration,
        latest_emotion_severity=latest_emotion_severity,
        latest_emotion_text=latest_emotion_text,
        latest_emotion_date=latest_emotion_date,
        total_assessments=total_assessments,
        has_recent_assessment=has_recent_assessment,
    )
