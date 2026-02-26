"""
Admin API Endpoints
User management (CRUD + reset password) for ADMIN role only
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.user import User, UserRole

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class UserListItem(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None
    role: str = Field(..., description="STUDENT, COUNSELOR, or ADMIN")
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    is_verified: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6)


# ============================================
# DEPENDENCY
# ============================================

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Only ADMIN role can access these endpoints"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================
# ENDPOINTS
# ============================================

@router.get("/users", response_model=List[UserListItem])
async def list_users(
    role: Optional[str] = Query(None, description="Filter by role: STUDENT, COUNSELOR, ADMIN"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with optional role filter and search.
    """
    query = db.query(User)

    if role:
        try:
            role_enum = UserRole(role.upper())
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Must be one of STUDENT, COUNSELOR, ADMIN, PARENT"
            )

    if search:
        like = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(like)) | (User.email.ilike(like))
        )

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserListItem, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user (counselor, student, or admin account).
    """
    # Check email uniqueness
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    try:
        role_enum = UserRole(request.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {request.role}"
        )

    new_user = User(
        email=request.email,
        full_name=request.full_name,
        phone=request.phone,
        role=role_enum,
        hashed_password=get_password_hash(request.password),
        is_active=True,
        is_verified=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/{user_id}", response_model=UserListItem)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get a single user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserListItem)
async def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user name, phone, or verified status."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if request.full_name is not None:
        user.full_name = request.full_name
    if request.phone is not None:
        user.phone = request.phone
    if request.is_verified is not None:
        user.is_verified = request.is_verified

    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/reset-password", status_code=status.HTTP_200_OK)
async def reset_user_password(
    user_id: int,
    request: ResetPasswordRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reset a user's password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password reset successfully"}


@router.put("/users/{user_id}/toggle-active", response_model=UserListItem)
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle user active/inactive status."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own active status"
        )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
