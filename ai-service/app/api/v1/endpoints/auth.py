"""
Authentication endpoints
Register, Login, Get Current User, Refresh Token
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user
)
from app.core.config import settings
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfileResponse,
    Token,
    RefreshToken
)
from app.models.user import User
from app.models.student import Student
from app.models.parent import Parent
from app.models.counselor import Counselor


router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user with role-specific profile
    
    - **email**: Valid email address (will be username)
    - **password**: Min 8 chars, must have uppercase, lowercase, number
    - **full_name**: User's full name
    - **role**: student, parent, counselor, or admin
    - Additional fields based on role
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        phone=user_data.phone,
        is_active=True
    )
    
    db.add(user)
    db.flush()  # Get user.id without committing
    
    # Create role-specific profile
    if user_data.role == "student":
        student = Student(
            user_id=user.id,
            student_code=user_data.student_code,
            university=user_data.university,
            major=user_data.major,
            year_of_study=user_data.year_of_study
        )
        db.add(student)
    
    elif user_data.role == "parent":
        parent = Parent(
            user_id=user.id
        )
        db.add(parent)
    
    elif user_data.role == "counselor":
        counselor = Counselor(
            user_id=user.id,
            license_number=user_data.license_number,
            specialization=user_data.specialization,
            years_of_experience=user_data.years_of_experience
        )
        db.add(counselor)
    
    # Commit all changes
    db.commit()
    db.refresh(user)
    
    # Generate JWT tokens
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login with email and password
    
    Returns JWT access token
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate JWT tokens
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible login endpoint
    For Swagger UI /docs authentication
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user information with role-specific profile
    
    Requires: Valid JWT token in Authorization header
    """
    # Get role-specific profile
    profile = None
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            profile = {
                "student_code": student.student_code,
                "university": student.university,
                "major": student.major,
                "year_of_study": student.year_of_study
            }
    
    elif current_user.role == "parent":
        parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()
        if parent:
            profile = {
                "id": parent.id,
                "occupation": parent.occupation,
                "relationship": parent.relationship
            }
    
    elif current_user.role == "counselor":
        counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
        if counselor:
            profile = {
                "license_number": counselor.license_number,
                "specialization": counselor.specialization,
                "years_of_experience": counselor.years_of_experience,
                "bio": counselor.bio
            }
    
    # Return user with profile
    user_dict = UserResponse.model_validate(current_user).model_dump()
    return UserProfileResponse(**user_dict, profile=profile)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    
    (Note: Refresh token implementation is simplified for MVP)
    """
    payload = verify_token(refresh_data.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.email == payload["email"]).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new access token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Logout current user
    
    Note: With JWT, logout is handled client-side by removing the token.
    This endpoint is here for completeness and can be extended with token blacklist.
    """
    return {"message": "Successfully logged out"}
