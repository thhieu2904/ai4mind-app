"""
Voice Analysis model - Results from voice-analysis service
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import Base


class VoiceAnalysis(Base):
    """
    Voice analysis results from voice-analysis microservice
    Stores transcription and emotion detection data
    """
    __tablename__ = "voice_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Audio file info
    audio_file_path = Column(String(500), nullable=False)  # Path to stored audio file
    audio_duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Transcription (from Whisper)
    transcription = Column(Text, nullable=False)
    transcription_language = Column(String(10), nullable=True)  # e.g., 'vi', 'en'
    transcription_confidence = Column(Float, nullable=True)
    
    # Emotion detection (future feature)
    detected_emotions = Column(JSON, nullable=True)  # {"happy": 0.2, "sad": 0.5, "angry": 0.1}
    dominant_emotion = Column(String(50), nullable=True)
    emotion_confidence = Column(Float, nullable=True)
    
    # Analysis metadata
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Error handling
    has_error = Column(Integer, default=0)  # 0: success, 1: has error
    error_message = Column(Text, nullable=True)

    # Relationships
    message = relationship("Message", back_populates="voice_analysis", uselist=False)

    def __repr__(self):
        return f"<VoiceAnalysis(id={self.id}, student_id={self.student_id})>"
