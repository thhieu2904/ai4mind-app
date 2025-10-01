"""
Assessment model - GAD-7 assessments
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import Base


class Assessment(Base):
    """
    GAD-7 Assessment records
    Stores mental health assessments completed by students
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Assessment data
    answers = Column(JSON, nullable=False)  # List of 7 answers (0-3 each)
    total_score = Column(Integer, nullable=False)  # Sum of all answers (0-21)
    severity_level = Column(String(50), nullable=False)  # minimal, mild, moderate, severe
    functional_impairment = Column(Integer, nullable=True)  # How difficult symptoms make daily functioning (0-3)
    
    # AI Analysis
    analysis = Column(Text, nullable=True)  # AI-generated analysis (Vietnamese)
    recommendations = Column(JSON, nullable=True)  # List of AI-generated recommendations
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)  # Optional student notes

    # Relationships
    student = relationship("Student", back_populates="assessments")
    voice_analyses = relationship("VoiceAnalysis", back_populates="assessment")

    def __repr__(self):
        return f"<Assessment(id={self.id}, student_id={self.student_id}, score={self.total_score})>"

    def get_severity_level(self) -> str:
        """
        Determine severity level based on GAD-7 score:
        - 0-4: Minimal anxiety
        - 5-9: Mild anxiety
        - 10-14: Moderate anxiety
        - 15-21: Severe anxiety
        """
        if self.total_score <= 4:
            return "minimal"
        elif self.total_score <= 9:
            return "mild"
        elif self.total_score <= 14:
            return "moderate"
        else:
            return "severe"
