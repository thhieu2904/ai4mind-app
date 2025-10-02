"""
Authentication Pydantic schemas for request/response validation
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(..., pattern="^(student|parent|counselor|admin)$")
    
    # Additional fields for specific roles
    phone: Optional[str] = Field(None, max_length=20)
    
    # Student specific - IMPORTANT for GAD-7 assessment
    date_of_birth: Optional[str] = Field(None, description="Date of birth in YYYY-MM-DD format")
    gender: Optional[str] = Field(None, pattern="^(male|female|other|prefer_not_to_say)$")
    student_code: Optional[str] = Field(None, max_length=20)
    university: Optional[str] = Field(None, max_length=200)
    major: Optional[str] = Field(None, max_length=200)
    year_of_study: Optional[int] = Field(None, ge=1, le=7)
    address: Optional[str] = Field(None, max_length=500)
    
    # Counselor specific
    license_number: Optional[str] = Field(None, max_length=50)
    specialization: Optional[str] = Field(None, max_length=200)
    years_of_experience: Optional[int] = Field(None, ge=0)
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('student_code')
    def validate_student_code(cls, v, values):
        """Validate student code format if provided"""
        # Student code is now OPTIONAL - can be added later
        # Students can register without it and add it in their profile later
        if v and len(v.strip()) == 0:
            raise ValueError('Student code cannot be empty if provided')
        return v if v else None
    
    @validator('license_number')
    def validate_license_number(cls, v, values):
        """Validate license number is required for counselor role"""
        if values.get('role') == 'counselor' and not v:
            raise ValueError('License number is required for counselor role')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserProfileResponse(UserResponse):
    """Extended user response with role-specific profile"""
    profile: Optional[dict] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds
    user: UserResponse


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    email: str
    role: str
    user_id: Optional[int] = None


class RefreshToken(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
