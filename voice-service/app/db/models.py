"""
Database models for Voice Service
Re-uses models from ai-service database
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    PARENT = "parent"
    COUNSELOR = "counselor"
    ADMIN = "admin"


class User(Base):
    """User model (read-only from ai-service)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean)
    
    # Relationships
    student = relationship("Student", back_populates="user", uselist=False)


class Student(Base):
    """Student model (read-only from ai-service)"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Personal info
    student_code = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(20))  # male, female, other, prefer_not_to_say
    
    # Relationships
    user = relationship("User", back_populates="student")
