"""
Dashboard schemas - Welcome card data
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DashboardWelcomeData(BaseModel):
    """
    Simplified dashboard welcome card data
    
    Fields:
    - user_name: Display name of the user
    - days_since_registration: Number of days since account creation
    - latest_emotion_severity: Latest assessment severity (minimal/mild/moderate/severe)
    - latest_emotion_text: Vietnamese translation of emotion
    - latest_emotion_date: When the latest assessment was taken
    - total_assessments: Total number of assessments completed
    - has_recent_assessment: Whether user has assessment in last 7 days
    """
    user_name: str = Field(..., description="User's full name")
    days_since_registration: int = Field(..., ge=0, description="Days since account creation")
    
    # Latest emotion data
    latest_emotion_severity: Optional[str] = Field(
        None, 
        description="Latest assessment severity level"
    )
    latest_emotion_text: Optional[str] = Field(
        None,
        description="Vietnamese emotion label (Tích cực/Bình thường/Lo âu/Căng thẳng)"
    )
    latest_emotion_date: Optional[datetime] = Field(
        None,
        description="Timestamp of latest assessment"
    )
    
    # Quick stats
    total_assessments: int = Field(0, ge=0, description="Total number of assessments")
    has_recent_assessment: bool = Field(
        False,
        description="Whether user has assessment within last 7 days"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_name": "Nguyễn Văn A",
                "days_since_registration": 15,
                "latest_emotion_severity": "minimal",
                "latest_emotion_text": "Tích cực",
                "latest_emotion_date": "2025-10-04T10:30:00Z",
                "total_assessments": 5,
                "has_recent_assessment": True
            }
        }
