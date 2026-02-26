/**
 * Counselor Chat Types
 * Direct messaging between students and counselors
 */

export interface Counselor {
  id: number;
  user_id: number;
  full_name: string;
  specialization?: string;
  years_of_experience?: number;
  bio?: string;
  is_available: boolean;
}

export interface CounselorConversation {
  id: number;
  student_id: number;
  counselor_id: number;
  status: "active" | "closed" | "archived";
  last_message_at: string; // ISO datetime
  created_at: string; // ISO datetime
  unread_count?: number;
  student_name?: string;   // populated for counselor view
  counselor_name?: string; // populated for student view
}

export interface CounselorMessage {
  id: number;
  conversation_id: number;
  sender_type: "student" | "counselor";
  content: string;
  is_read: boolean;
  created_at: string; // ISO datetime
}

export interface ConversationDetail {
  conversation: CounselorConversation;
  counselor: Counselor;
  messages: CounselorMessage[];
}

// Request DTOs
export interface CreateConversationRequest {
  counselor_id: number;
}

export interface SendMessageRequest {
  content: string;
}

export interface MarkMessageReadRequest {
  is_read: boolean;
}

// Response DTOs
export interface SendMessageResponse extends CounselorMessage {}

export interface CreateConversationResponse extends CounselorConversation {}

export interface ListCounselorsResponse extends Counselor {}

export interface MarkAllReadResponse {
  success: boolean;
  conversation_id: number;
  marked_count: number;
  message: string;
}
