"""
Counselor Chat API Endpoints
Direct messaging between students and counselors
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.counselor import Counselor
from app.schemas.counselor_chat import (
    MessageCreate,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationDetail,
    CounselorBasicInfo,
    MessageReadUpdate
)
from app.services.counselor_chat_service import CounselorChatService

router = APIRouter()


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_student_from_user(current_user: User, db: Session) -> Student:
    """Get student profile from current user"""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please complete your profile first."
        )
    return student


def get_counselor_from_user(current_user: User, db: Session) -> Counselor:
    """Get counselor profile from current user"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counselor profile not found."
        )
    return counselor


# ============================================
# COUNSELOR LISTING
# ============================================

@router.get("/counselors", response_model=List[CounselorBasicInfo])
async def list_available_counselors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get danh sách counselors đang available
    Chỉ students mới access endpoint này
    
    Returns:
        List[CounselorBasicInfo]: Danh sách counselors với thông tin cơ bản
    """
    # Verify student role
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view counselor list"
        )
    
    try:
        chat_service = CounselorChatService(db)
        counselors = chat_service.get_available_counselors()
        
        # Convert to response schema
        result = []
        for counselor in counselors:
            result.append(CounselorBasicInfo(
                id=counselor.id,
                user_id=counselor.user_id,
                full_name=counselor.user.full_name,
                specialization=counselor.specialization,
                years_of_experience=counselor.years_of_experience,
                bio=counselor.bio,
                is_available=counselor.is_available
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch counselors: {str(e)}"
        )


# ============================================
# CONVERSATION MANAGEMENT
# ============================================

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo conversation mới với counselor
    Nếu đã tồn tại conversation, trả về existing conversation
    
    Args:
        request: ConversationCreate với counselor_id
        
    Returns:
        ConversationResponse: Conversation đã tạo
    """
    # Verify student role
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create conversations with counselors"
        )
    
    student = get_student_from_user(current_user, db)
    
    try:
        chat_service = CounselorChatService(db)
        conversation = chat_service.create_or_get_conversation(
            student_id=student.id,
            counselor_id=request.counselor_id
        )
        
        # Count unread messages
        unread_count = chat_service._count_unread_messages(conversation.id, "student")
        
        return ConversationResponse(
            id=conversation.id,
            student_id=conversation.student_id,
            counselor_id=conversation.counselor_id,
            status=conversation.status,
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at,
            unread_count=unread_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chi tiết conversation với counselor info và messages
    
    Args:
        conversation_id: ID của conversation
        
    Returns:
        ConversationDetail: Conversation với counselor info và messages
    """
    try:
        chat_service = CounselorChatService(db)
        
        # Get conversation với permission check
        result = chat_service.get_conversation_with_details(
            conversation_id=conversation_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        # Convert to response schema
        conversation_response = ConversationResponse(
            id=result["conversation"].id,
            student_id=result["conversation"].student_id,
            counselor_id=result["conversation"].counselor_id,
            status=result["conversation"].status,
            last_message_at=result["conversation"].last_message_at,
            created_at=result["conversation"].created_at,
            unread_count=result["unread_count"]
        )
        
        counselor_info = CounselorBasicInfo(
            id=result["counselor"].id,
            user_id=result["counselor"].user_id,
            full_name=result["counselor"].user.full_name,
            specialization=result["counselor"].specialization,
            years_of_experience=result["counselor"].years_of_experience,
            bio=result["counselor"].bio,
            is_available=result["counselor"].is_available
        )
        
        messages = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_type=msg.sender_type,
                content=msg.content,
                is_read=msg.is_read,
                created_at=msg.created_at
            )
            for msg in result["messages"]
        ]
        
        return ConversationDetail(
            conversation=conversation_response,
            counselor=counselor_info,
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_my_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations của current user (student hoặc counselor)
    
    Returns:
        List[ConversationResponse]: Danh sách conversations
    """
    try:
        chat_service = CounselorChatService(db)
        
        if current_user.role == UserRole.STUDENT:
            student = get_student_from_user(current_user, db)
            conversations = chat_service.get_conversations_for_student(student.id)
        elif current_user.role == UserRole.COUNSELOR:
            counselor = get_counselor_from_user(current_user, db)
            conversations = chat_service.get_conversations_for_counselor(counselor.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid role for this endpoint"
            )
        
        # Convert to response
        result = []
        for conv in conversations:
            unread_count = chat_service._count_unread_messages(conv.id, current_user.role)
            student_name = None
            counselor_name = None
            try:
                if hasattr(conv, "student") and conv.student and hasattr(conv.student, "user"):
                    student_name = conv.student.user.full_name
                if hasattr(conv, "counselor") and conv.counselor and hasattr(conv.counselor, "user"):
                    counselor_name = conv.counselor.user.full_name
            except Exception:
                pass
            result.append(ConversationResponse(
                id=conv.id,
                student_id=conv.student_id,
                counselor_id=conv.counselor_id,
                status=conv.status,
                last_message_at=conv.last_message_at,
                created_at=conv.created_at,
                unread_count=unread_count,
                student_name=student_name,
                counselor_name=counselor_name,
            ))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}"
        )


# ============================================
# MESSAGE MANAGEMENT
# ============================================

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi message trong conversation
    
    Args:
        conversation_id: ID của conversation
        request: MessageCreate với content
        
    Returns:
        MessageResponse: Message đã gửi
    """
    try:
        chat_service = CounselorChatService(db)
        
        # Determine sender_type from user role
        if current_user.role == UserRole.STUDENT:
            sender_type = "student"
        elif current_user.role == UserRole.COUNSELOR:
            sender_type = "counselor"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students and counselors can send messages"
            )
        
        # Send message với permission check
        message = chat_service.send_message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=request.content,
            user_id=current_user.id
        )
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_type=message.sender_type,
            content=message.content,
            is_read=message.is_read,
            created_at=message.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.patch("/messages/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đánh dấu message đã đọc
    
    Args:
        message_id: ID của message
        
    Returns:
        MessageResponse: Message đã update
    """
    try:
        chat_service = CounselorChatService(db)
        
        message = chat_service.mark_message_as_read(
            message_id=message_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_type=message.sender_type,
            content=message.content,
            is_read=message.is_read,
            created_at=message.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark message as read: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/mark-all-read")
async def mark_all_messages_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đánh dấu tất cả messages trong conversation đã đọc
    
    Args:
        conversation_id: ID của conversation
        
    Returns:
        Dict với số messages đã mark
    """
    try:
        chat_service = CounselorChatService(db)
        
        updated_count = chat_service.mark_all_messages_as_read(
            conversation_id=conversation_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "marked_count": updated_count,
            "message": f"Marked {updated_count} messages as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark messages as read: {str(e)}"
        )
