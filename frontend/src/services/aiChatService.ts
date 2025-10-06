/**
 * AI Chat Service - API client for AI chat functionality
 */
import api from "./api";

export interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  related_assessment_id?: number;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  last_message_at: string;
  is_active: boolean;
  message_count: number;
  latest_assessment_id?: number;
}

export interface ConversationDetail extends Conversation {
  last_message_preview?: string;
}

export interface AssessmentContext {
  id: number;
  score: number;
  severity: string;
  date: string;
  analysis?: string;
  recommendations?: string[];
}

export interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  ai_message: Message;
  assessment_context?: AssessmentContext;
}

/**
 * Get hoặc tạo active conversation
 */
export const getOrCreateConversation = async (): Promise<Conversation> => {
  const response = await api.get<Conversation>("/api/v1/ai-chat/conversation");
  return response.data;
};

/**
 * Get all messages trong conversation
 */
export const getMessages = async (
  conversationId: number
): Promise<Message[]> => {
  const response = await api.get<Message[]>("/api/v1/ai-chat/messages", {
    params: { conversation_id: conversationId },
  });
  return response.data;
};

/**
 * Send message và nhận AI response
 */
export const sendMessage = async (content: string): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>("/api/v1/ai-chat/message", {
    content,
  });
  return response.data;
};

/**
 * End current conversation
 */
export const endConversation = async (): Promise<void> => {
  await api.post("/api/v1/ai-chat/end-conversation");
};

/**
 * Get conversation history
 */
export const getConversationHistory = async (
  limit: number = 10
): Promise<ConversationDetail[]> => {
  const response = await api.get<ConversationDetail[]>(
    "/api/v1/ai-chat/history",
    {
      params: { limit },
    }
  );
  return response.data;
};
