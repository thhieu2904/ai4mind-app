# TÓM TẮT TRIỂN KHAI AI CHAT - ĐANG THỰC HIỆN

## ✅ ĐÃ HOÀN THÀNH

### Backend (3/7 tasks)

- ✅ **Models** (`ai-service/app/models/ai_chat.py`)

  - AIConversation
  - AIMessage
  - Updated `__init__.py` và `student.py`

- ✅ **Schemas** (`ai-service/app/schemas/ai_chat.py`)

  - MessageCreate, MessageResponse
  - ConversationResponse, ChatResponse
  - AssessmentSummary, ConversationDetail

- ✅ **GeminiService** (`ai-service/app/services/gemini_service.py`)
  - Added `chat_with_mental_health_context()` method
  - Added `_build_mental_health_system_prompt()` helper
  - Supports assessment context + conversation history

---

## 🚧 ĐANG LÀM - TODO 5: Create AIChatService

File tiếp theo cần tạo: `ai-service/app/services/ai_chat_service.py`

### Nội dung file (COPY CODE BÊN DƯỚI):

```python
"""
AI Chat Service - Core logic for AI chat functionality
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Optional
from datetime import datetime

from app.models.ai_chat import AIConversation, AIMessage
from app.models.assessment import Assessment
from app.services.gemini_service import GeminiService


class AIChatService:
    """Service xử lý logic cho AI chat"""

    def __init__(self, db: Session):
        self.db = db
        self.gemini = GeminiService()

    def get_or_create_active_conversation(self, student_id: int) -> AIConversation:
        """
        Lấy conversation active hoặc tạo mới
        Rule: Mỗi student chỉ có 1 active conversation
        """
        # Check existing active conversation
        conversation = self.db.query(AIConversation).filter(
            AIConversation.student_id == student_id,
            AIConversation.is_active == True
        ).first()

        if conversation:
            return conversation

        # Create new conversation
        # Get latest assessment để link
        latest_assessment = self.db.query(Assessment).filter(
            Assessment.student_id == student_id
        ).order_by(desc(Assessment.created_at)).first()

        conversation = AIConversation(
            student_id=student_id,
            latest_assessment_id=latest_assessment.id if latest_assessment else None,
            title=f"Chat {datetime.now().strftime('%d/%m/%Y')}",
            is_active=True,
            last_message_at=datetime.now()
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        # Send welcome message với assessment context
        if latest_assessment:
            welcome_msg = self._generate_welcome_message(latest_assessment)
            self._save_ai_message(conversation.id, welcome_msg)
        else:
            # Welcome without assessment
            welcome_msg = """Xin chào! 👋 Tôi là AI4Mind Assistant.

Tôi ở đây để lắng nghe và hỗ trợ em về sức khỏe tinh thần.
Em có muốn chia sẻ gì với tôi không?"""
            self._save_ai_message(conversation.id, welcome_msg)

        return conversation

    async def send_message(
        self,
        student_id: int,
        message_content: str
    ) -> Dict:
        """
        Gửi message và nhận response từ AI

        Returns:
            Dict với user_message, ai_message, conversation_id, assessment_summary
        """
        # Get or create conversation
        conversation = self.get_or_create_active_conversation(student_id)

        # Save user message
        user_msg = AIMessage(
            conversation_id=conversation.id,
            role="user",
            content=message_content
        )
        self.db.add(user_msg)
        self.db.commit()
        self.db.refresh(user_msg)

        # Build context for AI
        context = self._build_context(conversation)

        # Call Gemini với context
        ai_response = await self.gemini.chat_with_mental_health_context(
            user_message=message_content,
            conversation_history=context["recent_messages"],
            assessment_data=context["assessment"]
        )

        # Save AI response
        ai_msg = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            related_assessment_id=conversation.latest_assessment_id
        )
        self.db.add(ai_msg)

        # Update last_message_at
        conversation.last_message_at = datetime.now()
        self.db.commit()
        self.db.refresh(ai_msg)

        return {
            "conversation_id": conversation.id,
            "user_message": user_msg,
            "ai_message": ai_msg,
            "assessment_summary": context.get("assessment")
        }

    def _build_context(self, conversation: AIConversation) -> Dict:
        """
        Xây dựng context cho AI
        Bao gồm: Assessment data + Recent messages (last 5)
        """
        # Get recent messages (exclude welcome message, get last 5 user/ai exchanges)
        recent_messages = self.db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation.id
        ).order_by(desc(AIMessage.created_at)).limit(6).all()

        # Reverse để đúng thứ tự thời gian (oldest first)
        recent_messages = list(reversed(recent_messages))

        # Format messages for Gemini (skip first if it's welcome)
        message_history = []
        for msg in recent_messages:
            message_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Get assessment data
        assessment_data = None
        if conversation.latest_assessment_id:
            assessment = self.db.query(Assessment).get(conversation.latest_assessment_id)
            if assessment:
                assessment_data = {
                    "id": assessment.id,
                    "score": assessment.total_score,
                    "severity": assessment.severity_level,
                    "date": assessment.created_at.strftime("%d/%m/%Y"),
                    "analysis": assessment.analysis if assessment.analysis else "",
                    "recommendations": assessment.recommendations if assessment.recommendations else []
                }

        return {
            "recent_messages": message_history,
            "assessment": assessment_data
        }

    def _generate_welcome_message(self, assessment: Assessment) -> str:
        """Generate welcome message với assessment context"""
        severity_map = {
            "minimal": "rất tốt",
            "mild": "ở mức nhẹ",
            "moderate": "ở mức trung bình",
            "severe": "đang cần được quan tâm"
        }

        severity_text = severity_map.get(assessment.severity_level, "")
        score = assessment.total_score

        # Different welcome based on severity
        if assessment.severity_level == "severe":
            return f"""Xin chào! 👋 Tôi là AI4Mind Assistant.

Tôi thấy em vừa hoàn thành bài đánh giá GAD-7 vào ngày {assessment.created_at.strftime('%d/%m/%Y')}.
Kết quả cho thấy em đang có mức độ lo âu khá cao ({score}/21 điểm).

Tôi ở đây để lắng nghe em. Em có muốn chia sẻ về những gì đang khiến em cảm thấy lo lắng không? 💙"""

        elif assessment.severity_level == "moderate":
            return f"""Xin chào! 👋 Tôi là AI4Mind Assistant.

Tôi thấy em vừa làm bài đánh giá GAD-7. Kết quả cho thấy em đang trải qua một số lo âu ({score}/21 điểm).

Tôi có thể giúp gì cho em hôm nay? Em muốn chia sẻ về cảm xúc của mình không? 😊"""

        else:
            return f"""Xin chào! 👋 Tôi là AI4Mind Assistant.

Cảm ơn em đã hoàn thành bài đánh giá GAD-7. Kết quả cho thấy tình trạng của em {severity_text}.

Tôi luôn ở đây để lắng nghe nếu em cần chia sẻ bất cứ điều gì nhé! 🌟"""

    def _save_ai_message(self, conversation_id: int, content: str):
        """Helper: Save AI message"""
        msg = AIMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=content
        )
        self.db.add(msg)
        self.db.commit()

    def get_conversation_messages(
        self,
        conversation_id: int,
        student_id: int
    ) -> List[AIMessage]:
        """Get all messages in conversation"""
        # Verify ownership
        conversation = self.db.query(AIConversation).filter(
            AIConversation.id == conversation_id,
            AIConversation.student_id == student_id
        ).first()

        if not conversation:
            raise ValueError("Conversation not found or access denied")

        return self.db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).order_by(AIMessage.created_at).all()

    def get_student_conversations(self, student_id: int, limit: int = 10) -> List[AIConversation]:
        """Get list of conversations cho student"""
        return self.db.query(AIConversation).filter(
            AIConversation.student_id == student_id
        ).order_by(desc(AIConversation.last_message_at)).limit(limit).all()

    def end_conversation(self, student_id: int) -> None:
        """Set active conversation to inactive"""
        conversation = self.db.query(AIConversation).filter(
            AIConversation.student_id == student_id,
            AIConversation.is_active == True
        ).first()

        if conversation:
            conversation.is_active = False
            self.db.commit()
```

---

## 📝 TIẾP THEO - SAU KHI TẠO FILE TRÊN:

### TODO 6: Create API Endpoints

File: `ai-service/app/api/v1/endpoints/ai_chat.py`

Code đầy đủ có trong file `AI_CHAT_IMPLEMENTATION_FLOW.md` (section "4. API Endpoints")

### TODO 7: Register Router

Thêm vào `ai-service/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import ai_chat

api_router.include_router(ai_chat.router, prefix="/ai-chat", tags=["AI Chat"])
```

---

## 📊 PROGRESS

- Backend: 43% (3/7)
- Frontend: 0% (0/4)
- Testing: 0% (0/3)

**Total: 21% completed (3/14 tasks)**

---

## 🎯 GỢI Ý

Bạn muốn tôi:

1. **A.** Tiếp tục tạo files còn lại (API endpoints, frontend)
2. **B.** Hướng dẫn bạn tự tạo và tôi review
3. **C.** Tạm dừng, setup database trên Supabase trước

---

_Last updated: In progress_
_Current task: Creating AIChatService_
