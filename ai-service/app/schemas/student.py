"""
Student schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from enum import Enum


class GenderEnum(str, Enum):
    """Gender options for voice analysis normalization"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class StudentBase(BaseModel):
    """Base student schema with common fields"""
    student_code: Optional[str] = Field(None, max_length=20, description="Student ID code")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    address: Optional[str] = Field(None, description="Address")
    gender: Optional[GenderEnum] = Field(GenderEnum.PREFER_NOT_TO_SAY, description="Gender for voice analysis")
    
    # Academic info
    university: Optional[str] = Field(None, max_length=255, description="University name")
    major: Optional[str] = Field(None, max_length=255, description="Major/Field of study")
    year_of_study: Optional[int] = Field(None, ge=1, le=6, description="Year of study (1-6)")
    
    # Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)


class StudentCreate(StudentBase):
    """Schema for creating a new student profile"""
    student_code: str = Field(..., max_length=20, description="Required student code")
    
    @validator('student_code')
    def validate_student_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Student code cannot be empty")
        return v.strip()


class StudentUpdate(BaseModel):
    """Schema for updating student profile - all fields optional"""
    student_code: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    gender: Optional[GenderEnum] = None
    university: Optional[str] = Field(None, max_length=255)
    major: Optional[str] = Field(None, max_length=255)
    year_of_study: Optional[int] = Field(None, ge=1, le=6)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1


class StudentPublicProfile(BaseModel):
    """Public student profile (limited fields)"""
    id: int
    student_code: str
    university: Optional[str]
    major: Optional[str]
    year_of_study: Optional[int]
    
    class Config:
        from_attributes = True
