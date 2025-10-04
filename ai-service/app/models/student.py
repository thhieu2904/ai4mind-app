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
    university = Column(String(255), nullable=True)  # School/University name
    major = Column(String(255), nullable=True)
    education_level = Column(String(50), nullable=True)  # high_school, undergraduate, graduate, other
    grade = Column(String(50), nullable=True)  # Grade/Year: '10', '11', '12', '1'-'5', etc.
    
    # Emergency contact - Foreign key to parents table
    emergency_contact_parent_id = Column(Integer, ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student")
    emergency_contact_parent = relationship("Parent", foreign_keys=[emergency_contact_parent_id], backref="emergency_contacts")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="student", cascade="all, delete-orphan")
    parent_consents = relationship("ParentConsent", back_populates="student", cascade="all, delete-orphan")
    voice_analyses = relationship("VoiceAnalysis", back_populates="student", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, student_code={self.student_code})>"
