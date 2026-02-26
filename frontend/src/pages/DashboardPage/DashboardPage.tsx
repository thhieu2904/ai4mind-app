import React, { useEffect, useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate, Navigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import PageHeaderCard from "../../components/common/PageHeaderCard";
import {
  DashboardService,
  DashboardWelcomeData,
} from "../../services/dashboardService";
import "./DashboardPage.css";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Redirect admin/counselor to their dedicated pages
  const role = (user?.role as string)?.toUpperCase();
  if (role === "ADMIN") return <Navigate to="/admin/dashboard" replace />;
  if (role === "COUNSELOR") return <Navigate to="/counselor/chats" replace />;

  const [welcomeData, setWelcomeData] = useState<DashboardWelcomeData | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only fetch student-specific data for STUDENT role
    if (user?.role === "STUDENT") {
      fetchWelcomeData();
    } else {
      // ADMIN, COUNSELOR: dùng data từ auth context, không cần gọi API
      setLoading(false);
    }
  }, [user]);

  const fetchWelcomeData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await DashboardService.getWelcomeData();
      setWelcomeData(data);
    } catch (err: any) {
      console.error("Failed to fetch welcome data:", err);
      setError("Không thể tải dữ liệu dashboard");
    } finally {
      setLoading(false);
    }
  };

  // Helper: Get emoji based on severity
  const getEmotionEmoji = (severity: string | null): string => {
    const emojiMap: Record<string, string> = {
      minimal: "😊",
      mild: "🙂",
      moderate: "😟",
      severe: "😔",
    };
    return emojiMap[severity || ""] || "💭";
  };

  // Helper: Format date difference
  const formatEmotionDate = (date: string | null): string => {
    if (!date) return "";

    const assessmentDate = new Date(date);
    const now = new Date();
    const diffDays = Math.floor(
      (now.getTime() - assessmentDate.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays === 0) return "hôm nay";
    if (diffDays === 1) return "hôm qua";
    if (diffDays <= 7) return `${diffDays} ngày trước`;
    return assessmentDate.toLocaleDateString("vi-VN");
  };

  return (
    <MainLayout>
      <div className="dashboard-container">
        {/* Page Header Card - Welcome */}
        {loading ? (
          <PageHeaderCard
            icon="🏠"
            title="Dashboard"
            subtitle="Đang tải..."
            variant="primary"
            gradient
          />
        ) : user?.role === "STUDENT" && error ? (
          <PageHeaderCard
            icon="🏠"
            title="Dashboard"
            subtitle={error}
            variant="primary"
            gradient
          />
        ) : user?.role !== "STUDENT" ? (
          // ADMIN / COUNSELOR: hiển thị welcome đơn giản không cần gọi API
          <PageHeaderCard
            icon="👋"
            title={`Xin chào, ${user?.full_name || "bạn"}!`}
            subtitle={
              user?.role === "ADMIN"
                ? "🛡️ Quản trị viên hệ thống"
                : "🩺 Tư vấn viên"
            }
            variant="primary"
            gradient
          />
        ) : (
          <PageHeaderCard
            icon="👋"
            title={`Xin chào, ${welcomeData?.user_name || user?.full_name || "bạn"}!`}
            subtitle={
              welcomeData?.latest_emotion_text
                ? `${getEmotionEmoji(welcomeData.latest_emotion_severity)} ${welcomeData.latest_emotion_text}`
                : "Chưa có đánh giá"
            }
            variant="primary"
            gradient
            description={
              <div className="dashboard-header-info">
                <p className="header-info-item">
                  🌟 Bạn đã chăm sóc sức khỏe tinh thần cùng{" "}
                  <strong>AI4Mind</strong> được{" "}
                  <strong>{welcomeData?.days_since_registration || 0}</strong>{" "}
                  ngày
                </p>

                {welcomeData?.latest_emotion_text && (
                  <p className="header-info-item">
                    📅 Cảm xúc gần nhất:{" "}
                    <strong>
                      {formatEmotionDate(welcomeData.latest_emotion_date)}
                    </strong>
                  </p>
                )}

                {/* Contextual messages */}
                {welcomeData?.latest_emotion_severity === "minimal" && (
                  <p className="header-info-item encouraging">
                    💪 Bạn đang làm rất tốt! Hãy tiếp tục duy trì.
                  </p>
                )}

                {welcomeData?.latest_emotion_severity === "severe" && (
                  <p className="header-info-item supportive">
                    🤗 Đừng lo lắng, chúng mình luôn ở đây hỗ trợ bạn.
                  </p>
                )}

                {!welcomeData?.has_recent_assessment &&
                  welcomeData &&
                  welcomeData.total_assessments > 0 && (
                    <p className="header-info-item reminder">
                      📅 Bạn chưa làm đánh giá trong tuần này.
                    </p>
                  )}

                {!welcomeData?.latest_emotion_text && (
                  <p className="header-info-item neutral">
                    💭 Hãy thử làm bài trắc nghiệm GAD-7 đầu tiên!
                  </p>
                )}
              </div>
            }
          />
        )}

        {/* Main Features Section */}
        <h2 className="section-title">Các tính năng chính</h2>

        <div className="features-grid">
          {/* Voice Recording */}
          <button
            className="feature-card"
            onClick={() => navigate("/voice-analysis")}
          >
            <div className="feature-icon">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            </div>
            <h3 className="feature-label">Ghi âm</h3>
          </button>

          {/* Health Assessment */}
          <button
            className="feature-card"
            onClick={() => navigate("/assessment")}
          >
            <div className="feature-icon">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <h3 className="feature-label">
              Trắc nghiệm
              <br />
              kiểm tra sức khỏe
            </h3>
          </button>

          {/* Statistics */}
          <button
            className="feature-card"
            onClick={() => navigate("/statistics")}
          >
            <div className="feature-icon">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <circle cx="12" cy="12" r="10" strokeWidth={1.5} />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M12 2v10l6 3"
                />
              </svg>
            </div>
            <h3 className="feature-label">
              Thống kê
              <br />
              sức khỏe
            </h3>
          </button>

          {/* Support */}
          <button
            className="feature-card"
            onClick={() => navigate("/support-hub")}
          >
            <div className="feature-icon">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
            </div>
            <h3 className="feature-label">
              Tìm kiếm
              <br />
              hỗ trợ
            </h3>
          </button>
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
