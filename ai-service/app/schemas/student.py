"""
Student schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator, computed_field
from typing import Optional
from datetime import date
from enum import Enum


class GenderEnum(str, Enum):
    """Gender options for voice analysis normalization"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class EducationLevelEnum(str, Enum):
    """Education level options"""
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    OTHER = "other"


class StudentBase(BaseModel):
    """Base student schema with common fields"""
    student_code: Optional[str] = Field(None, max_length=20, description="Student ID code")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    address: Optional[str] = Field(None, description="Address")
    gender: Optional[GenderEnum] = Field(GenderEnum.PREFER_NOT_TO_SAY, description="Gender for voice analysis")
    
    # Academic info
    university: Optional[str] = Field(None, max_length=255, description="University/School name")
    major: Optional[str] = Field(None, max_length=255, description="Major/Field of study")
    education_level: Optional[EducationLevelEnum] = Field(None, description="Education level (high_school, undergraduate, graduate, other)")
    grade: Optional[str] = Field(None, max_length=50, description="Grade/Year (e.g., '10', '11', '12', '1', '2', '3', '4', '5')")
    
    # Emergency contact - Foreign key to parents table
    emergency_contact_parent_id: Optional[int] = Field(None, description="Parent ID for emergency contact")


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
    # User basic info
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    
    # Student info
    student_code: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    gender: Optional[GenderEnum] = None
    university: Optional[str] = Field(None, max_length=255)
    major: Optional[str] = Field(None, max_length=255)
    education_level: Optional[EducationLevelEnum] = None
    grade: Optional[str] = Field(None, max_length=50)
    
    # Emergency contact
    emergency_contact_parent_id: Optional[int] = Field(None, description="Parent ID for emergency contact")
    parent_email: Optional[str] = Field(None, description="Parent email for emergency contact")
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("Họ và tên phải có ít nhất 2 ký tự")
        return v.strip() if v else v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None and v.strip():
            # Basic phone validation (Vietnamese format)
            import re
            phone = v.strip()
            if not re.match(r'^[0-9+\-\(\)\s]{8,15}$', phone):
                raise ValueError("Số điện thoại không hợp lệ")
            return phone
        return None if not v or not v.strip() else v
    
    @validator('parent_email')
    def validate_parent_email(cls, v):
        if v is not None and v.strip():
            # Email validation
            import re
            email = v.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValueError("Email phụ huynh không hợp lệ")
            return email
        return None if not v or not v.strip() else v


class StudentResponse(StudentBase):
    """Schema for student response with user info"""
    id: int
    user_id: int
    
    # User info (from users table)
    email: Optional[str] = None
    full_name: Optional[str] = None
    
    # Timestamps
    created_at: Optional[str] = None  # From users.created_at
    
    # Computed field
    parent_email: Optional[str] = None  # Computed from emergency_contact_parent
    
    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1
    
    @staticmethod
    def from_orm_with_parent(student) -> 'StudentResponse':
        """Create response with parent email and user info populated"""
        data = StudentResponse.model_validate(student)
        
        # Populate user info from relationship
        if student.user:
            data.email = student.user.email
            data.full_name = student.user.full_name
            # Convert datetime to ISO string
            if student.user.created_at:
                data.created_at = student.user.created_at.isoformat()
        
        # Populate parent_email from relationship
        if student.emergency_contact_parent and student.emergency_contact_parent.user:
            data.parent_email = student.emergency_contact_parent.user.email
            
        return data


class StudentPublicProfile(BaseModel):
    """Public student profile (limited fields)"""
    id: int
    student_code: str
    university: Optional[str]
    major: Optional[str]
    education_level: Optional[str]
    grade: Optional[str]
    
    class Config:
        from_attributes = True
