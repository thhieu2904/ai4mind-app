import React from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import "./DashboardPage.css";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <MainLayout>
      <div className="dashboard-container">
        {/* Welcome Card with Health Info */}
        <div className="welcome-card">
          <h1 className="welcome-title">
            Xin chào
            <br />
            (tên)!
          </h1>
          <div className="health-info">
            <p className="info-item">
              • Bạn đã chăm sóc sức khỏe tinh thần cùng <strong>AI4Mind</strong>{" "}
              được [số ngày] ngày.
            </p>
            <p className="info-item">
              • Trạng thái của bạn trong 30 ngày gần đây là [
              <strong>cảm xúc người dùng</strong>].
            </p>
          </div>
        </div>

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
          <button className="feature-card" onClick={() => navigate("/support")}>
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
