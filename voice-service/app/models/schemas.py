"""
Pydantic models for Voice Analysis API
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any
from datetime import datetime


class VoicePrompt(BaseModel):
    """Vietnamese voice recording prompt"""
    id: int
    text: str
    duration_estimate: int = Field(..., description="Estimated duration in seconds")
    category: str = Field(..., description="Prompt category (daily/emotion/future)")


class AudioFeatures(BaseModel):
    """Raw audio features extracted from file"""
    pitch_mean: float
    pitch_std: float
    pitch_min: float
    pitch_max: float
    energy_mean: float
    energy_std: float
    speech_rate: float
    pause_count: int
    pause_duration: float
    voice_stability: float
    duration: float


class NormalizedFeatures(BaseModel):
    """Gender-normalized audio features"""
    pitch_z_score: float
    pitch_deviation: float
    pitch_variability: float
    energy_relative: float
    speech_rate: float
    pause_ratio: float
    voice_stability: float
    severity: str  # normal, mild, moderate, severe


class EmotionScore(BaseModel):
    """Individual emotion score"""
    emotion: str
    confidence: float
    intensity: str
    contributing_factors: List[str]


class EmotionResult(BaseModel):
    """Emotion classification result"""
    primary_emotion: str
    intensity: str
    confidence: float
    emotion_scores: List[EmotionScore]
    summary: str
    contributing_factors: List[str]


class PsychologicalMarkers(BaseModel):
    """Text-based psychological markers"""
    self_reference: Dict[str, Any]
    uncertainty: Dict[str, Any]
    negation: Dict[str, Any]
    intensity: Dict[str, Any]


class TextAnalysisResult(BaseModel):
    """Text analysis result"""
    sentiment: float
    emotion_keywords: Dict[str, Dict]
    psychological_markers: PsychologicalMarkers
    text_stats: Dict[str, Any]
    dominant_emotion: str
    summary: str


class TranscriptResult(BaseModel):
    """Speech-to-text result"""
    transcript: str
    language: str
    duration: float
    confidence: float
    word_count: int


class VoiceAnalysisResponse(BaseModel):
    """Complete voice analysis response"""
    analysis_id: str
    user_id: int
    timestamp: datetime
    
    # Audio processing
    audio_features: AudioFeatures
    normalized_features: NormalizedFeatures
    
    # Speech-to-text
    transcript: TranscriptResult
    
    # Emotion detection
    emotion_result: EmotionResult
    
    # Text analysis
    text_analysis: TextAnalysisResult
    
    # Metadata
    gender: str
    audio_duration: float
    processing_time: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "voice_123456",
                "user_id": 1,
                "timestamp": "2025-10-01T10:30:00",
                "audio_features": {
                    "pitch_mean": 220.5,
                    "pitch_std": 45.2,
                    "energy_mean": 0.15,
                    "speech_rate": 3.8,
                    "pause_count": 5,
                    "duration": 15.5
                },
                "emotion_result": {
                    "primary_emotion": "anxiety",
                    "intensity": "moderate",
                    "confidence": 0.78
                },
                "transcript": {
                    "transcript": "Tôi đang cảm thấy lo lắng về công việc",
                    "confidence": 0.92,
                    "word_count": 7
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
