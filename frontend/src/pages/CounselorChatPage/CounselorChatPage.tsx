/**
 * CounselorChatPage - Messenger-like interface for chatting with counselor
 * Direct messaging between student and counselor (human-to-human)
 */
import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  CircularProgress,
  Chip,
  Alert,
  Container,
  Stack,
  Divider,
  Tooltip,
} from "@mui/material";
import {
  Send as SendIcon,
  Person as PersonIcon,
  ArrowBack as BackIcon,
  Psychology as CounselorIcon,
  CheckCircle as ReadIcon,
  Circle as UnreadIcon,
} from "@mui/icons-material";
import MainLayout from "../../components/layout/MainLayout";
import {
  getConversationDetail,
  sendMessage,
  markAllMessagesAsRead,
  formatMessageTimestamp,
} from "../../services/counselorChatService";
import {
  ConversationDetail,
  CounselorMessage,
} from "../../types/counselorChat";

const CounselorChatPage: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [conversationDetail, setConversationDetail] =
    useState<ConversationDetail | null>(null);
  const [messages, setMessages] = useState<CounselorMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto scroll to bottom khi có message mới
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation detail on mount
  useEffect(() => {
    if (!conversationId) {
      setError("Conversation ID không hợp lệ");
      setLoading(false);
      return;
    }

    loadConversation();
  }, [conversationId]);

  // Mark all messages as read khi vào page
  useEffect(() => {
    if (
      conversationDetail &&
      conversationDetail.conversation.unread_count &&
      conversationDetail.conversation.unread_count > 0
    ) {
      markAllMessagesAsRead(conversationDetail.conversation.id).catch((err) =>
        console.error("Failed to mark messages as read:", err)
      );
    }
  }, [conversationDetail]);

  const loadConversation = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getConversationDetail(Number(conversationId));
      setConversationDetail(data);
      setMessages(data.messages);
    } catch (err: any) {
      console.error("Failed to load conversation:", err);
      setError(
        err.response?.data?.detail ||
          "Không thể tải cuộc trò chuyện. Vui lòng thử lại."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || sending || !conversationId) return;

    const messageContent = inputValue.trim();
    setInputValue("");
    setSending(true);
    setError(null);

    // Optimistic UI update
    const tempMessage: CounselorMessage = {
      id: Date.now(),
      conversation_id: Number(conversationId),
      sender_type: "student",
      content: messageContent,
      is_read: false,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempMessage]);

    try {
      const response = await sendMessage(
        Number(conversationId),
        messageContent
      );

      // Replace temp message với real message từ server
      setMessages((prev) =>
        prev.map((msg) => (msg.id === tempMessage.id ? response : msg))
      );
    } catch (err: any) {
      console.error("Failed to send message:", err);
      setError(
        err.response?.data?.detail ||
          "Không thể gửi tin nhắn. Vui lòng thử lại."
      );

      // Remove temp message nếu gửi fail
      setMessages((prev) => prev.filter((msg) => msg.id !== tempMessage.id));
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getInitials = (fullName: string): string => {
    const parts = fullName.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return fullName.substring(0, 2).toUpperCase();
  };

  const getAvatarColor = (senderType: string): string => {
    return senderType === "counselor" ? "#1976d2" : "#4caf50";
  };

  if (loading) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight="400px"
          >
            <CircularProgress />
          </Box>
        </Container>
      </MainLayout>
    );
  }

  if (error && !conversationDetail) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Box textAlign="center">
            <IconButton onClick={() => navigate("/counselor-list")}>
              <BackIcon />
            </IconButton>
            <Typography variant="body2">
              Quay lại danh sách tư vấn viên
            </Typography>
          </Box>
        </Container>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Container
        maxWidth="lg"
        sx={{
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          py: 2,
        }}
      >
        {/* Header */}
        <Paper elevation={2} sx={{ mb: 2, p: 2 }}>
          <Box display="flex" alignItems="center">
            <IconButton
              onClick={() => navigate("/counselor-list")}
              sx={{ mr: 2 }}
            >
              <BackIcon />
            </IconButton>

            {conversationDetail && (
              <>
                <Avatar
                  sx={{
                    bgcolor: "#1976d2",
                    mr: 2,
                    width: 48,
                    height: 48,
                  }}
                >
                  {getInitials(conversationDetail.counselor.full_name)}
                </Avatar>
                <Box flexGrow={1}>
                  <Typography variant="h6" fontWeight="bold">
                    {conversationDetail.counselor.full_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {conversationDetail.counselor.specialization ||
                      "Tư vấn viên"}
                  </Typography>
                </Box>
                <Chip
                  label="Online"
                  color="success"
                  size="small"
                  sx={{
                    display: conversationDetail.counselor.is_available
                      ? "flex"
                      : "none",
                  }}
                />
              </>
            )}
          </Box>
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Messages Container */}
        <Paper
          elevation={2}
          sx={{
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            mb: 2,
          }}
        >
          {/* Messages List */}
          <Box
            sx={{
              flexGrow: 1,
              overflowY: "auto",
              p: 3,
              backgroundColor: "#f5f5f5",
            }}
          >
            {messages.length === 0 ? (
              <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                height="100%"
              >
                <CounselorIcon
                  sx={{ fontSize: 80, color: "text.disabled", mb: 2 }}
                />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Bắt đầu cuộc trò chuyện
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Gửi tin nhắn đầu tiên để bắt đầu tư vấn với chuyên gia
                </Typography>
              </Box>
            ) : (
              <Stack spacing={2}>
                {messages.map((message) => {
                  const isStudent = message.sender_type === "student";
                  const isRead = message.is_read;

                  return (
                    <Box
                      key={message.id}
                      display="flex"
                      justifyContent={isStudent ? "flex-end" : "flex-start"}
                    >
                      {/* Counselor Avatar */}
                      {!isStudent && conversationDetail && (
                        <Avatar
                          sx={{
                            bgcolor: getAvatarColor(message.sender_type),
                            mr: 1,
                            width: 32,
                            height: 32,
                          }}
                        >
                          {
                            getInitials(
                              conversationDetail.counselor.full_name
                            )[0]
                          }
                        </Avatar>
                      )}

                      {/* Message Bubble */}
                      <Paper
                        elevation={1}
                        sx={{
                          maxWidth: "70%",
                          p: 2,
                          backgroundColor: isStudent ? "#1976d2" : "white",
                          color: isStudent ? "white" : "text.primary",
                          borderRadius: isStudent
                            ? "16px 16px 4px 16px"
                            : "16px 16px 16px 4px",
                        }}
                      >
                        <Typography
                          variant="body1"
                          sx={{ whiteSpace: "pre-wrap" }}
                        >
                          {message.content}
                        </Typography>
                        <Box
                          display="flex"
                          alignItems="center"
                          justifyContent="flex-end"
                          mt={0.5}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              opacity: 0.8,
                              mr: 0.5,
                            }}
                          >
                            {formatMessageTimestamp(message.created_at)}
                          </Typography>
                          {isStudent && (
                            <Tooltip title={isRead ? "Đã đọc" : "Đã gửi"}>
                              {isRead ? (
                                <ReadIcon sx={{ fontSize: 14, opacity: 0.8 }} />
                              ) : (
                                <UnreadIcon
                                  sx={{ fontSize: 14, opacity: 0.8 }}
                                />
                              )}
                            </Tooltip>
                          )}
                        </Box>
                      </Paper>

                      {/* Student Avatar */}
                      {isStudent && (
                        <Avatar
                          sx={{
                            bgcolor: getAvatarColor(message.sender_type),
                            ml: 1,
                            width: 32,
                            height: 32,
                          }}
                        >
                          <PersonIcon fontSize="small" />
                        </Avatar>
                      )}
                    </Box>
                  );
                })}
                <div ref={messagesEndRef} />
              </Stack>
            )}
          </Box>

          <Divider />

          {/* Input Box */}
          <Box p={2} sx={{ backgroundColor: "white" }}>
            <Box display="flex" alignItems="flex-end">
              <TextField
                fullWidth
                multiline
                maxRows={4}
                placeholder="Nhập tin nhắn của bạn..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={sending}
                variant="outlined"
                sx={{ mr: 1 }}
              />
              <IconButton
                color="primary"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || sending}
                sx={{
                  backgroundColor: "primary.main",
                  color: "white",
                  "&:hover": {
                    backgroundColor: "primary.dark",
                  },
                  "&:disabled": {
                    backgroundColor: "action.disabledBackground",
                  },
                }}
              >
                {sending ? <CircularProgress size={24} /> : <SendIcon />}
              </IconButton>
            </Box>
          </Box>
        </Paper>

        {/* Info Notice */}
        {conversationDetail && (
          <Paper elevation={1} sx={{ p: 1.5, backgroundColor: "#e3f2fd" }}>
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
            >
              💬 Cuộc trò chuyện này là riêng tư giữa bạn và{" "}
              <strong>{conversationDetail.counselor.full_name}</strong>. Tư vấn
              viên sẽ phản hồi trong thời gian sớm nhất.
            </Typography>
          </Paper>
        )}
      </Container>
    </MainLayout>
  );
};

export default CounselorChatPage;
