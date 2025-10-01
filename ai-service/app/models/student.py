"""
Student model - Extended profile for students
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models import Base


class Student(Base):
    """
    Student profile with extended information
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal info
    student_code = Column(String(20), unique=True, index=True)  # Mã sinh viên
    date_of_birth = Column(Date, nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    gender = Column(String(20), nullable=True, default='prefer_not_to_say')  # male, female, other, prefer_not_to_say
    
    # Academic info
    university = Column(String(255), nullable=True)
    major = Column(String(255), nullable=True)
    year_of_study = Column(Integer, nullable=True)  # Năm học (1, 2, 3, 4)
    
    # Emergency contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="student", cascade="all, delete-orphan")
    parent_consents = relationship("ParentConsent", back_populates="student", cascade="all, delete-orphan")
    voice_analyses = relationship("VoiceAnalysis", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, student_code={self.student_code})>"
