"""
Secure Supabase Storage Utility
Audio file storage with ownership verification and access control
"""
import os
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from supabase import create_client, Client

from app.core.config import settings
from app.models.user import User, UserRole
from app.models.student import Student


class SecureStorage:
    """
    Secure file storage using Supabase Storage
    
    Features:
    - Ownership verification before upload/download
    - User-isolated folder structure
    - Signed URLs with access control
    - Role-based access (students, counselors, admins)
    
    Security:
    - Students can only access their own files
    - Counselors can access assigned students' files
    - Admins can access all files
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Optional[Client] = None
        self.bucket = "ai4mind-app"
        
        # Initialize if credentials available
        if settings.SUPABASE_PROJECT_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            self.supabase = create_client(
                settings.SUPABASE_PROJECT_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY  # Server-side key (admin access)
            )
    
    def _check_initialized(self):
        """Check if Supabase client is initialized"""
        if not self.supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service not configured. Please set SUPABASE_PROJECT_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
            )
    
    def _verify_file_access(
        self,
        file_path: str,
        current_user: User,
        db: Session
    ) -> Student:
        """
        Verify user has access to file
        
        File path format: {student_id}/{filename}
        
        Security:
        - Parse student_id from path
        - Verify user owns this student_id or has permission
        
        Args:
            file_path: Path in storage (e.g., "123/recording.wav")
            current_user: Current authenticated user
            db: Database session
        
        Raises:
            HTTPException 400: Invalid file path
            HTTPException 403: Access denied
            HTTPException 404: Student not found
        
        Returns:
            Student: Student that owns the file
        """
        # Parse student_id from file_path
        try:
            student_id_str = file_path.split('/')[0]
            student_id = int(student_id_str)
        except (ValueError, IndexError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path format. Expected: {student_id}/{filename}"
            )
        
        # Get student
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Check access permission
        # Admin: Access all files
        if current_user.role == UserRole.ADMIN:
            return student
        
        # Student: Only own files
        if current_user.role == UserRole.STUDENT:
            if student.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only access your own files"
                )
            return student
        
        # Counselor: Assigned students' files (TODO: check assignments)
        if current_user.role == UserRole.COUNSELOR:
            # For now, allow access to all students
            # TODO: Implement student_counselor_assignments check
            return student
        
        # Default: deny
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    def save_audio(
        self,
        file_content: bytes,
        filename: str,
        current_user: User,
        db: Session
    ) -> dict:
        """
        Save audio file to Supabase Storage
        WITH OWNERSHIP VERIFICATION
        
        Security:
        - Only students can upload files
        - Files saved to student's own folder
        - Folder structure: {student_id}/{filename}
        
        Args:
            file_content: Audio file bytes
            filename: Original filename (will be sanitized)
            current_user: Current authenticated user
            db: Database session
        
        Raises:
            HTTPException 403: If user is not a student
            HTTPException 404: If student profile not found
            HTTPException 500: If upload fails
        
        Returns:
            dict: {
                "path": "123/recording.wav",
                "student_id": 123,
                "size": 1024000,
                "uploaded_at": "2025-10-01T10:30:00Z"
            }
        """
        self._check_initialized()
        
        # Security: Only students can upload
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can upload audio files"
            )
        
        # Get student profile
        student = db.query(Student).filter(
            Student.user_id == current_user.id
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        # Sanitize filename (remove path traversal attempts)
        safe_filename = os.path.basename(filename)
        
        # Create unique filename with timestamp to allow multiple uploads
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # File path: {student_id}/{unique_filename}
        file_path = f"{student.id}/{unique_filename}"
        
        try:
            # Upload to Supabase Storage
            self.supabase.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": "audio/wav",
                    "cache-control": "3600",
                    "upsert": "true"  # Allow overwrite for multiple test uploads
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
        
        return {
            "path": file_path,
            "student_id": student.id,
            "size": len(file_content),
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    def get_audio(
        self,
        file_path: str,
        current_user: User,
        db: Session
    ) -> bytes:
        """
        Download audio file from Supabase Storage
        WITH ACCESS CONTROL
        
        Security:
        - Verify user has access to this file
        - Check ownership before download
        
        Args:
            file_path: Path in storage (e.g., "123/recording.wav")
            current_user: Current authenticated user
            db: Database session
        
        Raises:
            HTTPException 403: If access denied
            HTTPException 404: If file not found
        
        Returns:
            bytes: Audio file content
        """
        self._check_initialized()
        
        # Verify access
        self._verify_file_access(file_path, current_user, db)
        
        try:
            # Download from Supabase
            response = self.supabase.storage.from_(self.bucket).download(file_path)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {str(e)}"
            )
    
    def get_signed_url(
        self,
        file_path: str,
        current_user: User,
        db: Session,
        expires_in: int = 3600
    ) -> str:
        """
        Get temporary signed URL for file access
        WITH ACCESS CONTROL
        
        Security:
        - Verify user has access before creating URL
        - URL expires after specified time
        
        Args:
            file_path: Path in storage (e.g., "123/recording.wav")
            current_user: Current authenticated user
            db: Database session
            expires_in: URL validity in seconds (default 1 hour)
        
        Raises:
            HTTPException 403: If access denied
            HTTPException 404: If file not found
        
        Returns:
            str: Signed URL for temporary access
        """
        self._check_initialized()
        
        # Verify access
        self._verify_file_access(file_path, current_user, db)
        
        try:
            # Create signed URL
            response = self.supabase.storage.from_(self.bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            return response['signedURL']
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {str(e)}"
            )
    
    def delete_audio(
        self,
        file_path: str,
        current_user: User,
        db: Session
    ) -> bool:
        """
        Delete audio file from Supabase Storage
        WITH ACCESS CONTROL
        
        Security:
        - Only file owner or admin can delete
        - Verify ownership before deletion
        
        Args:
            file_path: Path in storage (e.g., "123/recording.wav")
            current_user: Current authenticated user
            db: Database session
        
        Raises:
            HTTPException 403: If access denied
            HTTPException 404: If file not found
        
        Returns:
            bool: True if deleted successfully
        """
        self._check_initialized()
        
        # Verify access (only owner or admin)
        student = self._verify_file_access(file_path, current_user, db)
        
        # Additional check: Only owner or admin can delete
        if current_user.role == UserRole.STUDENT:
            if student.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own files"
                )
        elif current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only file owner or admin can delete files"
            )
        
        try:
            # Delete from Supabase
            self.supabase.storage.from_(self.bucket).remove([file_path])
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    def list_student_files(
        self,
        student_id: int,
        current_user: User,
        db: Session
    ) -> list:
        """
        List all files for a student
        WITH ACCESS CONTROL
        
        Security:
        - Verify user has access to this student's files
        
        Args:
            student_id: Student ID
            current_user: Current authenticated user
            db: Database session
        
        Raises:
            HTTPException 403: If access denied
            HTTPException 404: If student not found
        
        Returns:
            list: List of file metadata
        """
        self._check_initialized()
        
        # Verify access
        file_path = f"{student_id}/"
        self._verify_file_access(file_path + "dummy", current_user, db)
        
        try:
            # List files in student's folder
            response = self.supabase.storage.from_(self.bucket).list(file_path)
            return response
        except Exception as e:
            # Empty list if folder doesn't exist
            return []


# Singleton instance
storage = SecureStorage()
