"""
Voice Analysis schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Voice analysis processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioFeatures(BaseModel):
    """Audio feature extraction results"""
    pitch_mean: float = Field(..., description="Average pitch (fundamental frequency) in Hz")
    pitch_std: float = Field(..., description="Standard deviation of pitch")
    pitch_min: Optional[float] = Field(None, description="Minimum pitch in Hz")
    pitch_max: Optional[float] = Field(None, description="Maximum pitch in Hz")
    energy_mean: float = Field(..., description="Average energy/intensity (0-1)")
    energy_max: Optional[float] = Field(None, description="Maximum energy")
    speech_rate: str = Field(..., description="Speech rate: slow/normal/fast")
    pause_count: int = Field(..., description="Number of pauses detected")
    voice_stability: float = Field(..., ge=0, le=1, description="Voice stability score (0-1)")
    zero_crossing_rate: Optional[float] = Field(None, description="Zero-crossing rate")
    # MFCCs can be stored as list
    mfccs: Optional[List[float]] = Field(None, description="Mel-frequency cepstral coefficients")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pitch_mean": 210.5,
                "pitch_std": 45.2,
                "pitch_min": 150.0,
                "pitch_max": 300.0,
                "energy_mean": 0.65,
                "energy_max": 0.95,
                "speech_rate": "fast",
                "pause_count": 12,
                "voice_stability": 0.45,
                "zero_crossing_rate": 0.082
            }
        }


class EmotionScores(BaseModel):
    """Emotion detection scores"""
    anxiety: float = Field(..., ge=0, le=1, description="Anxiety level (0-1)")
    sadness: float = Field(..., ge=0, le=1, description="Sadness level (0-1)")
    anger: float = Field(..., ge=0, le=1, description="Anger level (0-1)")
    neutral: float = Field(..., ge=0, le=1, description="Neutral/calm level (0-1)")
    joy: Optional[float] = Field(None, ge=0, le=1, description="Joy/happiness level (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "anxiety": 0.75,
                "sadness": 0.60,
                "anger": 0.10,
                "neutral": 0.20,
                "joy": 0.05
            }
        }


class Keyword(BaseModel):
    """Detected keyword with frequency and weight"""
    word: str = Field(..., description="The keyword")
    count: int = Field(..., ge=0, description="Occurrence count")
    weight: float = Field(..., ge=0, le=1, description="Importance weight (0-1)")


class PsychologicalMarkers(BaseModel):
    """Psychological markers from text analysis"""
    negative_words: int = Field(..., ge=0, description="Count of negative words")
    positive_words: int = Field(..., ge=0, description="Count of positive words")
    self_reference: int = Field(..., ge=0, description="Self-reference count (I, me, my)")
    uncertainty: int = Field(..., ge=0, description="Uncertainty indicators (maybe, perhaps)")
    anxiety_keywords: Optional[int] = Field(None, ge=0, description="Anxiety-related keywords")
    
    class Config:
        json_schema_extra = {
            "example": {
                "negative_words": 15,
                "positive_words": 3,
                "self_reference": 8,
                "uncertainty": 6,
                "anxiety_keywords": 5
            }
        }


class TextAnalysis(BaseModel):
    """Text/semantic analysis results"""
    sentiment: float = Field(..., ge=-1, le=1, description="Sentiment polarity (-1 to 1)")
    subjectivity: Optional[float] = Field(None, ge=0, le=1, description="Subjectivity score (0-1)")
    keywords: List[Keyword] = Field(default_factory=list, description="Detected keywords")
    psychological_markers: PsychologicalMarkers


class NormalizedFeatures(BaseModel):
    """Gender-normalized audio features"""
    pitch_z_score: float = Field(..., description="Pitch Z-score (normalized)")
    pitch_deviation: float = Field(..., ge=0, description="Absolute deviation from gender baseline")
    pitch_variability: float = Field(..., ge=0, description="Coefficient of variation for pitch")
    energy_relative: float = Field(..., ge=0, le=1, description="Relative energy (0-1)")
    gender_baseline: str = Field(..., description="Gender used for normalization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pitch_z_score": 1.5,
                "pitch_deviation": 1.5,
                "pitch_variability": 0.25,
                "energy_relative": 0.68,
                "gender_baseline": "female"
            }
        }


# Request schemas
class VoiceAnalysisCreate(BaseModel):
    """Schema for creating voice analysis (multipart form data)"""
    student_id: int = Field(..., description="Student ID")
    assessment_id: Optional[int] = Field(None, description="Optional link to GAD-7 assessment")
    prompt_id: Optional[int] = Field(None, description="Prompt ID used")
    prompt_text: Optional[str] = Field(None, description="Custom prompt text")
    # audio_file handled separately as UploadFile in FastAPI


# Response schemas
class VoiceAnalysisResponse(BaseModel):
    """Comprehensive voice analysis response"""
    id: int
    student_id: int
    assessment_id: Optional[int] = None
    
    # File info
    audio_file_path: str
    file_size_bytes: Optional[int] = None
    audio_duration: Optional[float] = None
    audio_format: Optional[str] = None
    
    # Prompt
    prompt_id: Optional[int] = None
    prompt_text: Optional[str] = None
    
    # Transcription
    transcription: Optional[str] = None
    transcription_language: str = "vi"
    word_count: Optional[int] = None
    transcription_confidence: Optional[float] = None
    
    # Analysis results
    audio_features: Optional[Dict[str, Any]] = None  # Can also use AudioFeatures
    detected_emotions: Optional[Dict[str, float]] = None  # Can also use EmotionScores
    dominant_emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    
    # Text analysis
    sentiment_score: Optional[float] = None
    keywords: Optional[List[Dict[str, Any]]] = None
    psychological_markers: Optional[Dict[str, int]] = None
    
    # Normalized features
    gender_used: Optional[str] = None
    normalized_features: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime
    processed_at: Optional[datetime] = None
    processing_status: ProcessingStatus
    processing_time: Optional[float] = None
    has_error: int = 0
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class VoiceAnalysisDetail(VoiceAnalysisResponse):
    """Detailed voice analysis with structured objects"""
    audio_features_structured: Optional[AudioFeatures] = None
    emotion_scores_structured: Optional[EmotionScores] = None
    text_analysis_structured: Optional[TextAnalysis] = None
    normalized_features_structured: Optional[NormalizedFeatures] = None


class VoiceAnalysisSummary(BaseModel):
    """Summary view of voice analysis"""
    id: int
    student_id: int
    dominant_emotion: Optional[str]
    sentiment_score: Optional[float]
    created_at: datetime
    processing_status: ProcessingStatus
    
    class Config:
        from_attributes = True


class VoicePrompt(BaseModel):
    """Voice recording prompt"""
    id: int
    text: str = Field(..., description="Prompt text in Vietnamese")
    duration_seconds: int = Field(..., description="Recommended duration")
    category: str = Field(..., description="Prompt category")
    language: str = Field(default="vi", description="Language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "text": "Hãy chia sẻ về cảm xúc của bạn trong tuần qua",
                "duration_seconds": 60,
                "category": "general",
                "language": "vi"
            }
        }
