# AI CHAT FLOW - THIẾT KẾ CỤ THỂ CHO AI4MIND

## 🎯 REQUIREMENTS

### Flow mong muốn:

1. ✅ User bắt đầu chat từ Dashboard
2. ✅ Gửi message kèm theo:
   - Thông tin GAD-7 assessment gần nhất (nếu có)
   - Lịch sử chat gần đây (2-3 messages)
3. ✅ AI hiểu context và phản hồi phù hợp
4. ✅ Giao diện như app nhắn tin (WhatsApp, Messenger)

---

## 🏗️ KIẾN TRÚC FLOW

```
┌─────────────┐
│  Dashboard  │
│   Button    │ "Trò chuyện với AI"
└──────┬──────┘
       │ Click
       ▼
┌─────────────────────────────────────────────┐
│  Step 1: Check if conversation exists       │
│  - Query: Has active conversation?          │
│    ✅ Yes → Load existing conversation      │
│    ❌ No  → Create new conversation         │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Step 2: Load Context                       │
│  - Latest GAD-7 assessment                  │
│  - Recent messages (last 5)                 │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Chat UI (Messenger-like)                   │
│  ┌────────────────────────────────────┐    │
│  │  AI: Xin chào! 👋                  │    │
│  │  Tôi thấy em vừa làm assessment... │    │
│  └────────────────────────────────────┘    │
│                                             │
│         ┌──────────────────────────┐        │
│         │ User: Em đang lo lắng... │        │
│         └──────────────────────────┘        │
│  [___Type message___________] [Send]        │
└─────────────────────────────────────────────┘
       │
       ▼ User sends message
┌─────────────────────────────────────────────┐
│  Step 3: Build Context for AI              │
│  {                                          │
│    "current_message": "Em đang lo lắng",    │
│    "recent_history": [...5 messages],       │
│    "assessment_context": {                  │
│      "score": 15,                           │
│      "severity": "severe",                  │
│      "date": "2025-10-03",                  │
│      "analysis": "..."                      │
│    }                                        │
│  }                                          │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Step 4: Call Gemini with Smart Context    │
│  - System prompt: Mental health assistant   │
│  - User context: Assessment + history       │
│  - Current question                         │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Step 5: Save & Display Response           │
│  - Save user message to DB                  │
│  - Save AI response to DB                   │
│  - Display in chat UI                       │
└─────────────────────────────────────────────┘
```

---

## 📊 DATABASE SCHEMA (Tối giản hóa)

```sql
-- Table 1: Conversations (Cuộc trò chuyện)
CREATE TABLE ai_conversations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,

    -- Link to latest assessment for quick access
    latest_assessment_id INTEGER REFERENCES assessments(id),

    -- Metadata
    title VARCHAR(255) DEFAULT 'Chat với AI',
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW()
);

-- Table 2: Messages (Tin nhắn)
CREATE TABLE ai_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ai_conversations(id) ON DELETE CASCADE,

    -- Message content
    role VARCHAR(20) NOT NULL,  -- 'user' hoặc 'assistant'
    content TEXT NOT NULL,

    -- Optional: Link to assessment được discuss
    related_assessment_id INTEGER REFERENCES assessments(id),

    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table 3: Quick Feedback (Optional - có thể bỏ qua ban đầu)
CREATE TABLE ai_chat_feedback (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ai_conversations(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_ai_messages_conversation ON ai_messages(conversation_id, created_at DESC);
CREATE INDEX idx_ai_conversations_student ON ai_conversations(student_id, last_message_at DESC);
```

**→ 2 tables chính là đủ để bắt đầu!**

---

## 🔧 BACKEND IMPLEMENTATION

### 1. Models (ai-service/app/models/ai_chat.py)

```python
"""
AI Chat models - Simplified version
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class AIConversation(Base):
    """AI chat conversation"""
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    latest_assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)

    title = Column(String(255), default="Chat với AI")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", backref="ai_conversations")
    latest_assessment = relationship("Assessment")
    messages = relationship(
        "AIMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AIMessage.created_at"
    )


class AIMessage(Base):
    """AI chat message"""
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"))

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    related_assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")
```

---

### 2. Schemas (ai-service/app/schemas/ai_chat.py)

```python
"""
AI Chat schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    """Request: User gửi message"""
    content: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    """Response: Message detail"""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response: Conversation detail"""
    id: int
    title: str
    is_active: bool
    created_at: datetime
    last_message_at: datetime
    latest_assessment_id: Optional[int] = None

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Response: Chat với cả user message và AI response"""
    conversation_id: int
    user_message: MessageResponse
    ai_message: MessageResponse

    # Optional: Include assessment context in response
    assessment_summary: Optional[dict] = None
```

---

### 3. Service (ai-service/app/services/ai_chat_service.py)

```python
"""
AI Chat Service - Core logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Optional
from datetime import datetime

from app.models.ai_chat import AIConversation, AIMessage
from app.models.assessment import Assessment
from app.services.gemini_service import GeminiService


class AIChatService:
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

        return conversation

    async def send_message(
        self,
        student_id: int,
        message_content: str
    ) -> Dict:
        """
        Gửi message và nhận response từ AI
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

        # Call Gemini
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
            "assessment_summary": context["assessment"] if context["assessment"] else None
        }

    def _build_context(self, conversation: AIConversation) -> Dict:
        """
        Xây dựng context cho AI
        Bao gồm: Assessment data + Recent messages
        """
        # Get recent messages (last 5)
        recent_messages = self.db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation.id
        ).order_by(desc(AIMessage.created_at)).limit(5).all()

        # Reverse để đúng thứ tự thời gian
        recent_messages = list(reversed(recent_messages))

        # Format messages for Gemini
        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]

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
                    "analysis": assessment.analysis,
                    "recommendations": assessment.recommendations
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

        return f"""Xin chào! 👋 Tôi là AI4Mind Assistant.

Tôi thấy em vừa hoàn thành bài đánh giá GAD-7 vào ngày {assessment.created_at.strftime('%d/%m/%Y')}.
Kết quả cho thấy tình trạng của em {severity_text}.

Em có muốn chia sẻ về cảm xúc của mình hoặc cần tôi hỗ trợ gì không?"""

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
        """Get list of conversations"""
        return self.db.query(AIConversation).filter(
            AIConversation.student_id == student_id
        ).order_by(desc(AIConversation.last_message_at)).limit(limit).all()
```

---

### 4. Update GeminiService (ai-service/app/services/gemini_service.py)

```python
# Add this method to existing GeminiService class

async def chat_with_mental_health_context(
    self,
    user_message: str,
    conversation_history: List[Dict],
    assessment_data: Optional[Dict] = None
) -> str:
    """
    Chat với context từ assessment và history

    Args:
        user_message: Tin nhắn hiện tại của user
        conversation_history: Lịch sử chat gần đây
        assessment_data: Thông tin GAD-7 assessment (nếu có)
    """
    # Build system instruction
    system_instruction = self._get_mental_health_chat_prompt(assessment_data)

    # Build full prompt với context
    context_prompt = ""

    if assessment_data:
        context_prompt = f"""
[CONTEXT - Assessment của user]
- Ngày đánh giá: {assessment_data['date']}
- Điểm GAD-7: {assessment_data['score']}/21
- Mức độ: {assessment_data['severity']}
- Phân tích: {assessment_data['analysis'][:200]}...

"""

    # Add conversation history
    if conversation_history:
        context_prompt += "[LỊCH SỬ CHAT GÇN ĐÂY]\n"
        for msg in conversation_history[-3:]:  # Only last 3 for context
            role_text = "User" if msg["role"] == "user" else "AI"
            context_prompt += f"{role_text}: {msg['content'][:100]}...\n"
        context_prompt += "\n"

    # Full message
    full_message = context_prompt + f"[TIN NHẮN MỚI]\nUser: {user_message}"

    # Call Gemini
    try:
        # Use chat with history if available
        if conversation_history:
            chat = self.model.start_chat(history=[
                {
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": [m["content"]]
                }
                for m in conversation_history
            ])
            response = await asyncio.to_thread(
                chat.send_message,
                full_message
            )
        else:
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_message
            )

        return response.text

    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def _get_mental_health_chat_prompt(self, assessment_data: Optional[Dict] = None) -> str:
    """System prompt cho mental health chat"""
    base_prompt = """Bạn là AI4Mind Assistant - trợ lý AI chuyên về sức khỏe tâm thần cho sinh viên Việt Nam.

VAI TRÒ:
- Lắng nghe và thấu hiểu cảm xúc của sinh viên
- Cung cấp hỗ trợ tâm lý ban đầu (không thay thế bác sĩ)
- Khuyến khích tích cực và động viên tinh thần
- Đề xuất các kỹ thuật self-care phù hợp

NGUYÊN TẮC:
1. Thể hiện sự đồng cảm và tôn trọng
2. KHÔNG chẩn đoán bệnh (không phải bác sĩ)
3. Khuyến khích tìm chuyên gia nếu nghiêm trọng
4. Ngôn ngữ đơn giản, gần gũi, văn hóa Việt Nam
5. Bảo mật tuyệt đối

CẢNH BÁO KHẨN CẤP:
- Ý định tự tử/tự hại → Khuyên gọi hotline 1800545475 NGAY
- Triệu chứng nghiêm trọng → Đề xuất gặp counselor

PHONG CÁCH:
- Thân thiện, ấm áp như bạn bè
- Câu ngắn, dễ hiểu
- Emoji nhẹ nhàng 😊

"""

    if assessment_data:
        severity = assessment_data.get('severity', '')
        if severity == 'severe':
            base_prompt += """
[LƯU Ý ĐẶC BIỆT]
User có mức độ lo âu cao. Cần:
- Đặc biệt chú ý đến cảm xúc
- Khuyến khích gặp chuyên gia mạnh mẽ hơn
- Theo dõi dấu hiệu nguy hiểm
"""

    return base_prompt
```

---

### 5. API Endpoints (ai-service/app/api/v1/endpoints/ai_chat.py)

```python
"""
AI Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.schemas.ai_chat import (
    MessageCreate, MessageResponse, ConversationResponse, ChatResponse
)
from app.services.ai_chat_service import AIChatService
from app.models.user import User

router = APIRouter()


@router.get("/conversation", response_model=ConversationResponse)
async def get_active_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy hoặc tạo active conversation cho student
    Endpoint này được gọi khi user mở chat page
    """
    if not current_user.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access chat"
        )

    chat_service = AIChatService(db)
    conversation = chat_service.get_or_create_active_conversation(
        student_id=current_user.student.id
    )

    return conversation


@router.get("/conversation/messages", response_model=List[MessageResponse])
async def get_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả messages trong active conversation
    """
    if not current_user.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access messages"
        )

    chat_service = AIChatService(db)

    # Get active conversation
    conversation = chat_service.get_or_create_active_conversation(
        student_id=current_user.student.id
    )

    # Get messages
    messages = chat_service.get_conversation_messages(
        conversation_id=conversation.id,
        student_id=current_user.student.id
    )

    return messages


@router.post("/message", response_model=ChatResponse)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi message và nhận response từ AI

    Flow:
    1. Save user message
    2. Load context (assessment + recent messages)
    3. Call Gemini
    4. Save AI response
    5. Return both messages
    """
    if not current_user.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can send messages"
        )

    chat_service = AIChatService(db)

    try:
        result = await chat_service.send_message(
            student_id=current_user.student.id,
            message_content=data.content
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử conversations (cho archive/history page - optional)
    """
    if not current_user.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access conversation history"
        )

    chat_service = AIChatService(db)
    conversations = chat_service.get_student_conversations(
        student_id=current_user.student.id
    )

    return conversations


@router.post("/conversation/end")
async def end_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kết thúc conversation hiện tại (set is_active = False)
    User có thể start new conversation sau đó
    """
    if not current_user.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can end conversation"
        )

    chat_service = AIChatService(db)
    conversation = chat_service.get_or_create_active_conversation(
        student_id=current_user.student.id
    )

    conversation.is_active = False
    db.commit()

    return {"message": "Conversation ended successfully"}
```

---

## 💻 FRONTEND IMPLEMENTATION

### 1. Service (frontend/src/services/aiChatService.ts)

```typescript
import api from "./api";

export interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  is_active: boolean;
  created_at: string;
  last_message_at: string;
  latest_assessment_id: number | null;
}

export interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  ai_message: Message;
  assessment_summary?: {
    id: number;
    score: number;
    severity: string;
    date: string;
  };
}

export const aiChatService = {
  /**
   * Get or create active conversation
   * Call this when user opens chat page
   */
  getActiveConversation: async (): Promise<Conversation> => {
    const response = await api.get("/api/v1/ai-chat/conversation");
    return response.data;
  },

  /**
   * Get all messages in active conversation
   */
  getMessages: async (): Promise<Message[]> => {
    const response = await api.get("/api/v1/ai-chat/conversation/messages");
    return response.data;
  },

  /**
   * Send message and get AI response
   */
  sendMessage: async (content: string): Promise<ChatResponse> => {
    const response = await api.post("/api/v1/ai-chat/message", { content });
    return response.data;
  },

  /**
   * End current conversation
   */
  endConversation: async (): Promise<void> => {
    await api.post("/api/v1/ai-chat/conversation/end");
  },
};
```

---

### 2. Chat Page (frontend/src/pages/AIChatPage/AIChatPage.tsx)

```typescript
import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
  Container,
  AppBar,
  Toolbar,
  Avatar,
  Chip,
} from "@mui/material";
import {
  Send as SendIcon,
  ArrowBack,
  SmartToy,
  Person,
  MoreVert,
} from "@mui/icons-material";
import {
  aiChatService,
  Message,
  Conversation,
} from "../../services/aiChatService";
import MainLayout from "../../components/layout/MainLayout";
import "./AIChatPage.css";

const AIChatPage: React.FC = () => {
  const navigate = useNavigate();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    initializeChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = async () => {
    try {
      // Step 1: Get or create conversation
      const conv = await aiChatService.getActiveConversation();
      setConversation(conv);

      // Step 2: Load messages
      const msgs = await aiChatService.getMessages();
      setMessages(msgs);
    } catch (error) {
      console.error("Failed to initialize chat:", error);
      alert("Không thể tải chat. Vui lòng thử lại.");
    } finally {
      setInitialLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setLoading(true);

    try {
      const response = await aiChatService.sendMessage(userMessage);

      // Add both user message and AI response
      setMessages((prev) => [
        ...prev,
        response.user_message,
        response.ai_message,
      ]);
    } catch (error) {
      console.error("Failed to send message:", error);
      alert("Không thể gửi tin nhắn. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (initialLoading) {
    return (
      <MainLayout>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="80vh"
        >
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Box
        sx={{
          height: "calc(100vh - 100px)",
          display: "flex",
          flexDirection: "column",
          bgcolor: "#f5f5f5",
        }}
      >
        {/* Header */}
        <AppBar position="static" elevation={1} sx={{ bgcolor: "white" }}>
          <Toolbar>
            <IconButton edge="start" onClick={() => navigate("/dashboard")}>
              <ArrowBack />
            </IconButton>
            <Avatar sx={{ bgcolor: "primary.main", ml: 2, mr: 1 }}>
              <SmartToy />
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" color="text.primary">
                AI4Mind Assistant
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Luôn sẵn sàng hỗ trợ bạn
              </Typography>
            </Box>
            <IconButton>
              <MoreVert />
            </IconButton>
          </Toolbar>
        </AppBar>

        {/* Messages Area */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: "auto",
            p: 2,
            bgcolor: "#e5ddd5", // WhatsApp-like background
          }}
        >
          {messages.length === 0 && !loading && (
            <Box textAlign="center" py={8}>
              <SmartToy sx={{ fontSize: 80, color: "primary.main", mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Xin chào! Tôi là AI4Mind Assistant 👋
              </Typography>
              <Typography color="text.secondary">
                Bạn có thể chia sẻ bất cứ điều gì với tôi.
                <br />
                Tôi ở đây để lắng nghe và hỗ trợ bạn.
              </Typography>
            </Box>
          )}

          {messages.map((message) => {
            const isUser = message.role === "user";
            return (
              <Box
                key={message.id}
                sx={{
                  display: "flex",
                  justifyContent: isUser ? "flex-end" : "flex-start",
                  mb: 1,
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    maxWidth: "70%",
                    p: 1.5,
                    bgcolor: isUser ? "#dcf8c6" : "white",
                    borderRadius: 2,
                    position: "relative",
                  }}
                >
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {message.content}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      display: "block",
                      mt: 0.5,
                      textAlign: "right",
                      color: "text.secondary",
                    }}
                  >
                    {new Date(message.created_at).toLocaleTimeString("vi-VN", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </Typography>
                </Paper>
              </Box>
            );
          })}

          {loading && (
            <Box display="flex" justifyContent="flex-start" mb={1}>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  bgcolor: "white",
                  borderRadius: 2,
                }}
              >
                <Box display="flex" gap={0.5}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      bgcolor: "grey.400",
                      animation: "pulse 1.4s infinite ease-in-out",
                    }}
                  />
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      bgcolor: "grey.400",
                      animation: "pulse 1.4s infinite ease-in-out 0.2s",
                    }}
                  />
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      bgcolor: "grey.400",
                      animation: "pulse 1.4s infinite ease-in-out 0.4s",
                    }}
                  />
                </Box>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Paper
          elevation={3}
          sx={{
            p: 1.5,
            borderTop: "1px solid",
            borderColor: "divider",
          }}
        >
          <Box display="flex" gap={1} alignItems="flex-end">
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Nhập tin nhắn..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              variant="outlined"
              size="small"
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                },
              }}
            />
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || loading}
              sx={{
                bgcolor: "primary.main",
                color: "white",
                "&:hover": {
                  bgcolor: "primary.dark",
                },
                "&:disabled": {
                  bgcolor: "grey.300",
                },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Box>

      {/* CSS for typing animation */}
      <style>{`
        @keyframes pulse {
          0%, 60%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
          }
          30% {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </MainLayout>
  );
};

export default AIChatPage;
```

---

### 3. Update Dashboard (frontend/src/pages/DashboardPage/DashboardPage.tsx)

```typescript
// Add navigation to AI Chat
<button className="feature-card" onClick={() => navigate("/ai-chat")}>
  <div className="feature-icon">
    <SmartToy sx={{ fontSize: 48 }} />
  </div>
  <h3 className="feature-label">Trò chuyện với AI</h3>
</button>
```

---

### 4. Update Routes (frontend/src/App.tsx)

```typescript
import AIChatPage from "./pages/AIChatPage";

// Add route
<Route
  path="/ai-chat"
  element={
    <ProtectedRoute>
      <AIChatPage />
    </ProtectedRoute>
  }
/>;
```

---

## 🗄️ DATABASE MIGRATION

```python
"""Add AI chat tables

Revision ID: add_ai_chat
Create Date: 2025-10-05
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # AI Conversations
    op.create_table(
        'ai_conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('latest_assessment_id', sa.Integer(), sa.ForeignKey('assessments.id'), nullable=True),
        sa.Column('title', sa.String(255), default='Chat với AI'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_message_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # AI Messages
    op.create_table(
        'ai_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('ai_conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('related_assessment_id', sa.Integer(), sa.ForeignKey('assessments.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Indexes
    op.create_index('idx_ai_messages_conversation', 'ai_messages', ['conversation_id', 'created_at'])
    op.create_index('idx_ai_conversations_student', 'ai_conversations', ['student_id', 'last_message_at'])

def downgrade():
    op.drop_table('ai_messages')
    op.drop_table('ai_conversations')
```

---

## 🚀 IMPLEMENTATION CHECKLIST

### Backend:

- [ ] Create models (ai_chat.py)
- [ ] Create schemas (ai_chat.py)
- [ ] Create service (ai_chat_service.py)
- [ ] Update GeminiService
- [ ] Create API endpoints
- [ ] Create migration
- [ ] Run migration
- [ ] Update API router

### Frontend:

- [ ] Create service (aiChatService.ts)
- [ ] Create AIChatPage component
- [ ] Update Dashboard navigation
- [ ] Update App routes
- [ ] Test flow end-to-end

### Testing:

- [ ] Test create conversation
- [ ] Test send message
- [ ] Test with assessment context
- [ ] Test without assessment
- [ ] Test message history loading
- [ ] Test mobile responsive

---

## 📊 SUCCESS METRICS

- [ ] Chat loads in < 2s
- [ ] AI response in < 5s
- [ ] Message history correct
- [ ] Assessment context working
- [ ] Mobile UI good
- [ ] No crashes

---

_Design completed: October 5, 2025_
_Ready for implementation!_ 🚀
