/**
 * AI Chat Page - Messenger-like interface for chatting with AI Assistant
 */
import React, { useState, useEffect, useRef } from "react";
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
} from "@mui/material";
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  ArrowBack as BackIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import {
  getOrCreateConversation,
  getMessages,
  sendMessage,
  Message,
  AssessmentContext,
} from "../../services/aiChatService";

const AIChatPage: React.FC = () => {
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [assessmentContext, setAssessmentContext] =
    useState<AssessmentContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize conversation
  useEffect(() => {
    const initConversation = async () => {
      try {
        setLoading(true);
        const conversation = await getOrCreateConversation();

        // Load messages
        const msgs = await getMessages(conversation.id);
        setMessages(msgs);
      } catch (err: any) {
        console.error("Failed to init conversation:", err);
        setError(
          err.response?.data?.detail ||
            "Không thể kết nối với AI. Vui lòng thử lại."
        );
      } finally {
        setLoading(false);
      }
    };

    initConversation();
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || sending) return;

    const userMessageContent = inputValue.trim();
    setInputValue("");
    setSending(true);
    setError(null);

    // Optimistic UI update
    const tempUserMsg: Message = {
      id: Date.now(),
      role: "user",
      content: userMessageContent,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendMessage(userMessageContent);

      // Replace temp message with real messages
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...withoutTemp, response.user_message, response.ai_message];
      });

      // Update assessment context if provided
      if (response.assessment_context) {
        setAssessmentContext(response.assessment_context);
      }
    } catch (err: any) {
      console.error("Failed to send message:", err);
      setError(
        err.response?.data?.detail ||
          "Không thể gửi tin nhắn. Vui lòng thử lại."
      );

      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
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

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      minimal: "success",
      mild: "info",
      moderate: "warning",
      severe: "error",
    };
    return colors[severity] || "default";
  };

  const getSeverityLabel = (severity: string) => {
    const labels: Record<string, string> = {
      minimal: "Rất tốt",
      mild: "Nhẹ",
      moderate: "Trung bình",
      severe: "Nghiêm trọng",
    };
    return labels[severity] || severity;
  };

  if (loading) {
    return (
      <MainLayout>
        <Container
          maxWidth="md"
          sx={{
            height: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Stack alignItems="center" spacing={2}>
            <CircularProgress size={48} />
            <Typography color="text.secondary">
              Đang kết nối với AI Assistant...
            </Typography>
          </Stack>
        </Container>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          bgcolor: "#f5f5f5",
        }}
      >
        {/* Header */}
        <Paper
          elevation={2}
          sx={{
            px: 2,
            py: 1.5,
            display: "flex",
            alignItems: "center",
            bgcolor: "primary.main",
            color: "white",
            borderRadius: 0,
          }}
        >
          <IconButton
            onClick={() => navigate("/dashboard")}
            sx={{ color: "white", mr: 1 }}
          >
            <BackIcon />
          </IconButton>

          <Avatar sx={{ bgcolor: "white", color: "primary.main", mr: 1.5 }}>
            <AIIcon />
          </Avatar>

          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              AI4Mind Assistant
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Trợ lý sức khỏe tinh thần
            </Typography>
          </Box>
        </Paper>

        {/* Assessment Context Badge */}
        {assessmentContext && (
          <Paper
            sx={{
              m: 2,
              p: 2,
              bgcolor: "#fff3e0",
              borderLeft: 4,
              borderColor: "warning.main",
            }}
          >
            <Stack direction="row" spacing={1} alignItems="center">
              <InfoIcon color="warning" fontSize="small" />
              <Typography variant="body2" sx={{ flex: 1 }}>
                Đánh giá GAD-7 gần nhất:{" "}
                <strong>{assessmentContext.score}/21 điểm</strong> - Mức độ:{" "}
                <Chip
                  label={getSeverityLabel(assessmentContext.severity)}
                  size="small"
                  color={getSeverityColor(assessmentContext.severity) as any}
                  sx={{ ml: 1 }}
                />
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {assessmentContext.date}
              </Typography>
            </Stack>
          </Paper>
        )}

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Messages Container */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            px: 2,
            pb: 2,
            "&::-webkit-scrollbar": {
              width: "8px",
            },
            "&::-webkit-scrollbar-thumb": {
              bgcolor: "rgba(0,0,0,0.2)",
              borderRadius: "4px",
            },
          }}
        >
          <Stack spacing={2} sx={{ maxWidth: "800px", mx: "auto", py: 2 }}>
            {messages.map((message, index) => {
              const isUser = message.role === "user";
              const isFirst =
                index === 0 || messages[index - 1].role !== message.role;

              return (
                <Box
                  key={message.id}
                  sx={{
                    display: "flex",
                    justifyContent: isUser ? "flex-end" : "flex-start",
                    alignItems: "flex-start",
                    gap: 1,
                  }}
                >
                  {/* Avatar for AI */}
                  {!isUser && isFirst && (
                    <Avatar
                      sx={{ bgcolor: "primary.main", width: 32, height: 32 }}
                    >
                      <AIIcon fontSize="small" />
                    </Avatar>
                  )}
                  {!isUser && !isFirst && <Box sx={{ width: 32 }} />}

                  {/* Message Bubble */}
                  <Paper
                    elevation={1}
                    sx={{
                      px: 2,
                      py: 1.5,
                      maxWidth: "70%",
                      bgcolor: isUser ? "primary.main" : "white",
                      color: isUser ? "white" : "text.primary",
                      borderRadius: isUser
                        ? "18px 18px 4px 18px"
                        : "18px 18px 18px 4px",
                      wordWrap: "break-word",
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        whiteSpace: "pre-wrap",
                        lineHeight: 1.5,
                      }}
                    >
                      {message.content}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        display: "block",
                        mt: 0.5,
                        opacity: 0.7,
                        fontSize: "0.7rem",
                      }}
                    >
                      {new Date(message.created_at).toLocaleTimeString(
                        "vi-VN",
                        {
                          hour: "2-digit",
                          minute: "2-digit",
                        }
                      )}
                    </Typography>
                  </Paper>

                  {/* Avatar for User */}
                  {isUser && isFirst && (
                    <Avatar
                      sx={{ bgcolor: "secondary.main", width: 32, height: 32 }}
                    >
                      <PersonIcon fontSize="small" />
                    </Avatar>
                  )}
                  {isUser && !isFirst && <Box sx={{ width: 32 }} />}
                </Box>
              );
            })}

            {/* Typing Indicator */}
            {sending && (
              <Box sx={{ display: "flex", gap: 1, alignItems: "flex-start" }}>
                <Avatar sx={{ bgcolor: "primary.main", width: 32, height: 32 }}>
                  <AIIcon fontSize="small" />
                </Avatar>
                <Paper
                  elevation={1}
                  sx={{
                    px: 2,
                    py: 1.5,
                    bgcolor: "white",
                    borderRadius: "18px 18px 18px 4px",
                  }}
                >
                  <Stack direction="row" spacing={0.5}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        bgcolor: "grey.400",
                        animation: "bounce 1.4s infinite ease-in-out",
                        animationDelay: "0s",
                      }}
                    />
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        bgcolor: "grey.400",
                        animation: "bounce 1.4s infinite ease-in-out",
                        animationDelay: "0.2s",
                      }}
                    />
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        bgcolor: "grey.400",
                        animation: "bounce 1.4s infinite ease-in-out",
                        animationDelay: "0.4s",
                      }}
                    />
                  </Stack>
                </Paper>
              </Box>
            )}

            <div ref={messagesEndRef} />
          </Stack>
        </Box>

        {/* Input Area */}
        <Paper
          elevation={3}
          sx={{
            p: 2,
            borderRadius: 0,
            bgcolor: "white",
          }}
        >
          <Box sx={{ maxWidth: "800px", mx: "auto", display: "flex", gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Nhập tin nhắn của bạn..."
              disabled={sending}
              variant="outlined"
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: "24px",
                  bgcolor: "#f5f5f5",
                },
              }}
            />
            <IconButton
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || sending}
              color="primary"
              sx={{
                bgcolor: "primary.main",
                color: "white",
                "&:hover": {
                  bgcolor: "primary.dark",
                },
                "&:disabled": {
                  bgcolor: "grey.300",
                },
                width: 48,
                height: 48,
              }}
            >
              {sending ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                <SendIcon />
              )}
            </IconButton>
          </Box>
        </Paper>

        {/* Bounce Animation for Typing Indicator */}
        <style>
          {`
          @keyframes bounce {
            0%, 60%, 100% {
              transform: translateY(0);
            }
            30% {
              transform: translateY(-10px);
            }
          }
        `}
        </style>
      </Box>
    </MainLayout>
  );
};

export default AIChatPage;
