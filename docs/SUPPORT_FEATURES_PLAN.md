# KẾ HOẠCH TRIỂN KHAI TÍNH NĂNG "TÌM KIẾM HỖ TRỢ"

## 📋 TỔNG QUAN

Tài liệu này mô tả chi tiết kế hoạch triển khai 3 tính năng mới trong module "Tìm kiếm hỗ trợ":

1. **Chat với AI (Chatbot)** - Trò chuyện với AI hỗ trợ tâm lý
2. **Tìm kiếm chuyên gia tâm lý** - Nhắn tin trực tiếp với counselor
3. **Liên hệ trung tâm gần nhất** - Map điều hướng đến bệnh viện/phòng khám

---

## 🏗️ KIẾN TRÚC HIỆN TẠI

### Backend (ai-service)

- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **AI Service**: Google Gemini (đã có GeminiService)
- **Models**: User, Student, Counselor, Conversation, Message

### Frontend

- **Framework**: React 18 + TypeScript
- **UI Library**: Material-UI (MUI)
- **Routing**: React Router v6
- **State Management**: React Query
- **Maps**: Cần thêm (đề xuất: Leaflet hoặc Google Maps)

---

## 🎯 TÍNH NĂNG 1: CHAT VỚI AI (CHATBOT)

### 📐 Thiết kế Database

#### Bảng đã có (tận dụng):

```sql
-- conversations: Đã có trong models/conversation.py
-- messages: Đã có trong models/conversation.py
```

#### Bảng mới cần tạo:

```sql
-- Chat sessions metadata
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    session_type VARCHAR(50) DEFAULT 'general_support', -- general_support, anxiety, depression, stress
    tags TEXT[], -- Các tag để phân loại chat
    sentiment_score FLOAT, -- Điểm cảm xúc tổng thể (phân tích từ AI)
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

-- Feedback từ user về chat
CREATE TABLE chat_feedback (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 🔧 Backend Implementation

#### 1. Models (ai-service/app/models/chat.py)

```python
"""
Chat models - Extended conversation features
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base

class ChatSession(Base):
    """Chat session metadata"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    session_type = Column(String(50), default="general_support")
    tags = Column(ARRAY(String), default=[])
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    conversation = relationship("Conversation", backref="chat_session")

class ChatFeedback(Base):
    """User feedback on chat"""
    __tablename__ = "chat_feedback"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    rating = Column(Integer)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### 2. Schemas (ai-service/app/schemas/chat.py)

```python
"""
Chat schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    session_type: str = "general_support"

class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    is_active: bool
    created_at: datetime
    last_message_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    user_message: MessageResponse
    ai_message: MessageResponse
    conversation_id: int

class ChatFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
```

#### 3. Service (ai-service/app/services/chat_service.py)

```python
"""
Chat Service - Xử lý logic chat với AI
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.models.conversation import Conversation, Message
from app.models.chat import ChatSession, ChatFeedback
from app.services.gemini_service import GeminiService
from datetime import datetime

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.gemini = GeminiService()

    async def create_conversation(self, student_id: int, session_type: str = "general_support") -> Conversation:
        """Tạo conversation mới"""
        conversation = Conversation(
            student_id=student_id,
            title=f"Chat {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            is_active=True,
            last_message_at=datetime.now()
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        # Tạo chat session metadata
        chat_session = ChatSession(
            conversation_id=conversation.id,
            session_type=session_type
        )
        self.db.add(chat_session)
        self.db.commit()

        return conversation

    async def send_message(
        self,
        conversation_id: int,
        user_message: str,
        student_id: int
    ) -> Dict[str, any]:
        """Gửi tin nhắn và nhận phản hồi từ AI"""

        # Verify conversation belongs to student
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.student_id == student_id
        ).first()

        if not conversation:
            raise ValueError("Conversation not found")

        # Lưu user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        self.db.add(user_msg)
        self.db.commit()
        self.db.refresh(user_msg)

        # Lấy lịch sử chat
        history = self._get_conversation_history(conversation_id)

        # Gọi Gemini AI với system prompt cho mental health support
        system_prompt = self._get_mental_health_system_prompt()
        ai_response = await self.gemini.chat(
            message=user_message,
            conversation_history=history,
            system_instruction=system_prompt
        )

        # Lưu AI response
        ai_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )
        self.db.add(ai_msg)

        # Update last_message_at
        conversation.last_message_at = datetime.now()
        self.db.commit()
        self.db.refresh(ai_msg)

        return {
            "user_message": user_msg,
            "ai_message": ai_msg,
            "conversation_id": conversation_id
        }

    def _get_conversation_history(self, conversation_id: int, limit: int = 10) -> List[Dict]:
        """Lấy lịch sử conversation"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    def _get_mental_health_system_prompt(self) -> str:
        """System prompt cho AI mental health support"""
        return """
Bạn là AI4Mind Assistant - trợ lý AI chuyên về sức khỏe tâm thần cho sinh viên Việt Nam.

VAI TRÒ:
- Lắng nghe và thấu hiểu cảm xúc của sinh viên
- Cung cấp hỗ trợ tâm lý ban đầu (first-line support)
- Khuyến khích tích cực và động viên tinh thần
- Đề xuất các kỹ thuật self-care đơn giản

NGUYÊN TẮC:
1. Luôn thể hiện sự đồng cảm và tôn trọng
2. KHÔNG chẩn đoán bệnh lý tâm thần (không phải bác sĩ)
3. KHUYẾN KHÍCH tìm kiếm chuyên gia nếu vấn đề nghiêm trọng
4. Sử dụng ngôn ngữ đơn giản, gần gũi, phù hợp văn hóa Việt Nam
5. Giữ bí mật và tôn trọng quyền riêng tư

CẢNH BÁO:
- Nếu phát hiện ý định tự tử/tự hại: NGAY LẬP TỨC khuyên gọi hotline 1800545475
- Nếu triệu chứng nghiêm trọng: Đề xuất gặp counselor hoặc bác sĩ tâm thần

PHONG CÁCH:
- Thân thiện, ấm áp
- Câu văn ngắn gọn, dễ hiểu
- Sử dụng emoji phù hợp (nhẹ nhàng)
"""

    def get_conversations(self, student_id: int, limit: int = 20) -> List[Conversation]:
        """Lấy danh sách conversations của student"""
        return self.db.query(Conversation).filter(
            Conversation.student_id == student_id
        ).order_by(Conversation.last_message_at.desc()).limit(limit).all()

    def get_messages(self, conversation_id: int, student_id: int) -> List[Message]:
        """Lấy tất cả messages trong conversation"""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.student_id == student_id
        ).first()

        if not conversation:
            raise ValueError("Conversation not found")

        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()

    async def save_feedback(
        self,
        conversation_id: int,
        student_id: int,
        rating: int,
        feedback_text: Optional[str] = None
    ):
        """Lưu feedback từ user"""
        feedback = ChatFeedback(
            conversation_id=conversation_id,
            student_id=student_id,
            rating=rating,
            feedback_text=feedback_text
        )
        self.db.add(feedback)
        self.db.commit()
```

#### 4. API Endpoints (ai-service/app/api/v1/endpoints/chat.py)

```python
"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.schemas.chat import (
    MessageCreate, MessageResponse, ConversationCreate,
    ConversationResponse, ChatResponse, ChatFeedbackCreate
)
from app.services.chat_service import ChatService
from app.models.user import User

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo conversation mới"""
    if not current_user.student:
        raise HTTPException(status_code=403, detail="Only students can create conversations")

    chat_service = ChatService(db)
    conversation = await chat_service.create_conversation(
        student_id=current_user.student.id,
        session_type=data.session_type
    )
    return conversation

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách conversations"""
    if not current_user.student:
        raise HTTPException(status_code=403, detail="Only students can access conversations")

    chat_service = ChatService(db)
    return chat_service.get_conversations(current_user.student.id)

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy tất cả messages trong conversation"""
    if not current_user.student:
        raise HTTPException(status_code=403, detail="Only students can access messages")

    chat_service = ChatService(db)
    try:
        return chat_service.get_messages(conversation_id, current_user.student.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gửi message và nhận response từ AI"""
    if not current_user.student:
        raise HTTPException(status_code=403, detail="Only students can send messages")

    chat_service = ChatService(db)
    try:
        result = await chat_service.send_message(
            conversation_id=conversation_id,
            user_message=data.content,
            student_id=current_user.student.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.post("/conversations/{conversation_id}/feedback")
async def submit_feedback(
    conversation_id: int,
    data: ChatFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback về chat conversation"""
    if not current_user.student:
        raise HTTPException(status_code=403, detail="Only students can submit feedback")

    chat_service = ChatService(db)
    await chat_service.save_feedback(
        conversation_id=conversation_id,
        student_id=current_user.student.id,
        rating=data.rating,
        feedback_text=data.feedback_text
    )
    return {"message": "Feedback saved successfully"}
```

### 💻 Frontend Implementation

#### 1. Service (frontend/src/services/chatService.ts)

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
  title: string | null;
  is_active: boolean;
  created_at: string;
  last_message_at: string | null;
}

export interface ChatResponse {
  user_message: Message;
  ai_message: Message;
  conversation_id: number;
}

export const chatService = {
  // Tạo conversation mới
  createConversation: async (
    sessionType: string = "general_support"
  ): Promise<Conversation> => {
    const response = await api.post("/api/v1/chat/conversations", {
      session_type: sessionType,
    });
    return response.data;
  },

  // Lấy danh sách conversations
  getConversations: async (): Promise<Conversation[]> => {
    const response = await api.get("/api/v1/chat/conversations");
    return response.data;
  },

  // Lấy messages trong conversation
  getMessages: async (conversationId: number): Promise<Message[]> => {
    const response = await api.get(
      `/api/v1/chat/conversations/${conversationId}/messages`
    );
    return response.data;
  },

  // Gửi message
  sendMessage: async (
    conversationId: number,
    content: string
  ): Promise<ChatResponse> => {
    const response = await api.post(
      `/api/v1/chat/conversations/${conversationId}/messages`,
      { content }
    );
    return response.data;
  },

  // Submit feedback
  submitFeedback: async (
    conversationId: number,
    rating: number,
    feedback?: string
  ): Promise<void> => {
    await api.post(`/api/v1/chat/conversations/${conversationId}/feedback`, {
      rating,
      feedback_text: feedback,
    });
  },
};
```

#### 2. Chat Page Component (frontend/src/pages/AIChatPage/AIChatPage.tsx)

```typescript
import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
  List,
  ListItem,
  Avatar,
  Container,
  AppBar,
  Toolbar,
  Fab,
} from "@mui/material";
import {
  Send as SendIcon,
  ArrowBack,
  SmartToy,
  Person,
} from "@mui/icons-material";
import { chatService, Message } from "../../services/chatService";
import MainLayout from "../../components/layout/MainLayout";

const AIChatPage: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Load messages khi vào conversation
  useEffect(() => {
    if (conversationId) {
      loadMessages();
    }
  }, [conversationId]);

  // Auto scroll to bottom khi có message mới
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const data = await chatService.getMessages(Number(conversationId));
      setMessages(data);
    } catch (error) {
      console.error("Failed to load messages:", error);
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
      const response = await chatService.sendMessage(
        Number(conversationId),
        userMessage
      );

      // Update messages với cả user message và AI response
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
      <Container
        maxWidth="md"
        sx={{
          height: "calc(100vh - 100px)",
          display: "flex",
          flexDirection: "column",
          py: 2,
        }}
      >
        {/* Header */}
        <AppBar
          position="static"
          color="transparent"
          elevation={0}
          sx={{ mb: 2 }}
        >
          <Toolbar sx={{ px: 0 }}>
            <IconButton edge="start" onClick={() => navigate("/support")}>
              <ArrowBack />
            </IconButton>
            <SmartToy sx={{ mx: 1, color: "primary.main" }} />
            <Typography variant="h6">AI4Mind Assistant</Typography>
          </Toolbar>
        </AppBar>

        {/* Messages List */}
        <Paper
          elevation={2}
          sx={{
            flexGrow: 1,
            overflow: "auto",
            p: 2,
            mb: 2,
            bgcolor: "#f5f5f5",
          }}
        >
          <List>
            {messages.length === 0 && (
              <Box textAlign="center" py={4}>
                <SmartToy sx={{ fontSize: 60, color: "primary.main", mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Xin chào! Tôi là AI4Mind Assistant 👋
                </Typography>
                <Typography color="text.secondary">
                  Bạn có thể chia sẻ những gì bạn đang cảm thấy hoặc băn khoăn.
                  <br />
                  Tôi ở đây để lắng nghe bạn.
                </Typography>
              </Box>
            )}

            {messages.map((message) => (
              <ListItem
                key={message.id}
                sx={{
                  display: "flex",
                  justifyContent:
                    message.role === "user" ? "flex-end" : "flex-start",
                  mb: 2,
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    flexDirection:
                      message.role === "user" ? "row-reverse" : "row",
                    alignItems: "flex-start",
                    maxWidth: "80%",
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor:
                        message.role === "user"
                          ? "primary.main"
                          : "secondary.main",
                      mx: 1,
                    }}
                  >
                    {message.role === "user" ? <Person /> : <SmartToy />}
                  </Avatar>
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      bgcolor:
                        message.role === "user" ? "primary.light" : "white",
                      color: message.role === "user" ? "white" : "text.primary",
                    }}
                  >
                    <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                      {message.content}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ opacity: 0.7, display: "block", mt: 1 }}
                    >
                      {new Date(message.created_at).toLocaleTimeString("vi-VN")}
                    </Typography>
                  </Paper>
                </Box>
              </ListItem>
            ))}

            {loading && (
              <ListItem sx={{ justifyContent: "flex-start" }}>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Avatar sx={{ bgcolor: "secondary.main", mr: 1 }}>
                    <SmartToy />
                  </Avatar>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <CircularProgress size={20} />
                  </Paper>
                </Box>
              </ListItem>
            )}

            <div ref={messagesEndRef} />
          </List>
        </Paper>

        {/* Input Field */}
        <Paper elevation={3} sx={{ p: 2 }}>
          <Box display="flex" gap={1}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Nhập tin nhắn của bạn..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || loading}
              sx={{ alignSelf: "flex-end" }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Container>
    </MainLayout>
  );
};

export default AIChatPage;
```

#### 3. Support Hub Page (frontend/src/pages/SupportPage/SupportPage.tsx)

```typescript
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
} from "@mui/material";
import { SmartToy, Psychology, LocalHospital } from "@mui/icons-material";
import MainLayout from "../../components/layout/MainLayout";
import { chatService } from "../../services/chatService";

const SupportPage: React.FC = () => {
  const navigate = useNavigate();

  const handleStartAIChat = async () => {
    try {
      // Tạo conversation mới và navigate
      const conversation = await chatService.createConversation(
        "general_support"
      );
      navigate(`/support/ai-chat/${conversation.id}`);
    } catch (error) {
      console.error("Failed to create conversation:", error);
      alert("Không thể tạo cuộc trò chuyện. Vui lòng thử lại.");
    }
  };

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom align="center" sx={{ mb: 4 }}>
          Tìm kiếm hỗ trợ sức khỏe tinh thần
        </Typography>

        <Grid container spacing={3}>
          {/* AI Chat */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                height: "100%",
                cursor: "pointer",
                "&:hover": { boxShadow: 6 },
              }}
            >
              <CardContent sx={{ textAlign: "center", py: 4 }}>
                <SmartToy sx={{ fontSize: 60, color: "primary.main", mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  Trò chuyện với AI
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  Chia sẻ cảm xúc và nhận hỗ trợ từ AI4Mind Assistant
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleStartAIChat}
                >
                  Bắt đầu trò chuyện
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Counselor */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                height: "100%",
                cursor: "pointer",
                "&:hover": { boxShadow: 6 },
              }}
            >
              <CardContent sx={{ textAlign: "center", py: 4 }}>
                <Psychology
                  sx={{ fontSize: 60, color: "secondary.main", mb: 2 }}
                />
                <Typography variant="h5" gutterBottom>
                  Tìm kiếm chuyên gia
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  Kết nối với chuyên gia tâm lý chuyên nghiệp
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  color="secondary"
                  onClick={() => navigate("/support/counselor")}
                >
                  Tìm chuyên gia
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Medical Center */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                height: "100%",
                cursor: "pointer",
                "&:hover": { boxShadow: 6 },
              }}
            >
              <CardContent sx={{ textAlign: "center", py: 4 }}>
                <LocalHospital
                  sx={{ fontSize: 60, color: "error.main", mb: 2 }}
                />
                <Typography variant="h5" gutterBottom>
                  Trung tâm gần nhất
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  Tìm bệnh viện và phòng khám gần bạn
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  color="error"
                  onClick={() => navigate("/support/medical-center")}
                >
                  Xem bản đồ
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </MainLayout>
  );
};

export default SupportPage;
```

---

## 🎯 TÍNH NĂNG 2: TÌM KIẾM CHUYÊN GIA TÂM LÝ

### 📐 Thiết kế Database

```sql
-- Messaging giữa student và counselor
CREATE TABLE counselor_messages (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    counselor_id INTEGER REFERENCES counselors(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL, -- 'student' or 'counselor'
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversation thread
CREATE TABLE counselor_conversations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    counselor_id INTEGER REFERENCES counselors(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active', -- active, closed, archived
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_counselor_messages_conv ON counselor_messages(student_id, counselor_id);
CREATE INDEX idx_counselor_messages_created ON counselor_messages(created_at DESC);
```

### 🔧 Backend Implementation

#### 1. Models (ai-service/app/models/counselor_chat.py)

```python
"""
Counselor Chat models - Messaging between students and counselors
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base

class CounselorConversation(Base):
    """Conversation thread between student and counselor"""
    __tablename__ = "counselor_conversations"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    counselor_id = Column(Integer, ForeignKey("counselors.id", ondelete="CASCADE"))
    status = Column(String(50), default="active")
    last_message_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    counselor = relationship("Counselor")
    messages = relationship("CounselorMessage", back_populates="conversation", cascade="all, delete-orphan")

class CounselorMessage(Base):
    """Messages between student and counselor"""
    __tablename__ = "counselor_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("counselor_conversations.id", ondelete="CASCADE"))
    sender_type = Column(String(20), nullable=False)  # 'student' or 'counselor'
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("CounselorConversation", back_populates="messages")
```

#### 2. Service (ai-service/app/services/counselor_chat_service.py)

```python
"""
Counselor Chat Service - Messaging với counselors
"""
from sqlalchemy.orm import Session
from typing import List
from app.models.counselor_chat import CounselorConversation, CounselorMessage
from app.models.counselor import Counselor
from datetime import datetime

class CounselorChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_available_counselors(self) -> List[Counselor]:
        """Lấy danh sách counselors có sẵn"""
        return self.db.query(Counselor).filter(
            Counselor.is_available == True
        ).all()

    def create_conversation(self, student_id: int, counselor_id: int) -> CounselorConversation:
        """Tạo conversation mới hoặc lấy conversation hiện có"""
        # Check existing conversation
        existing = self.db.query(CounselorConversation).filter(
            CounselorConversation.student_id == student_id,
            CounselorConversation.counselor_id == counselor_id,
            CounselorConversation.status == "active"
        ).first()

        if existing:
            return existing

        # Create new
        conversation = CounselorConversation(
            student_id=student_id,
            counselor_id=counselor_id,
            last_message_at=datetime.now()
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def send_message(
        self,
        conversation_id: int,
        content: str,
        sender_type: str,
        user_id: int
    ) -> CounselorMessage:
        """Gửi message"""
        # Verify permission
        conversation = self.db.query(CounselorConversation).filter(
            CounselorConversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError("Conversation not found")

        # Verify sender
        if sender_type == "student" and conversation.student_id != user_id:
            raise ValueError("Unauthorized")
        elif sender_type == "counselor" and conversation.counselor_id != user_id:
            raise ValueError("Unauthorized")

        # Create message
        message = CounselorMessage(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content
        )
        self.db.add(message)

        # Update last_message_at
        conversation.last_message_at = datetime.now()
        self.db.commit()
        self.db.refresh(message)

        return message
```

#### 3. API Endpoints (ai-service/app/api/v1/endpoints/counselor_chat.py)

```python
"""
Counselor Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.services.counselor_chat_service import CounselorChatService
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/counselors")
async def get_available_counselors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách counselors available"""
    service = CounselorChatService(db)
    counselors = service.get_available_counselors()

    return [
        {
            "id": c.id,
            "name": c.user.full_name,
            "specialization": c.specialization,
            "years_of_experience": c.years_of_experience,
            "bio": c.bio
        }
        for c in counselors
    ]

@router.post("/conversations")
async def create_conversation(
    counselor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo conversation với counselor"""
    if not current_user.student:
        raise HTTPException(status_code=403, detail="Only students can create conversations")

    service = CounselorChatService(db)
    conversation = service.create_conversation(
        student_id=current_user.student.id,
        counselor_id=counselor_id
    )
    return conversation

# ... thêm các endpoints send_message, get_messages, etc.
```

### 💻 Frontend Implementation

Tương tự AIChatPage nhưng với:

- List counselors để chọn
- UI khác biệt (không có AI avatar)
- Real-time updates (optional: WebSocket)

---

## 🎯 TÍNH NĂNG 3: LIÊN HỆ TRUNG TÂM GẦN NHẤT

### 📐 Thiết kế Database

```sql
-- Medical centers/hospitals database
CREATE TABLE medical_centers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100),
    district VARCHAR(100),
    phone VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    type VARCHAR(50), -- hospital, clinic, counseling_center
    specialties TEXT[], -- Array of specialties
    website VARCHAR(255),
    opening_hours TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_medical_centers_location ON medical_centers(latitude, longitude);
CREATE INDEX idx_medical_centers_city ON medical_centers(city);
```

### 🔧 Backend Implementation

#### 1. Service (ai-service/app/services/medical_center_service.py)

```python
"""
Medical Center Service - Tìm kiếm trung tâm y tế
"""
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.medical_center import MedicalCenter
import math

class MedicalCenterService:
    def __init__(self, db: Session):
        self.db = db

    def find_nearby_centers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10
    ) -> List[Dict]:
        """Tìm medical centers gần vị trí user (trong bán kính radius_km)"""
        # Haversine formula để tính khoảng cách
        centers = self.db.query(MedicalCenter).all()

        nearby = []
        for center in centers:
            if center.latitude and center.longitude:
                distance = self._calculate_distance(
                    latitude, longitude,
                    float(center.latitude), float(center.longitude)
                )
                if distance <= radius_km:
                    nearby.append({
                        **center.__dict__,
                        "distance_km": round(distance, 2)
                    })

        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Tính khoảng cách giữa 2 điểm (Haversine formula)"""
        R = 6371  # Earth radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
```

#### 2. API Endpoints (ai-service/app/api/v1/endpoints/medical_centers.py)

```python
"""
Medical Centers API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.services.medical_center_service import MedicalCenterService

router = APIRouter()

@router.get("/nearby")
async def find_nearby_centers(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius: float = Query(10, description="Search radius in km"),
    db: Session = Depends(get_db)
):
    """Tìm medical centers gần vị trí user"""
    service = MedicalCenterService(db)
    centers = service.find_nearby_centers(latitude, longitude, radius)
    return centers
```

### 💻 Frontend Implementation

#### 1. Cài đặt Leaflet

```bash
npm install leaflet react-leaflet
npm install @types/leaflet --save-dev
```

#### 2. Medical Center Map Page (frontend/src/pages/MedicalCenterPage/MedicalCenterPage.tsx)

```typescript
import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import {
  Container,
  Box,
  Typography,
  List,
  ListItem,
  Card,
} from "@mui/material";
import MainLayout from "../../components/layout/MainLayout";
import "leaflet/dist/leaflet.css";

interface MedicalCenter {
  id: number;
  name: string;
  address: string;
  phone: string;
  latitude: number;
  longitude: number;
  distance_km: number;
}

const MedicalCenterPage: React.FC = () => {
  const [userLocation, setUserLocation] = useState<[number, number] | null>(
    null
  );
  const [centers, setCenters] = useState<MedicalCenter[]>([]);

  useEffect(() => {
    // Get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords: [number, number] = [
            position.coords.latitude,
            position.coords.longitude,
          ];
          setUserLocation(coords);
          loadNearbyCenters(coords[0], coords[1]);
        },
        (error) => {
          console.error("Error getting location:", error);
          // Default to Hanoi
          setUserLocation([21.0285, 105.8542]);
          loadNearbyCenters(21.0285, 105.8542);
        }
      );
    }
  }, []);

  const loadNearbyCenters = async (lat: number, lng: number) => {
    try {
      const response = await fetch(
        `/api/v1/medical-centers/nearby?latitude=${lat}&longitude=${lng}&radius=10`
      );
      const data = await response.json();
      setCenters(data);
    } catch (error) {
      console.error("Failed to load centers:", error);
    }
  };

  if (!userLocation) {
    return (
      <MainLayout>
        <Box>Đang tải bản đồ...</Box>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Trung tâm y tế gần bạn
        </Typography>

        <Box sx={{ height: "500px", mb: 3 }}>
          <MapContainer
            center={userLocation}
            zoom={13}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
            />

            {/* User location marker */}
            <Marker position={userLocation}>
              <Popup>Vị trí của bạn</Popup>
            </Marker>

            {/* Medical center markers */}
            {centers.map((center) => (
              <Marker
                key={center.id}
                position={[center.latitude, center.longitude]}
              >
                <Popup>
                  <strong>{center.name}</strong>
                  <br />
                  {center.address}
                  <br />
                  SĐT: {center.phone}
                  <br />
                  Khoảng cách: {center.distance_km} km
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </Box>

        {/* List of nearby centers */}
        <Typography variant="h6" gutterBottom>
          Danh sách trung tâm ({centers.length})
        </Typography>
        <List>
          {centers.map((center) => (
            <ListItem key={center.id}>
              <Card sx={{ width: "100%", p: 2 }}>
                <Typography variant="h6">{center.name}</Typography>
                <Typography variant="body2">{center.address}</Typography>
                <Typography variant="body2">SĐT: {center.phone}</Typography>
                <Typography variant="body2" color="primary">
                  Cách bạn {center.distance_km} km
                </Typography>
              </Card>
            </ListItem>
          ))}
        </List>
      </Container>
    </MainLayout>
  );
};

export default MedicalCenterPage;
```

---

## 📝 DATABASE MIGRATION

### Alembic Migration Script

```python
"""Add support features tables

Revision ID: xxx
Create Date: 2025-01-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Chat sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id', ondelete='CASCADE')),
        sa.Column('session_type', sa.String(50), default='general_support'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Chat feedback
    op.create_table(
        'chat_feedback',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id', ondelete='CASCADE')),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE')),
        sa.Column('rating', sa.Integer()),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Counselor conversations
    op.create_table(
        'counselor_conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE')),
        sa.Column('counselor_id', sa.Integer(), sa.ForeignKey('counselors.id', ondelete='CASCADE')),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('last_message_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Counselor messages
    op.create_table(
        'counselor_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('counselor_conversations.id', ondelete='CASCADE')),
        sa.Column('sender_type', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Medical centers
    op.create_table(
        'medical_centers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100)),
        sa.Column('district', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('latitude', sa.Numeric(10, 8)),
        sa.Column('longitude', sa.Numeric(11, 8)),
        sa.Column('type', sa.String(50)),
        sa.Column('specialties', postgresql.ARRAY(sa.String())),
        sa.Column('website', sa.String(255)),
        sa.Column('opening_hours', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Indexes
    op.create_index('idx_counselor_messages_conv', 'counselor_messages', ['student_id', 'counselor_id'])
    op.create_index('idx_counselor_messages_created', 'counselor_messages', ['created_at'])
    op.create_index('idx_medical_centers_location', 'medical_centers', ['latitude', 'longitude'])

def downgrade():
    op.drop_table('medical_centers')
    op.drop_table('counselor_messages')
    op.drop_table('counselor_conversations')
    op.drop_table('chat_feedback')
    op.drop_table('chat_sessions')
```

---

## 🔧 ROUTING SETUP

### Backend (ai-service/app/api/v1/api.py)

```python
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, students, assessments, voice_analysis,
    chat, counselor_chat, medical_centers  # NEW
)

api_router = APIRouter()

# Existing routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(voice_analysis.router, prefix="/voice-analysis", tags=["voice-analysis"])

# NEW Support features
api_router.include_router(chat.router, prefix="/chat", tags=["AI Chat"])
api_router.include_router(counselor_chat.router, prefix="/counselor-chat", tags=["Counselor Chat"])
api_router.include_router(medical_centers.router, prefix="/medical-centers", tags=["Medical Centers"])
```

### Frontend (frontend/src/App.tsx)

```typescript
import SupportPage from './pages/SupportPage';
import AIChatPage from './pages/AIChatPage';
import CounselorChatPage from './pages/CounselorChatPage';
import MedicalCenterPage from './pages/MedicalCenterPage';

// Add routes
<Route path="/support" element={<ProtectedRoute><SupportPage /></ProtectedRoute>} />
<Route path="/support/ai-chat/:conversationId" element={<ProtectedRoute><AIChatPage /></ProtectedRoute>} />
<Route path="/support/counselor" element={<ProtectedRoute><CounselorChatPage /></ProtectedRoute>} />
<Route path="/support/medical-center" element={<ProtectedRoute><MedicalCenterPage /></ProtectedRoute>} />
```

---

## 📊 LỘ TRÌNH TRIỂN KHAI

### Phase 1: AI Chat (2-3 ngày)

1. ✅ Setup database tables (chat_sessions, chat_feedback)
2. ✅ Implement backend: models, services, endpoints
3. ✅ Update GeminiService với system prompt
4. ✅ Frontend: chatService, AIChatPage, SupportPage
5. ✅ Testing và debugging
6. ✅ Deploy

### Phase 2: Counselor Chat (2-3 ngày)

1. ✅ Setup database tables (counselor_conversations, counselor_messages)
2. ✅ Implement backend: models, services, endpoints
3. ✅ Frontend: counselorChatService, CounselorListPage, CounselorChatPage
4. ✅ Testing với real counselor accounts
5. ✅ (Optional) WebSocket for real-time
6. ✅ Deploy

### Phase 3: Medical Center Map (2-3 ngày)

1. ✅ Setup database tables (medical_centers)
2. ✅ Seed database với medical centers data (Hà Nội, TPHCM)
3. ✅ Implement backend: models, services, endpoints
4. ✅ Install Leaflet + setup frontend
5. ✅ MedicalCenterPage với map integration
6. ✅ Testing geolocation
7. ✅ Deploy

### Phase 4: Integration & Polish (1-2 ngày)

1. ✅ End-to-end testing tất cả flows
2. ✅ UI/UX improvements
3. ✅ Performance optimization
4. ✅ Documentation updates
5. ✅ Production deployment

---

## 🔐 BẢO MẬT & QUYỀN HẠN

### Permissions

- **Student**: Có thể chat AI, message counselor, xem map
- **Counselor**: Có thể nhận và trả lời messages từ students
- **Admin**: Quản lý medical centers, xem tất cả conversations

### Data Privacy

- Conversations được encrypt
- Counselors chỉ xem được messages assigned cho họ
- Students có thể delete conversations
- GDPR compliance (right to be forgotten)

---

## 📈 MONITORING & ANALYTICS

### Metrics cần track:

- Số lượng AI chat sessions
- Thời gian response trung bình
- User satisfaction (từ feedback ratings)
- Counselor response time
- Medical center search frequency
- Gemini API usage & costs

---

## 🚀 DEPLOYMENT CHECKLIST

### Environment Variables (.env)

```bash
# Existing
GEMINI_API_KEY=your_key_here

# New (if needed)
GOOGLE_MAPS_API_KEY=your_key_here  # Nếu dùng Google Maps thay vì Leaflet
```

### Dependencies

Backend:

```txt
google-generativeai  # Already have
sqlalchemy[postgresql]  # Already have
```

Frontend:

```json
{
  "leaflet": "^1.9.4",
  "react-leaflet": "^4.2.1",
  "@types/leaflet": "^1.9.8"
}
```

---

## 📞 SUPPORT & MAINTENANCE

### Hotline Emergency

- Tích hợp số hotline 1800545475 trong AI chat
- Hiển thị trong emergency situations
- Auto-suggest khi detect keywords: "tự tử", "không muốn sống", etc.

### Content Moderation

- Implement keyword filtering
- Report abuse feature
- Counselor escalation system

---

## 🎨 UI/UX GUIDELINES

### Design Principles:

1. **Đơn giản, dễ hiểu** - Clear navigation
2. **Thân thiện, ấm áp** - Soft colors, friendly icons
3. **Responsive** - Mobile-first design
4. **Accessibility** - WCAG AA compliance
5. **Fast loading** - Optimize images, lazy load

### Color Scheme (tham khảo Frame 9):

- Primary: `#667eea` (purple-blue)
- Secondary: `#764ba2` (purple)
- Background: `#f5f5f7` (light gray)
- Error/Emergency: `#f44336` (red)

---

## 📝 TESTING STRATEGY

### Unit Tests:

- ChatService methods
- GeminiService với mock responses
- Distance calculation algorithm

### Integration Tests:

- API endpoints với test database
- Frontend components với MSW (Mock Service Worker)

### E2E Tests:

- User flow: Start chat → Send message → Receive response
- Counselor flow: Receive message → Reply
- Map flow: Get location → Load centers → Navigate

---

## 🎯 SUCCESS METRICS

### KPIs:

- **Adoption Rate**: % students using support features
- **Engagement**: Average messages per conversation
- **Satisfaction**: Feedback rating >= 4.0/5.0
- **Response Time**: AI < 3s, Counselor < 15min
- **Retention**: Return usage within 7 days >= 40%

---

## 📚 DOCUMENTATION LINKS

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Leaflet Documentation](https://leafletjs.com/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/) (for real-time)
- [React Leaflet Guide](https://react-leaflet.js.org/)

---

## 🔮 FUTURE ENHANCEMENTS

### Phase 5+ (Optional):

1. **Voice Chat với AI** - Speech-to-text integration
2. **Video Call với Counselor** - WebRTC integration
3. **Group Therapy Sessions** - Multi-user conversations
4. **AI Sentiment Analysis** - Real-time emotion detection
5. **Appointment Booking** - Schedule với counselors/medical centers
6. **Notification System** - Push notifications cho messages
7. **Mobile App** - React Native version

---

_Last Updated: January 4, 2025_
_Version: 1.0_
