"""
AI Chat schemas for API validation and serialization
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================
# REQUEST SCHEMAS (Input)
# ============================================

class MessageCreate(BaseModel):
    """Request schema for creating a message"""
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Em đang cảm thấy lo lắng về kỳ thi sắp tới"
            }
        }


class ConversationCreate(BaseModel):
    """Request schema for creating a conversation (optional - auto-created)"""
    title: Optional[str] = Field(None, max_length=255, description="Conversation title")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Chat về lo âu"
            }
        }


# ============================================
# RESPONSE SCHEMAS (Output)
# ============================================

class MessageResponse(BaseModel):
    """Response schema for a message"""
    id: int
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    created_at: datetime
    related_assessment_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "role": "assistant",
                "content": "Xin chào! Tôi là AI4Mind Assistant. Em có thể chia sẻ với tôi...",
                "created_at": "2025-10-05T10:30:00Z",
                "related_assessment_id": None
            }
        }


class ConversationResponse(BaseModel):
    """Response schema for a conversation"""
    id: int
    title: str
    is_active: bool
    created_at: datetime
    last_message_at: datetime
    latest_assessment_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Chat với AI",
                "is_active": True,
                "created_at": "2025-10-05T10:00:00Z",
                "last_message_at": "2025-10-05T10:30:00Z",
                "latest_assessment_id": 34
            }
        }


class AssessmentSummary(BaseModel):
    """Summary of GAD-7 assessment for context"""
    id: int
    score: int
    severity: str
    date: str
    analysis: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 34,
                "score": 15,
                "severity": "severe",
                "date": "03/10/2025",
                "analysis": "Kết quả cho thấy em đang có mức độ lo âu cao..."
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat exchange (user message + AI response)"""
    conversation_id: int
    user_message: MessageResponse
    ai_message: MessageResponse
    assessment_summary: Optional[AssessmentSummary] = None

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "user_message": {
                    "id": 2,
                    "role": "user",
                    "content": "Em đang lo lắng",
                    "created_at": "2025-10-05T10:30:00Z",
                    "related_assessment_id": None
                },
                "ai_message": {
                    "id": 3,
                    "role": "assistant",
                    "content": "Em đang lo lắng à? Hãy chia sẻ thêm với tôi...",
                    "created_at": "2025-10-05T10:30:05Z",
                    "related_assessment_id": 34
                },
                "assessment_summary": {
                    "id": 34,
                    "score": 15,
                    "severity": "severe",
                    "date": "03/10/2025"
                }
            }
        }


class ConversationDetail(BaseModel):
    """Detailed conversation with all messages"""
    conversation: ConversationResponse
    messages: list[MessageResponse]
    message_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "conversation": {
                    "id": 1,
                    "title": "Chat với AI",
                    "is_active": True,
                    "created_at": "2025-10-05T10:00:00Z",
                    "last_message_at": "2025-10-05T10:30:00Z",
                    "latest_assessment_id": 34
                },
                "messages": [],
                "message_count": 5
            }
        }


# ============================================
# FEEDBACK SCHEMAS (Optional - for future)
# ============================================

class ChatFeedbackCreate(BaseModel):
    """Request schema for chat feedback"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "feedback_text": "AI rất hữu ích và thông cảm"
            }
        }
