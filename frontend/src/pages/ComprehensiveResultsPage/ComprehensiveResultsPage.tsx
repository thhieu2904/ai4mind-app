import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import "./ComprehensiveResultsPage.css";

interface LocationState {
  // GAD-7 Data
  assessmentId: number;
  gad7Score: number;
  gad7Severity: string;

  // Voice Data
  voiceAnalysisId?: number;
  dominantEmotion?: string;
  sentimentScore?: number;
  transcription?: string;

  // Gemini Comprehensive Analysis
  comprehensiveAnalysis?: string;
  comprehensiveRecommendations?: string[];

  // Loading state - when navigating before API completes
  isLoading?: boolean;

  // Voice-only analysis flag
  isVoiceOnly?: boolean;
}

const ComprehensiveResultsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState;

  const [isLoading, setIsLoading] = useState(false);

  // Debug log
  console.log("🎯 ComprehensiveResultsPage received state:", state);

  // Redirect if no essential data
  if (!state) {
    console.warn("⚠️ No state provided, redirecting to dashboard");
    navigate("/dashboard");
    return null;
  }

  // Check if we have minimum required data
  if (!state) {
    console.warn("⚠️ No state provided, redirecting to dashboard");
    navigate("/dashboard");
    return null;
  }

  // For voice-only analysis, allow assessmentId = 0
  const isVoiceOnly = state.isVoiceOnly || state.assessmentId === 0;
  const hasVoiceData = state.voiceAnalysisId && state.comprehensiveAnalysis;

  if (!isVoiceOnly && (!state.assessmentId || state.gad7Score === undefined)) {
    console.warn(
      "⚠️ Missing GAD-7 data for comprehensive analysis, redirecting to dashboard"
    );
    navigate("/dashboard");
    return null;
  }

  // If we have GAD-7 data but missing voice/comprehensive data, show loading
  if (!isVoiceOnly && !hasVoiceData && !state.isLoading) {
    // This shouldn't happen in normal flow, but handle gracefully
    console.warn("⚠️ Missing voice analysis data but not in loading state");
    setIsLoading(true);
    // Could fetch data here if needed
  }
  const {
    assessmentId,
    gad7Score,
    gad7Severity,
    voiceAnalysisId,
    dominantEmotion,
    sentimentScore,
    transcription,
    comprehensiveAnalysis,
    comprehensiveRecommendations,
  } = state;

  // Use fallback if comprehensive data is missing
  const finalAnalysis =
    comprehensiveAnalysis ||
    "Đang xử lý phân tích tổng hợp. Vui lòng chờ trong giây lát...";
  const finalRecommendations = comprehensiveRecommendations || [
    "Gặp tư vấn viên để được hỗ trợ chi tiết hơn",
    "Thực hành các kỹ thuật thư giãn hàng ngày",
    "Theo dõi tình trạng trong thời gian tới",
  ];

  // Severity color mapping
  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      minimal: "#10b981",
      mild: "#f59e0b",
      moderate: "#f97316",
      severe: "#dc2626",
    };
    return colors[severity] || "#6b7280";
  };

  const getSeverityLabel = (severity: string) => {
    const labels: Record<string, string> = {
      minimal: "Lo âu tối thiểu",
      mild: "Lo âu nhẹ",
      moderate: "Lo âu trung bình",
      severe: "Lo âu nặng",
    };
    return labels[severity] || severity;
  };

  // Emotion icon mapping
  const getEmotionIcon = (emotion?: string) => {
    switch (emotion?.toLowerCase()) {
      case "anxiety":
        return "😰";
      case "sadness":
        return "😢";
      case "anger":
        return "😠";
      case "neutral":
        return "😐";
      case "joy":
        return "😊";
      default:
        return "🎭";
    }
  };

  const getEmotionLabel = (emotion?: string) => {
    const labels: Record<string, string> = {
      anxiety: "Lo âu",
      sadness: "Buồn bã",
      anger: "Giận dữ",
      neutral: "Trung tính",
      joy: "Vui vẻ",
    };
    return labels[emotion?.toLowerCase() || ""] || emotion || "N/A";
  };

  // Check if we're still loading comprehensive data
  const isLoadingData = (!isVoiceOnly && !hasVoiceData) || isLoading;

  // Loading component
  if (isLoadingData && !isVoiceOnly) {
    return (
      <MainLayout>
        <div className="comprehensive-results-container">
          <div className="comprehensive-header">
            <button
              className="back-button"
              onClick={() => navigate("/dashboard")}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <h1 className="page-title">Đang phân tích...</h1>
            <div className="header-spacer"></div>
          </div>

          {/* Loading State */}
          <div style={{ textAlign: "center", padding: "40px 20px" }}>
            <div style={{ fontSize: "48px", marginBottom: "20px" }}>🧠</div>
            <h2 style={{ color: "#6b7280", marginBottom: "10px" }}>
              Đang xử lý phân tích tổng hợp
            </h2>
            <p style={{ color: "#9ca3af" }}>
              AI đang kết hợp dữ liệu từ bài đánh giá GAD-7 và phân tích giọng
              nói của bạn...
            </p>
            <div style={{ marginTop: "30px" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  border: "4px solid #f3f4f6",
                  borderTop: "4px solid #8b5cf6",
                  borderRadius: "50%",
                  animation: "spin 1s linear infinite",
                  margin: "0 auto",
                }}
              ></div>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="comprehensive-results-container">
        {/* Header */}
        <div className="comprehensive-header">
          <button
            className="back-button"
            onClick={() => navigate("/dashboard")}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          <h1 className="page-title">Đánh giá toàn diện</h1>
          <div className="header-spacer"></div>
        </div>

        {/* Summary Cards */}
        <div className="summary-grid">
          {/* GAD-7 Summary */}
          <div className="summary-card gad7-card">
            <div className="summary-icon">📊</div>
            <h3 className="summary-title">GAD-7 Assessment</h3>
            <div className="summary-content">
              <div className="score-display">
                <span className="score-value">{gad7Score}</span>
                <span className="score-max">/21</span>
              </div>
              <div
                className="severity-badge"
                style={{ backgroundColor: getSeverityColor(gad7Severity) }}
              >
                {getSeverityLabel(gad7Severity)}
              </div>
            </div>
          </div>

          {/* Voice Summary */}
          <div className="summary-card voice-card">
            <div className="summary-icon">🎤</div>
            <h3 className="summary-title">Voice Analysis</h3>
            <div className="summary-content">
              <div className="emotion-display">
                <span className="emotion-icon">
                  {getEmotionIcon(dominantEmotion)}
                </span>
                <span className="emotion-label">
                  {getEmotionLabel(dominantEmotion)}
                </span>
              </div>
              {sentimentScore !== undefined && (
                <div className="sentiment-bar">
                  <div className="sentiment-label">
                    Sentiment:{" "}
                    {sentimentScore > 0
                      ? "Tích cực"
                      : sentimentScore < -0.2
                        ? "Tiêu cực"
                        : "Trung tính"}
                  </div>
                  <div className="sentiment-progress">
                    <div
                      className="sentiment-fill"
                      style={{
                        width: `${Math.abs(sentimentScore) * 100}%`,
                        backgroundColor:
                          sentimentScore > 0 ? "#10b981" : "#dc2626",
                      }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Gemini Comprehensive Analysis */}
        <div className="analysis-card">
          <div className="analysis-header">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <h2 className="analysis-title">Phân tích tổng hợp từ AI</h2>
          </div>
          <div className="analysis-content">
            <p className="analysis-text">{finalAnalysis}</p>
          </div>
        </div>

        {/* Transcription (if available) */}
        {transcription && (
          <div className="transcription-card">
            <h3 className="transcription-title">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                />
              </svg>
              Nội dung chia sẻ
            </h3>
            <p className="transcription-text">"{transcription}"</p>
          </div>
        )}

        {/* Recommendations */}
        <div className="recommendations-card">
          <h2 className="recommendations-title">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Khuyến nghị từ phân tích tổng hợp
          </h2>
          <ul className="recommendations-list">
            {finalRecommendations.map((recommendation, index) => (
              <li key={index} className="recommendation-item">
                <span className="recommendation-number">{index + 1}</span>
                <span className="recommendation-text">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Cross-validation Note */}
        <div className="info-note">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>
            Kết quả này được tạo bởi AI dựa trên việc so sánh chéo giữa đánh giá
            GAD-7 (tự đánh giá) và phân tích giọng nói (cảm xúc khách quan),
            giúp phát hiện sự khác biệt và đưa ra đánh giá chính xác hơn.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            className="action-button secondary"
            onClick={() =>
              navigate(`/assessment/results`, {
                state: {
                  assessmentId,
                  score: gad7Score,
                  severity: gad7Severity,
                },
              })
            }
          >
            Xem chi tiết GAD-7
          </button>
          <button
            className="action-button primary"
            onClick={() => navigate("/dashboard")}
          >
            Về trang chủ
          </button>
        </div>
      </div>
    </MainLayout>
  );
};

export default ComprehensiveResultsPage;
