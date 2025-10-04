/**
 * SupportHubPage - Landing page cho "Tìm kiếm hỗ trợ sức khỏe tinh thần"
 * 3 options: AI Chat, Counselor Chat, Medical Centers
 */
import React from "react";
import { useNavigate } from "react-router-dom";
import { Container, Box, Typography, Stack, Paper } from "@mui/material";
import {
  SmartToy as AIIcon,
  People as CounselorIcon,
  LocalHospital as HospitalIcon,
} from "@mui/icons-material";
import MainLayout from "../../components/layout/MainLayout/MainLayout";

const SupportHubPage: React.FC = () => {
  const navigate = useNavigate();

  const supportOptions = [
    {
      title: "Trò chuyện với AI",
      description: "Tư vấn tức thì với AI Assistant",
      icon: <AIIcon sx={{ fontSize: 48 }} />,
      route: "/ai-chat",
      color: "#667eea",
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    {
      title: "Tìm kiếm chuyên gia tâm lý",
      description: "Kết nối với tư vấn viên chuyên nghiệp",
      icon: <CounselorIcon sx={{ fontSize: 48 }} />,
      route: "/counselor-list",
      color: "#f093fb",
      gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    },
    {
      title: "Tìm kiếm trung tâm y tế",
      description: "Địa chỉ bệnh viện và phòng khám gần bạn",
      icon: <HospitalIcon sx={{ fontSize: 48 }} />,
      route: "/medical-centers",
      color: "#4facfe",
      gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    },
  ];

  return (
    <MainLayout>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box mb={4} textAlign="center">
          <Typography
            variant="h4"
            gutterBottom
            fontWeight="bold"
            sx={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Tìm kiếm hỗ trợ
            <br />
            sức khỏe tinh thần
          </Typography>
          <Typography variant="body1" color="text.secondary" mt={1}>
            Chọn hình thức hỗ trợ phù hợp với bạn
          </Typography>
        </Box>

        {/* Support Options */}
        <Stack spacing={3}>
          {supportOptions.map((option, index) => (
            <Paper
              key={index}
              elevation={3}
              sx={{
                p: 3,
                cursor: "pointer",
                transition: "all 0.3s ease",
                borderRadius: 4,
                background: "white",
                border: "2px solid transparent",
                "&:hover": {
                  transform: "translateY(-8px)",
                  boxShadow: 6,
                  borderColor: option.color,
                },
              }}
              onClick={() => navigate(option.route)}
            >
              <Box display="flex" alignItems="center">
                {/* Icon */}
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: 3,
                    background: option.gradient,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "white",
                    mr: 3,
                    flexShrink: 0,
                  }}
                >
                  {option.icon}
                </Box>

                {/* Content */}
                <Box flexGrow={1}>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    {option.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {option.description}
                  </Typography>
                </Box>

                {/* Arrow */}
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    backgroundColor: "rgba(0,0,0,0.05)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    ml: 2,
                  }}
                >
                  <Typography variant="h5">→</Typography>
                </Box>
              </Box>
            </Paper>
          ))}
        </Stack>

        {/* Info Box */}
        <Paper
          elevation={0}
          sx={{
            mt: 4,
            p: 3,
            backgroundColor: "#f8f9fa",
            borderRadius: 3,
            border: "1px solid #e0e0e0",
          }}
        >
          <Typography variant="body2" color="text.secondary" textAlign="center">
            💡 <strong>Lưu ý:</strong> Tất cả thông tin của bạn đều được bảo mật
            và chỉ được sử dụng cho mục đích hỗ trợ sức khỏe tinh thần.
          </Typography>
        </Paper>
      </Container>
    </MainLayout>
  );
};

export default SupportHubPage;
