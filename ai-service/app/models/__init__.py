"""
SQLAlchemy Base class and model imports
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here to ensure they're registered
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent, ParentConsent
from app.models.counselor import Counselor
from app.models.assessment import Assessment
from app.models.conversation import Conversation, Message
from app.models.voice_analysis import VoiceAnalysis
from app.models.ai_chat import AIConversation, AIMessage

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Student",
    "Parent",
    "ParentConsent",
    "Counselor",
    "Assessment",
    "Conversation",
    "Message",
    "VoiceAnalysis",
    "AIConversation",
    "AIMessage",
]
