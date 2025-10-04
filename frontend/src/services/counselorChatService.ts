/**
 * Counselor Chat Service - API client for counselor messaging
 * Direct messaging between students and counselors (human-to-human)
 */
import api from "./api";
import {
  Counselor,
  CounselorConversation,
  CounselorMessage,
  ConversationDetail,
  CreateConversationRequest,
  CreateConversationResponse,
  SendMessageRequest,
  SendMessageResponse,
  MarkAllReadResponse,
} from "../types/counselorChat";

/**
 * Get danh sách counselors đang available
 * Chỉ students mới access endpoint này
 */
export const listAvailableCounselors = async (): Promise<Counselor[]> => {
  const response = await api.get<Counselor[]>(
    "/api/v1/counselor-chat/counselors"
  );
  return response.data;
};

/**
 * Tạo conversation mới với counselor
 * Nếu đã tồn tại conversation, trả về existing conversation
 */
export const createConversation = async (
  counselorId: number
): Promise<CreateConversationResponse> => {
  const response = await api.post<CreateConversationResponse>(
    "/api/v1/counselor-chat/conversations",
    { counselor_id: counselorId } as CreateConversationRequest
  );
  return response.data;
};

/**
 * Get chi tiết conversation với counselor info và messages
 */
export const getConversationDetail = async (
  conversationId: number
): Promise<ConversationDetail> => {
  const response = await api.get<ConversationDetail>(
    `/api/v1/counselor-chat/conversations/${conversationId}`
  );
  return response.data;
};

/**
 * Get all conversations của current user (student)
 */
export const listMyConversations = async (): Promise<
  CounselorConversation[]
> => {
  const response = await api.get<CounselorConversation[]>(
    "/api/v1/counselor-chat/conversations"
  );
  return response.data;
};

/**
 * Gửi message trong conversation
 */
export const sendMessage = async (
  conversationId: number,
  content: string
): Promise<SendMessageResponse> => {
  const response = await api.post<SendMessageResponse>(
    `/api/v1/counselor-chat/conversations/${conversationId}/messages`,
    { content } as SendMessageRequest
  );
  return response.data;
};

/**
 * Đánh dấu message đã đọc
 */
export const markMessageAsRead = async (
  messageId: number
): Promise<CounselorMessage> => {
  const response = await api.patch<CounselorMessage>(
    `/api/v1/counselor-chat/messages/${messageId}/read`
  );
  return response.data;
};

/**
 * Đánh dấu tất cả messages trong conversation đã đọc
 */
export const markAllMessagesAsRead = async (
  conversationId: number
): Promise<MarkAllReadResponse> => {
  const response = await api.post<MarkAllReadResponse>(
    `/api/v1/counselor-chat/conversations/${conversationId}/mark-all-read`
  );
  return response.data;
};

/**
 * Helper: Format datetime for display
 */
export const formatMessageTime = (isoDatetime: string): string => {
  const date = new Date(isoDatetime);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInHours = diffInMs / (1000 * 60 * 60);
  const diffInDays = diffInMs / (1000 * 60 * 60 * 24);

  if (diffInHours < 1) {
    const minutes = Math.floor(diffInMs / (1000 * 60));
    return `${minutes} phút trước`;
  } else if (diffInHours < 24) {
    const hours = Math.floor(diffInHours);
    return `${hours} giờ trước`;
  } else if (diffInDays < 7) {
    const days = Math.floor(diffInDays);
    return `${days} ngày trước`;
  } else {
    return date.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  }
};

/**
 * Helper: Format datetime for message timestamp
 */
export const formatMessageTimestamp = (isoDatetime: string): string => {
  const date = new Date(isoDatetime);
  return date.toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });
};
