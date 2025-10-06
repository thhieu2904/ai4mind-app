"""
Counselor Chat models - Direct messaging between students and counselors
Real-time conversations with human counselors (not AI)
"""
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import Base


class CounselorConversation(Base):
    """
    Conversation thread between a student and a counselor
    Each student-counselor pair has exactly one conversation (unique constraint)
    """
    __tablename__ = "counselor_conversations"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conversation status: 'active', 'closed', 'archived'
    status = Column(String(50), nullable=False, default="active", index=True)
    
    # Timestamps
    last_message_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    student = relationship("Student", foreign_keys=[student_id])
    counselor = relationship("Counselor", foreign_keys=[counselor_id])
    messages = relationship(
        "CounselorMessage", 
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="CounselorMessage.created_at"
    )

    def __repr__(self):
        return f"<CounselorConversation(id={self.id}, student={self.student_id}, counselor={self.counselor_id}, status={self.status})>"


class CounselorMessage(Base):
    """
    Individual message in counselor conversation
    sender_type can be 'student' or 'counselor'
    """
    __tablename__ = "counselor_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    conversation_id = Column(BigInteger, ForeignKey("counselor_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Sender: 'student' or 'counselor'
    sender_type = Column(String(20), nullable=False, index=True)
    
    # Message content
    content = Column(Text, nullable=False)
    
    # Read status
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Relationships
    conversation = relationship("CounselorConversation", back_populates="messages")

    def __repr__(self):
        return f"<CounselorMessage(id={self.id}, conversation={self.conversation_id}, sender={self.sender_type}, read={self.is_read})>"
