"""
Pydantic schemas for request/response validation
"""
from .auth import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData
)
from .assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentDetail,
    AssessmentStats,
    AssessmentListResponse
)
from .student import (
    GenderEnum,
    StudentBase,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentPublicProfile
)
from .voice_analysis import (
    ProcessingStatus,
    AudioFeatures,
    EmotionScores,
    Keyword,
    PsychologicalMarkers,
    TextAnalysis,
    NormalizedFeatures,
    VoiceAnalysisCreate,
    VoiceAnalysisResponse,
    VoiceAnalysisDetail,
    VoiceAnalysisSummary,
    VoicePrompt
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "AssessmentCreate",
    "AssessmentResponse",
    "AssessmentDetail",
    "AssessmentStats",
    "AssessmentListResponse",
    "GenderEnum",
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentPublicProfile",
    "ProcessingStatus",
    "AudioFeatures",
    "EmotionScores",
    "Keyword",
    "PsychologicalMarkers",
    "TextAnalysis",
    "NormalizedFeatures",
    "VoiceAnalysisCreate",
    "VoiceAnalysisResponse",
    "VoiceAnalysisDetail",
    "VoiceAnalysisSummary",
    "VoicePrompt"
]
