"""
Counselor Chat Service - Core logic for counselor messaging
Direct messaging between students and counselors (human-to-human)
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import HTTPException, status

from app.models.counselor_chat import CounselorConversation, CounselorMessage
from app.models.counselor import Counselor
from app.models.user import User, UserRole


class CounselorChatService:
    """Service xử lý logic cho counselor chat"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================
    # COUNSELOR LISTING
    # ============================================
    
    def get_available_counselors(self) -> List[Counselor]:
        """
        Lấy danh sách counselors đang available
        
        Returns:
            List[Counselor]: List counselors với is_available=True
        """
        counselors = (
            self.db.query(Counselor)
            .join(User)
            .filter(
                Counselor.is_available == True,
                User.is_active == True,
                User.is_verified == True
            )
            .options(joinedload(Counselor.user))
            .all()
        )
        
        return counselors
    
    # ============================================
    # CONVERSATION MANAGEMENT
    # ============================================
    
    def create_or_get_conversation(
        self, 
        student_id: int, 
        counselor_id: int
    ) -> CounselorConversation:
        """
        Tạo conversation mới hoặc lấy existing conversation
        Rule: Mỗi cặp student-counselor chỉ có 1 conversation
        
        Args:
            student_id: ID của student
            counselor_id: ID của counselor
            
        Returns:
            CounselorConversation: Conversation đã tạo hoặc existing
            
        Raises:
            HTTPException: Nếu counselor không tồn tại hoặc không available
        """
        # Verify counselor exists and is available
        counselor = self.db.query(Counselor).filter(
            Counselor.id == counselor_id
        ).first()
        
        if not counselor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Counselor with ID {counselor_id} not found"
            )
        
        if not counselor.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Counselor {counselor_id} is not currently available"
            )
        
        # Check existing conversation
        conversation = self.db.query(CounselorConversation).filter(
            CounselorConversation.student_id == student_id,
            CounselorConversation.counselor_id == counselor_id
        ).first()
        
        if conversation:
            # Reactivate if closed/archived
            if conversation.status != "active":
                conversation.status = "active"
                conversation.last_message_at = datetime.now()
                self.db.commit()
                self.db.refresh(conversation)
            return conversation
        
        # Create new conversation
        conversation = CounselorConversation(
            student_id=student_id,
            counselor_id=counselor_id,
            status="active",
            last_message_at=datetime.now()
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def get_conversation_with_details(
        self, 
        conversation_id: int,
        user_id: int,
        user_role: str
    ) -> Optional[Dict]:
        """
        Lấy conversation detail với counselor info và messages
        
        Args:
            conversation_id: ID của conversation
            user_id: ID của user (để verify permission)
            user_role: Role của user ('student' hoặc 'counselor')
            
        Returns:
            Dict với conversation, counselor, messages
            
        Raises:
            HTTPException: Nếu không tìm thấy hoặc không có permission
        """
        conversation = (
            self.db.query(CounselorConversation)
            .options(
                joinedload(CounselorConversation.counselor).joinedload(Counselor.user),
                joinedload(CounselorConversation.student)
            )
            .filter(CounselorConversation.id == conversation_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Verify permission
        if user_role == UserRole.STUDENT.value or user_role == UserRole.STUDENT:
            # Student chỉ xem conversation của mình
            if conversation.student.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this conversation"
                )
        elif user_role == UserRole.COUNSELOR.value or user_role == UserRole.COUNSELOR:
            # Counselor chỉ xem conversation của mình
            if conversation.counselor.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this conversation"
                )
        
        # Load messages
        messages = (
            self.db.query(CounselorMessage)
            .filter(CounselorMessage.conversation_id == conversation_id)
            .order_by(CounselorMessage.created_at.asc())
            .all()
        )
        
        # Count unread messages
        unread_count = self._count_unread_messages(conversation_id, user_role)
        
        return {
            "conversation": conversation,
            "counselor": conversation.counselor,
            "messages": messages,
            "unread_count": unread_count
        }
    
    def get_conversations_for_student(self, student_id: int) -> List[CounselorConversation]:
        """
        Lấy all conversations của student (sorted by last_message_at)
        
        Args:
            student_id: ID của student
            
        Returns:
            List[CounselorConversation]: Danh sách conversations
        """
        conversations = (
            self.db.query(CounselorConversation)
            .filter(CounselorConversation.student_id == student_id)
            .options(joinedload(CounselorConversation.counselor).joinedload(Counselor.user))
            .order_by(desc(CounselorConversation.last_message_at))
            .all()
        )
        
        return conversations

    def get_conversations_for_counselor(self, counselor_id: int) -> List[CounselorConversation]:
        """
        Lấy all conversations của counselor (sorted by last_message_at)
        
        Args:
            counselor_id: ID của counselor profile
            
        Returns:
            List[CounselorConversation]: Danh sách conversations
        """
        from app.models.student import Student
        conversations = (
            self.db.query(CounselorConversation)
            .filter(CounselorConversation.counselor_id == counselor_id)
            .options(
                joinedload(CounselorConversation.student).joinedload(Student.user)
            )
            .order_by(desc(CounselorConversation.last_message_at))
            .all()
        )
        
        return conversations
    
    # ============================================
    # MESSAGE MANAGEMENT
    # ============================================
    
    def send_message(
        self,
        conversation_id: int,
        sender_type: str,
        content: str,
        user_id: int
    ) -> CounselorMessage:
        """
        Gửi message trong conversation
        
        Args:
            conversation_id: ID của conversation
            sender_type: 'student' hoặc 'counselor'
            content: Nội dung message
            user_id: ID của user (để verify permission)
            
        Returns:
            CounselorMessage: Message đã gửi
            
        Raises:
            HTTPException: Nếu không có permission hoặc conversation không tồn tại
        """
        # Get conversation
        conversation = self.db.query(CounselorConversation).filter(
            CounselorConversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Verify permission
        if sender_type == "student":
            student = self.db.query(User).filter(User.id == user_id).first()
            if not student or student.role != UserRole.STUDENT:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only students can send as 'student'"
                )
            # Check if this student owns the conversation
            from app.models.student import Student
            student_record = self.db.query(Student).filter(Student.user_id == user_id).first()
            if not student_record or student_record.id != conversation.student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to send in this conversation"
                )
        elif sender_type == "counselor":
            counselor_user = self.db.query(User).filter(User.id == user_id).first()
            if not counselor_user or counselor_user.role != UserRole.COUNSELOR:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only counselors can send as 'counselor'"
                )
            # Check if this counselor owns the conversation
            counselor_record = self.db.query(Counselor).filter(Counselor.user_id == user_id).first()
            if not counselor_record or counselor_record.id != conversation.counselor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to send in this conversation"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sender_type must be 'student' or 'counselor'"
            )
        
        # Create message
        message = CounselorMessage(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            is_read=False  # Always start as unread
        )
        
        self.db.add(message)
        
        # Update conversation last_message_at (trigger will handle this, but update manually for safety)
        conversation.last_message_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def mark_message_as_read(self, message_id: int, user_id: int, user_role: str) -> CounselorMessage:
        """
        Đánh dấu message đã đọc
        
        Args:
            message_id: ID của message
            user_id: ID của user (để verify permission)
            user_role: Role của user
            
        Returns:
            CounselorMessage: Message đã update
            
        Raises:
            HTTPException: Nếu không có permission
        """
        message = self.db.query(CounselorMessage).filter(
            CounselorMessage.id == message_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found"
            )
        
        # Get conversation để check permission
        conversation = self.db.query(CounselorConversation).filter(
            CounselorConversation.id == message.conversation_id
        ).first()
        
        # Verify permission (chỉ receiver mới mark as read)
        if user_role == UserRole.STUDENT.value or user_role == UserRole.STUDENT:
            # Student chỉ mark read message từ counselor
            from app.models.student import Student
            student_record = self.db.query(Student).filter(Student.user_id == user_id).first()
            if not student_record or student_record.id != conversation.student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to mark this message as read"
                )
            if message.sender_type == "student":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot mark your own message as read"
                )
        elif user_role == UserRole.COUNSELOR.value or user_role == UserRole.COUNSELOR:
            # Counselor chỉ mark read message từ student
            counselor_record = self.db.query(Counselor).filter(Counselor.user_id == user_id).first()
            if not counselor_record or counselor_record.id != conversation.counselor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to mark this message as read"
                )
            if message.sender_type == "counselor":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot mark your own message as read"
                )
        
        # Update
        message.is_read = True
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def mark_all_messages_as_read(
        self, 
        conversation_id: int, 
        user_id: int, 
        user_role: str
    ) -> int:
        """
        Đánh dấu tất cả messages trong conversation đã đọc
        
        Args:
            conversation_id: ID của conversation
            user_id: ID của user
            user_role: Role của user
            
        Returns:
            int: Số messages đã mark as read
        """
        conversation = self.db.query(CounselorConversation).filter(
            CounselorConversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Verify permission
        if user_role == UserRole.STUDENT.value or user_role == UserRole.STUDENT:
            from app.models.student import Student
            student_record = self.db.query(Student).filter(Student.user_id == user_id).first()
            if not student_record or student_record.id != conversation.student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to mark messages in this conversation"
                )
            # Mark counselor messages as read
            sender_type_filter = "counselor"
        elif user_role == UserRole.COUNSELOR.value or user_role == UserRole.COUNSELOR:
            counselor_record = self.db.query(Counselor).filter(Counselor.user_id == user_id).first()
            if not counselor_record or counselor_record.id != conversation.counselor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to mark messages in this conversation"
                )
            # Mark student messages as read
            sender_type_filter = "student"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user role"
            )
        
        # Update all unread messages from opposite sender
        updated_count = (
            self.db.query(CounselorMessage)
            .filter(
                CounselorMessage.conversation_id == conversation_id,
                CounselorMessage.sender_type == sender_type_filter,
                CounselorMessage.is_read == False
            )
            .update({"is_read": True})
        )
        
        self.db.commit()
        
        return updated_count
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _count_unread_messages(self, conversation_id: int, user_role: str) -> int:
        """
        Đếm số unread messages trong conversation
        
        Args:
            conversation_id: ID của conversation
            user_role: Role của user ('student' hoặc 'counselor')
            
        Returns:
            int: Số unread messages
        """
        # Student đếm messages từ counselor, counselor đếm messages từ student
        sender_type = "counselor" if (user_role == UserRole.STUDENT.value or user_role == UserRole.STUDENT) else "student"
        
        count = (
            self.db.query(func.count(CounselorMessage.id))
            .filter(
                CounselorMessage.conversation_id == conversation_id,
                CounselorMessage.sender_type == sender_type,
                CounselorMessage.is_read == False
            )
            .scalar()
        )
        
        return count or 0
