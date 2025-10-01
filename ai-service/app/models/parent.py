"""
Parent model - Parents of students
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models import Base


class Parent(Base):
    """
    Parent profile - can view their children's data with consent
    """
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal info
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    occupation = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="parent")
    consents = relationship("ParentConsent", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Parent(id={self.id}, user_id={self.user_id})>"


class ParentConsent(Base):
    """
    Parent consent to access student data
    Students must approve parents to view their mental health data
    """
    __tablename__ = "parent_consents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    
    # Consent status
    is_approved = Column(Integer, default=0)  # 0: pending, 1: approved, -1: rejected
    
    # Relationships
    student = relationship("Student", back_populates="parent_consents")
    parent = relationship("Parent", back_populates="consents")

    def __repr__(self):
        return f"<ParentConsent(student_id={self.student_id}, parent_id={self.parent_id}, approved={self.is_approved})>"
