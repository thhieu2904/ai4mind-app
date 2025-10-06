/**
 * CounselorListPage - Danh sách counselors available để student chọn và bắt đầu chat
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  Avatar,
} from "@mui/material";
import {
  Person as PersonIcon,
  Chat as ChatIcon,
  Search as SearchIcon,
  WorkOutline as WorkIcon,
  School as SchoolIcon,
} from "@mui/icons-material";
import { Counselor } from "../../types/counselorChat";
import {
  listAvailableCounselors,
  createConversation,
} from "../../services/counselorChatService";

const CounselorListPage: React.FC = () => {
  const navigate = useNavigate();

  const [counselors, setCounselors] = useState<Counselor[]>([]);
  const [filteredCounselors, setFilteredCounselors] = useState<Counselor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [creatingConversation, setCreatingConversation] = useState<
    number | null
  >(null);

  // Load counselors on mount
  useEffect(() => {
    loadCounselors();
  }, []);

  // Filter counselors khi search query thay đổi
  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredCounselors(counselors);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = counselors.filter(
        (c) =>
          c.full_name.toLowerCase().includes(query) ||
          (c.specialization &&
            c.specialization.toLowerCase().includes(query)) ||
          (c.bio && c.bio.toLowerCase().includes(query))
      );
      setFilteredCounselors(filtered);
    }
  }, [searchQuery, counselors]);

  const loadCounselors = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listAvailableCounselors();
      setCounselors(data);
      setFilteredCounselors(data);
    } catch (err: any) {
      console.error("Failed to load counselors:", err);
      setError(
        err.response?.data?.detail ||
          "Không thể tải danh sách tư vấn viên. Vui lòng thử lại sau."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStartChat = async (counselorId: number) => {
    try {
      setCreatingConversation(counselorId);
      setError(null);

      // Create hoặc get existing conversation
      const conversation = await createConversation(counselorId);

      // Navigate to chat page
      navigate(`/counselor-chat/${conversation.id}`);
    } catch (err: any) {
      console.error("Failed to create conversation:", err);
      setError(
        err.response?.data?.detail ||
          "Không thể tạo cuộc trò chuyện. Vui lòng thử lại."
      );
    } finally {
      setCreatingConversation(null);
    }
  };

  const getInitials = (fullName: string): string => {
    const parts = fullName.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return fullName.substring(0, 2).toUpperCase();
  };

  const getAvatarColor = (id: number): string => {
    const colors = [
      "#1976d2", // blue
      "#388e3c", // green
      "#d32f2f", // red
      "#7b1fa2", // purple
      "#f57c00", // orange
      "#0097a7", // cyan
    ];
    return colors[id % colors.length];
  };

  if (loading) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
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

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box mb={4}>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Chọn Tư Vấn Viên
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Kết nối với chuyên gia tâm lý để được tư vấn và hỗ trợ
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Search Box */}
        <Box mb={3}>
          <TextField
            fullWidth
            placeholder="Tìm kiếm theo tên, chuyên môn, mô tả..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Counselor Cards */}
        {filteredCounselors.length === 0 ? (
          <Alert severity="info">
            {searchQuery.trim() === ""
              ? "Hiện tại chưa có tư vấn viên nào available."
              : "Không tìm thấy tư vấn viên phù hợp với từ khóa tìm kiếm."}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {filteredCounselors.map((counselor) => (
              <Grid item xs={12} md={6} key={counselor.id}>
                <Card
                  elevation={2}
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    transition: "all 0.3s",
                    "&:hover": {
                      transform: "translateY(-4px)",
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    {/* Avatar + Name */}
                    <Box display="flex" alignItems="center" mb={2}>
                      <Avatar
                        sx={{
                          width: 64,
                          height: 64,
                          mr: 2,
                          bgcolor: getAvatarColor(counselor.id),
                          fontSize: "1.5rem",
                          fontWeight: "bold",
                        }}
                      >
                        {getInitials(counselor.full_name)}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" fontWeight="bold">
                          {counselor.full_name}
                        </Typography>
                        <Chip
                          label="Available"
                          color="success"
                          size="small"
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    </Box>

                    {/* Specialization */}
                    {counselor.specialization && (
                      <Box display="flex" alignItems="flex-start" mb={1.5}>
                        <SchoolIcon
                          sx={{ mr: 1, mt: 0.5, color: "primary.main" }}
                          fontSize="small"
                        />
                        <Typography variant="body2" color="text.secondary">
                          <strong>Chuyên môn:</strong>{" "}
                          {counselor.specialization}
                        </Typography>
                      </Box>
                    )}

                    {/* Experience */}
                    {counselor.years_of_experience !== undefined && (
                      <Box display="flex" alignItems="center" mb={1.5}>
                        <WorkIcon
                          sx={{ mr: 1, color: "primary.main" }}
                          fontSize="small"
                        />
                        <Typography variant="body2" color="text.secondary">
                          <strong>Kinh nghiệm:</strong>{" "}
                          {counselor.years_of_experience} năm
                        </Typography>
                      </Box>
                    )}

                    {/* Bio */}
                    {counselor.bio && (
                      <Box mt={2}>
                        <Typography variant="body2" color="text.secondary">
                          {counselor.bio}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>

                  {/* Action Button */}
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    <Button
                      variant="contained"
                      fullWidth
                      startIcon={<ChatIcon />}
                      onClick={() => handleStartChat(counselor.id)}
                      disabled={creatingConversation === counselor.id}
                    >
                      {creatingConversation === counselor.id ? (
                        <>
                          <CircularProgress size={20} sx={{ mr: 1 }} />
                          Đang tạo cuộc trò chuyện...
                        </>
                      ) : (
                        "Bắt đầu trò chuyện"
                      )}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Empty State */}
        {!loading && counselors.length === 0 && (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            minHeight="300px"
          >
            <PersonIcon sx={{ fontSize: 80, color: "text.disabled", mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Chưa có tư vấn viên nào available
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Vui lòng quay lại sau hoặc liên hệ với bộ phận hỗ trợ.
            </Typography>
          </Box>
        )}
      </Container>
    </MainLayout>
  );
};

export default CounselorListPage;
