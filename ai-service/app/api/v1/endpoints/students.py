"""
Students API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import EmailStr

from app.core.database import get_db
from app.api.dependencies import get_current_user_student, get_current_active_user, check_student_access
from app.models.student import Student
from app.models.parent import Parent
from app.models.user import User, UserRole
from app.schemas.student import StudentResponse, StudentUpdate
from app.schemas.auth import UserCreate

router = APIRouter()


@router.get("/me", response_model=StudentResponse)
def get_current_student_profile(
    current_student: Student = Depends(get_current_user_student),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated student's profile
    
    **Authentication**: Required (student role only)
    
    **Returns**: Student profile with all details including user info
    """
    # Refresh with eager loading of user and parent relationships
    student = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.emergency_contact_parent).joinedload(Parent.user)
    ).filter(Student.id == current_student.id).first()
    
    return StudentResponse.from_orm_with_parent(student)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get student profile by ID
    
    **Authentication**: Required (authenticated user)
    
    **Access Control**:
    - Students can only view their own profile
    - Counselors can view assigned students (TODO: implement assignment check)
    - Admins can view all students
    
    **Returns**: Student profile
    """
    # Check access permission
    await check_student_access(student_id=student_id, current_user=current_user, db=db)
    
    student = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.emergency_contact_parent).joinedload(Parent.user)
    ).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    return StudentResponse.from_orm_with_parent(student)


@router.put("/me", response_model=StudentResponse)
def update_current_student_profile(
    student_data: StudentUpdate,
    current_student: Student = Depends(get_current_user_student),
    db: Session = Depends(get_db)
):
    """
    Update current authenticated student's profile
    
    **Authentication**: Required (student role only)
    
    **Features**:
    - Update basic info (name, phone, address, academic info)
    - Update emergency contact by providing parent email
    - Auto-create parent account if email doesn't exist
    - Link student to existing parent if email exists
    
    **Note**: Cannot delete parent once set (for safety)
    
    **Returns**: Updated student profile
    """
    # Update basic fields
    update_data = student_data.model_dump(exclude_unset=True, exclude={'parent_email', 'full_name'})
    
    # Handle full_name update (update user table)
    if student_data.full_name:
        current_student.user.full_name = student_data.full_name
    
    # Handle parent email update (if provided in body)
    if student_data.parent_email:
        parent_email = student_data.parent_email.strip().lower()
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, parent_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email phụ huynh không hợp lệ"
            )
        
        # Check if student is trying to use their own email
        if parent_email == current_student.user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể sử dụng email của chính bạn làm email phụ huynh"
            )
        
        print(f"[DEBUG] Updating parent email to: {parent_email}")  # DEBUG
        
        # Check if parent with this email already exists
        parent_user = db.query(User).filter(
            User.email == parent_email,
            User.role == UserRole.PARENT
        ).first()
        
        if parent_user:
            # Parent exists, get parent record
            print(f"[DEBUG] Parent user found: {parent_user.id}")  # DEBUG
            parent = db.query(Parent).filter(Parent.user_id == parent_user.id).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Parent user exists but parent profile not found"
                )
            update_data['emergency_contact_parent_id'] = parent.id
        else:
            # Check if email already exists with different role (student, admin, etc.)
            existing_user = db.query(User).filter(User.email == parent_email).first()
            if existing_user:
                print(f"[DEBUG] Email exists with role: {existing_user.role}")  # DEBUG
                role_names = {
                    "student": "học sinh",
                    "parent": "phụ huynh",
                    "admin": "quản trị viên",
                    "counselor": "tư vấn viên"
                }
                role_vn = role_names.get(existing_user.role.value if hasattr(existing_user.role, 'value') else existing_user.role, existing_user.role)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {parent_email} đã được đăng ký với vai trò '{role_vn}'. Vui lòng sử dụng email khác cho phụ huynh."
                )
            
            # Create new parent account
            print(f"[DEBUG] Creating new parent account for: {parent_email}")  # DEBUG
            from app.core.security import get_password_hash
            
            # Generate temporary password (parent will reset via email)
            temp_password = "TempPass123!"  # TODO: Send email with reset link
            hashed_password = get_password_hash(temp_password)
            
            # Create user account for parent
            new_parent_user = User(
                email=parent_email,
                hashed_password=hashed_password,
                full_name="Phụ huynh",  # Temporary name, parent can update later
                role="parent",
                is_active=False,  # Inactive until parent verifies email
                is_verified=False
            )
            db.add(new_parent_user)
            db.flush()  # Get the user ID
            
            # Create parent profile
            new_parent = Parent(
                user_id=new_parent_user.id,
                phone_number=None  # Parent will update later
            )
            db.add(new_parent)
            db.flush()  # Get the parent ID
            
            print(f"[DEBUG] Created parent profile: {new_parent.id}")  # DEBUG
            update_data['emergency_contact_parent_id'] = new_parent.id
            
            # TODO: Send welcome email to parent with account activation link
            # send_parent_welcome_email(parent_email, temp_password)
    
    # Update student record
    print(f"[DEBUG] Updating student with data: {update_data}")  # DEBUG
    for field, value in update_data.items():
        setattr(current_student, field, value)
    
    try:
        db.commit()
        print(f"[DEBUG] Successfully committed changes")  # DEBUG
        # Refresh with user and parent relationships
        db.refresh(current_student)
        student = db.query(Student).options(
            joinedload(Student.user),
            joinedload(Student.emergency_contact_parent).joinedload(Parent.user)
        ).filter(Student.id == current_student.id).first()
    except Exception as e:
        db.rollback()
        print(f"[DEBUG] Error during commit/refresh: {e}")  # DEBUG
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student profile: {str(e)}"
        )
    
    print(f"[DEBUG] Returning student response")  # DEBUG
    return StudentResponse.from_orm_with_parent(student)

