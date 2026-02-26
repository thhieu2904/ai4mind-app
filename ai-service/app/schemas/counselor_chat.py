"""
Counselor Chat schemas for API validation and serialization
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# REQUEST SCHEMAS (Input)
# ============================================

class MessageCreate(BaseModel):
    """Request schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Em cảm thấy lo lắng về kỳ thi sắp tới, cô có thể tư vấn giúp em được không ạ?"
            }
        }


class ConversationCreate(BaseModel):
    """Request schema for creating a conversation with a counselor"""
    counselor_id: int = Field(..., gt=0, description="ID of the counselor to chat with")

    class Config:
        json_schema_extra = {
            "example": {
                "counselor_id": 1
            }
        }


# ============================================
# RESPONSE SCHEMAS (Output)
# ============================================

class MessageResponse(BaseModel):
    """Response schema for a message"""
    id: int
    conversation_id: int
    sender_type: str = Field(..., description="'student' or 'counselor'")
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "sender_type": "counselor",
                "content": "Xin chào em! Tôi là chuyên gia tâm lý. Em hãy chia sẻ với tôi nhé.",
                "is_read": True,
                "created_at": "2025-10-05T10:30:00Z"
            }
        }


class ConversationResponse(BaseModel):
    """Response schema for a conversation"""
    id: int
    student_id: int
    counselor_id: int
    status: str
    last_message_at: datetime
    created_at: datetime
    unread_count: Optional[int] = 0  # Computed field
    student_name: Optional[str] = None  # Populated for counselor view
    counselor_name: Optional[str] = None  # Populated for student view

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": 5,
                "counselor_id": 1,
                "status": "active",
                "last_message_at": "2025-10-05T10:30:00Z",
                "created_at": "2025-10-05T10:00:00Z",
                "unread_count": 2
            }
        }


class CounselorBasicInfo(BaseModel):
    """Basic counselor information for listing"""
    id: int
    user_id: int
    full_name: str
    specialization: Optional[str]
    years_of_experience: Optional[int]
    bio: Optional[str]
    is_available: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 10,
                "full_name": "TS. Nguyễn Văn A",
                "specialization": "Tâm lý lâm sàng, Lo âu, Trầm cảm",
                "years_of_experience": 8,
                "bio": "Chuyên gia tâm lý lâm sàng với 8 năm kinh nghiệm hỗ trợ sinh viên",
                "is_available": True
            }
        }


class ConversationDetail(BaseModel):
    """Detailed conversation with counselor info and messages"""
    conversation: ConversationResponse
    counselor: CounselorBasicInfo
    messages: List[MessageResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "conversation": {
                    "id": 1,
                    "student_id": 5,
                    "counselor_id": 1,
                    "status": "active",
                    "last_message_at": "2025-10-05T10:30:00Z",
                    "created_at": "2025-10-05T10:00:00Z",
                    "unread_count": 0
                },
                "counselor": {
                    "id": 1,
                    "user_id": 10,
                    "full_name": "TS. Nguyễn Văn A",
                    "specialization": "Tâm lý lâm sàng",
                    "years_of_experience": 8,
                    "bio": "Chuyên gia tâm lý",
                    "is_available": True
                },
                "messages": [
                    {
                        "id": 1,
                        "conversation_id": 1,
                        "sender_type": "counselor",
                        "content": "Xin chào em!",
                        "is_read": True,
                        "created_at": "2025-10-05T10:00:00Z"
                    },
                    {
                        "id": 2,
                        "conversation_id": 1,
                        "sender_type": "student",
                        "content": "Chào cô ạ!",
                        "is_read": True,
                        "created_at": "2025-10-05T10:05:00Z"
                    }
                ]
            }
        }


class MessageReadUpdate(BaseModel):
    """Request schema for marking message as read"""
    is_read: bool = Field(True, description="Mark message as read")

    class Config:
        json_schema_extra = {
            "example": {
                "is_read": True
            }
        }
