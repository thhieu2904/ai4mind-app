"""
Conversation and Message models - AI chatbot interactions
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import Base


class Conversation(Base):
    """
    Conversation session between student and AI chatbot
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Conversation metadata
    title = Column(String(255), nullable=True)  # Auto-generated or user-defined
    is_active = Column(Boolean, default=True)  # Active conversation or archived
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("Student", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

    def __repr__(self):
        return f"<Conversation(id={self.id}, student_id={self.student_id})>"


class Message(Base):
    """
    Individual messages within a conversation
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Voice analysis reference (if message came from voice input)
    voice_analysis_id = Column(Integer, ForeignKey("voice_analyses.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    voice_analysis = relationship("VoiceAnalysis", back_populates="message")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"
