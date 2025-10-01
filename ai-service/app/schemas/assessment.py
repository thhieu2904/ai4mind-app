"""
Assessment Pydantic schemas for GAD-7 questionnaire
"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator


class AssessmentCreate(BaseModel):
    """Schema for creating new GAD-7 assessment"""
    answers: List[int] = Field(
        ...,
        min_length=7,
        max_length=7,
        description="Array of 7 answers, each value must be 0-3"
    )
    functional_impairment: Optional[int] = Field(
        None,
        ge=0,
        le=3,
        description="How difficult symptoms make daily functioning (0-3)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional notes from student about their situation"
    )
    
    @validator('answers')
    def validate_answers(cls, v):
        """Validate that all answers are between 0 and 3"""
        if len(v) != 7:
            raise ValueError('Must provide exactly 7 answers for GAD-7 questions')
        
        for i, answer in enumerate(v, 1):
            if not 0 <= answer <= 3:
                raise ValueError(f'Answer {i} must be between 0 and 3, got {answer}')
        
        return v
    
    @validator('functional_impairment')
    def validate_functional_impairment(cls, v):
        """Validate functional impairment score"""
        if v is not None and not 0 <= v <= 3:
            raise ValueError('Functional impairment must be between 0 and 3')
        return v


class AssessmentResponse(BaseModel):
    """Schema for assessment response"""
    id: int
    user_id: int
    answers: List[int]
    total_score: int
    severity_level: str  # minimal, mild, moderate, severe
    
    # Gemini analysis
    analysis: Optional[str] = None
    recommendations: Optional[List[str]] = None
    
    # Additional data
    functional_impairment: Optional[int] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentDetail(AssessmentResponse):
    """Extended assessment response with question details"""
    questions_with_answers: List[Dict] = []
    severity_info: Dict = {}
    
    class Config:
        from_attributes = True


class AssessmentStats(BaseModel):
    """Statistics for user's assessments"""
    total_assessments: int
    average_score: float
    latest_score: Optional[int] = None
    latest_severity: Optional[str] = None
    trend: Optional[str] = None  # improving, worsening, stable
    score_history: List[Dict] = []  # List of {date, score, severity}
    
    class Config:
        from_attributes = True


class AssessmentListResponse(BaseModel):
    """Paginated list of assessments"""
    items: List[AssessmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
