"""
AI Chat API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.student import Student
from app.schemas.ai_chat import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ChatResponse,
    ConversationDetail
)
from app.services.ai_chat_service import AIChatService

router = APIRouter()


def get_student_from_user(current_user: User, db: Session) -> Student:
    """Helper: Get student profile from current user"""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please complete your profile first."
        )
    return student


@router.get("/conversation", response_model=ConversationResponse)
async def get_or_create_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active conversation hoặc tạo mới
    Trả về conversation với welcome message nếu là mới
    """
    student = get_student_from_user(current_user, db)
    
    try:
        chat_service = AIChatService(db)
        conversation = chat_service.get_or_create_active_conversation(student.id)
        
        # Get all messages including welcome
        messages = chat_service.get_conversation_messages(conversation.id, student.id)
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            last_message_at=conversation.last_message_at,
            is_active=conversation.is_active,
            message_count=len(messages),
            latest_assessment_id=conversation.latest_assessment_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages in conversation
    Sắp xếp theo thời gian (oldest first)
    """
    student = get_student_from_user(current_user, db)
    
    try:
        chat_service = AIChatService(db)
        messages = chat_service.get_conversation_messages(conversation_id, student.id)
        
        return [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                related_assessment_id=msg.related_assessment_id
            )
            for msg in messages
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message và nhận AI response
    
    Flow:
    1. Save user message
    2. Build context (assessment + recent messages)
    3. Call Gemini API
    4. Save AI response
    5. Return both messages
    """
    student = get_student_from_user(current_user, db)
    
    if not message_data.content or not message_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )
    
    try:
        chat_service = AIChatService(db)
        result = await chat_service.send_message(
            student_id=student.id,
            message_content=message_data.content.strip()
        )
        
        user_msg = result["user_message"]
        ai_msg = result["ai_message"]
        assessment = result.get("assessment_summary")
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            user_message=MessageResponse(
                id=user_msg.id,
                role=user_msg.role,
                content=user_msg.content,
                created_at=user_msg.created_at,
                related_assessment_id=user_msg.related_assessment_id
            ),
            ai_message=MessageResponse(
                id=ai_msg.id,
                role=ai_msg.role,
                content=ai_msg.content,
                created_at=ai_msg.created_at,
                related_assessment_id=ai_msg.related_assessment_id
            ),
            assessment_context=assessment
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/end-conversation")
async def end_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kết thúc conversation hiện tại
    Set is_active = False
    """
    student = get_student_from_user(current_user, db)
    
    try:
        chat_service = AIChatService(db)
        chat_service.end_conversation(student.id)
        
        return {
            "message": "Conversation ended successfully",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end conversation: {str(e)}"
        )


@router.get("/history", response_model=List[ConversationDetail])
async def get_conversation_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get danh sách conversations của student
    Sorted by last_message_at DESC
    """
    student = get_student_from_user(current_user, db)
    
    try:
        chat_service = AIChatService(db)
        conversations = chat_service.get_student_conversations(student.id, limit)
        
        result = []
        for conv in conversations:
            # Get message count
            messages = chat_service.get_conversation_messages(conv.id, student.id)
            
            # Get preview (last message)
            last_msg = messages[-1] if messages else None
            
            result.append(ConversationDetail(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                last_message_at=conv.last_message_at,
                is_active=conv.is_active,
                message_count=len(messages),
                latest_assessment_id=conv.latest_assessment_id,
                last_message_preview=last_msg.content[:100] if last_msg else None
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )
