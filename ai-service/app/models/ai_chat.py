"""
AI Chat models - Conversations and Messages between students and AI assistant
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import Base


class AIConversation(Base):
    """
    AI chat conversation between student and AI assistant
    Each student can have multiple conversations, but only one active at a time
    """
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    latest_assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True)
    
    # Conversation metadata
    title = Column(String(255), default="Chat với AI", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    student = relationship("Student", back_populates="ai_conversations")
    latest_assessment = relationship("Assessment", foreign_keys=[latest_assessment_id])
    messages = relationship(
        "AIMessage", 
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AIMessage.created_at"
    )

    def __repr__(self):
        return f"<AIConversation(id={self.id}, student_id={self.student_id}, active={self.is_active})>"


class AIMessage(Base):
    """
    Individual message within an AI conversation
    Can be from user (student) or assistant (AI)
    """
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Optional: Link to assessment being discussed
    related_assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")
    related_assessment = relationship("Assessment", foreign_keys=[related_assessment_id])

    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<AIMessage(id={self.id}, role={self.role}, content='{preview}')>"
