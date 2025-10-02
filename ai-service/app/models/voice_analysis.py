"""
Voice Analysis model - Comprehensive voice recording analysis results
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import Base


class VoiceAnalysis(Base):
    """
    Voice analysis results from voice-analysis microservice
    Stores audio features, transcription, emotion detection, and text analysis
    """
    __tablename__ = "voice_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(
        Integer, 
        ForeignKey("assessments.id", ondelete="CASCADE"), 
        nullable=False,  # Changed: Every voice analysis must belong to an assessment
        index=True,
        comment="Required: Links voice analysis to its parent assessment"
    )
    
    # Audio file info
    audio_file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    audio_duration = Column(Float, nullable=True)  # Duration in seconds
    audio_format = Column(String(10), nullable=True)  # wav, mp3, m4a
    
    # Prompt used for recording
    prompt_id = Column(Integer, nullable=True)
    prompt_text = Column(Text, nullable=True)
    
    # Transcription (from Whisper)
    transcription = Column(Text, nullable=True)
    transcription_language = Column(String(10), default='vi')
    word_count = Column(Integer, nullable=True)
    transcription_confidence = Column(Float, nullable=True)
    
    # Audio features (JSONB)
    # {pitch_mean, pitch_std, energy_mean, speech_rate, pause_count, voice_stability, mfccs}
    audio_features = Column(JSON, nullable=True)
    
    # Emotion detection
    detected_emotions = Column(JSON, nullable=True)  # {anxiety: 0.75, sadness: 0.60, anger: 0.10, neutral: 0.20}
    dominant_emotion = Column(String(50), nullable=True, index=True)
    emotion_confidence = Column(Float, nullable=True)
    
    # Text/Semantic analysis
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    keywords = Column(JSON, nullable=True)  # [{word, count, weight}, ...]
    psychological_markers = Column(JSON, nullable=True)  # {negative_words, positive_words, self_reference, uncertainty}
    
    # Gender-normalized features
    gender_used = Column(String(20), nullable=True)  # male, female, other, prefer_not_to_say
    normalized_features = Column(JSON, nullable=True)  # {pitch_z_score, pitch_deviation, pitch_variability, energy_relative}
    
    # 🆕 Comprehensive Analysis from Gemini (cross-validation of GAD-7 + Voice)
    comprehensive_analysis = Column(Text, nullable=True)  # Gemini's comprehensive analysis text
    comprehensive_recommendations = Column(JSON, nullable=True)  # Array of recommendation strings
    
    # Processing metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_status = Column(String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    
    # Error handling
    has_error = Column(Integer, default=0)  # 0: success, 1: has error
    error_message = Column(Text, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="voice_analyses")
    assessment = relationship("Assessment", back_populates="voice_analyses")
    message = relationship("Message", back_populates="voice_analysis", uselist=False)

    def __repr__(self):
        return f"<VoiceAnalysis(id={self.id}, student_id={self.student_id}, status={self.processing_status})>"
