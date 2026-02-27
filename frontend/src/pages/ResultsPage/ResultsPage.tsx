import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import "./ResultsPage.css";

// Converts **bold** markers to <strong> and \n to <br> — no extra dependency needed
const renderMarkdown = (text: string): React.ReactNode => {
  const lines = text.split("\n");
  return lines.map((line, li) => {
    const parts = line.split(/(\*\*[^*]+\*\*)/g);
    return (
      <React.Fragment key={li}>
        {li > 0 && <br />}
        {parts.map((part, pi) =>
          part.startsWith("**") && part.endsWith("**") ? (
            <strong key={pi}>{part.slice(2, -2)}</strong>
          ) : (
            part
          )
        )}
      </React.Fragment>
    );
  });
};

interface LocationState {
  assessmentId: number;
  score: number;
  severity: string;
  analysis?: string;
  recommendations?: string[];
  answers: (number | null)[];
}

const getSeverityInfo = (severity: string) => {
  const severityMap: Record<
    string,
    {
      label: string;
      color: string;
      description: string;
      recommendations: string[];
    }
  > = {
    minimal: {
      label: "Lo âu tối thiểu",
      color: "#10b981",
      description:
        "Bạn có mức độ lo âu rất thấp hoặc không có lo âu. Đây là một dấu hiệu tích cực cho sức khỏe tinh thần của bạn.",
      recommendations: [
        "Tiếp tục duy trì lối sống lành mạnh và các hoạt động thư giãn",
        "Thực hành chánh niệm và thiền định thường xuyên",
        "Duy trì mối quan hệ xã hội tích cực",
        "Tập thể dục đều đặn và ngủ đủ giấc",
      ],
    },
    mild: {
      label: "Lo âu nhẹ",
      color: "#f59e0b",
      description:
        "Bạn đang trải qua mức độ lo âu nhẹ. Đây là điều bình thường và có thể được quản lý với một số thay đổi trong lối sống.",
      recommendations: [
        "Thực hành các kỹ thuật thư giãn như hít thở sâu",
        "Tăng cường hoạt động thể chất",
        "Giảm caffeine và các chất kích thích",
        "Chia sẻ cảm xúc với người thân hoặc bạn bè",
        "Theo dõi tình trạng trong 2-4 tuần tới",
      ],
    },
    moderate: {
      label: "Lo âu trung bình",
      color: "#f97316",
      description:
        "Bạn đang có mức độ lo âu trung bình. Nên cân nhắc tìm kiếm sự hỗ trợ chuyên môn để quản lý tốt hơn.",
      recommendations: [
        "Nên tham khảo ý kiến của chuyên gia tâm lý",
        "Xem xét liệu pháp nhận thức hành vi (CBT)",
        "Thực hành các kỹ thuật giảm căng thẳng hàng ngày",
        "Tránh rượu và các chất kích thích",
        "Xây dựng thói quen ngủ nghỉ đều đặn",
        "Tham gia nhóm hỗ trợ nếu có thể",
      ],
    },
    severe: {
      label: "Lo âu nặng",
      color: "#dc2626",
      description:
        "Bạn đang trải qua mức độ lo âu nghiêm trọng. Rất khuyến khích bạn tìm kiếm sự giúp đỡ chuyên nghiệp ngay.",
      recommendations: [
        "Hãy liên hệ với chuyên gia tâm lý hoặc bác sĩ tâm thần ngay",
        "Xem xét điều trị kết hợp (liệu pháp + thuốc nếu cần)",
        "Tránh tự điều trị hoặc sử dụng chất gây nghiện",
        "Thông báo cho người thân để được hỗ trợ",
        "Đường dây nóng: 1800-xxxx (24/7)",
        "Không đối mặt một mình - hãy tìm kiếm giúp đỡ",
      ],
    },
  };

  return severityMap[severity];
};

const ResultsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState;

  useEffect(() => {
    // Redirect if no assessment data
    if (!state || !state.assessmentId || typeof state.score !== "number") {
      navigate("/assessment");
    }
  }, [state, navigate]);

  if (!state || !state.assessmentId || typeof state.score !== "number") {
    return null;
  }

  const { assessmentId, score, severity, analysis, recommendations } = state;

  // Use Gemini analysis if available, fallback to hardcoded
  const severityInfo = getSeverityInfo(severity);
  const displayAnalysis = analysis || severityInfo.description;
  const displayRecommendations =
    recommendations && recommendations.length > 0
      ? recommendations
      : severityInfo.recommendations;

  const handleBackToDashboard = () => {
    navigate("/dashboard");
  };

  const handleRetakeAssessment = () => {
    navigate("/assessment");
  };

  return (
    <MainLayout>
      <div className="results-container">
        {/* Header */}
        <div className="results-header">
          <button className="back-button" onClick={handleBackToDashboard}>
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
          <h1 className="results-title">Kết quả đánh giá</h1>
          <div className="header-spacer"></div>
        </div>

        {/* Score Card */}
        <div className="score-card">
          <div className="score-badge">
            <div className="score-value">{score}</div>
            <div className="score-max">/21</div>
          </div>
          <div
            className={`severity-badge severity-${severity}`}
            style={{ background: severityInfo.color }}
          >
            {severityInfo.label}
          </div>
        </div>

        {/* Description Card */}
        <div className="info-card">
          <h2 className="info-title">Đánh giá của bạn</h2>
          <p className="info-description">{renderMarkdown(displayAnalysis)}</p>
        </div>

        {/* Recommendations Card */}
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
            Khuyến nghị
          </h2>
          <ul className="recommendations-list">
            {displayRecommendations.map((rec, index) => (
              <li key={index} className="recommendation-item">
                {renderMarkdown(rec)}
              </li>
            ))}
          </ul>
        </div>

        {/* Voice Analysis Suggestion Card */}
        <div className="suggestion-card">
          <div className="suggestion-icon">
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
          <div className="suggestion-content">
            <h3 className="suggestion-title">Đánh giá toàn diện hơn</h3>
            <p className="suggestion-text">
              Kết quả GAD-7 chỉ dựa trên câu trả lời chủ quan của bạn. Để có
              đánh giá chính xác hơn, hãy thực hiện thêm{" "}
              <strong>phân tích giọng nói</strong> - công nghệ AI sẽ phân tích
              cảm xúc từ giọng nói của bạn.
            </p>
            <button
              className="suggestion-button"
              onClick={() =>
                navigate("/voice-analysis", {
                  state: {
                    assessmentId,
                    gad7Score: score,
                    gad7Severity: severity,
                  },
                })
              }
            >
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
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
              Phân tích giọng nói ngay
            </button>
          </div>
        </div>

        {/* Important Note */}
        {(severity === "moderate" || severity === "severe") && (
          <div className={`warning-card warning-${severity}`}>
            <div className="warning-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
            </div>
            <div className="warning-content">
              <h3 className="warning-title">Lưu ý quan trọng</h3>
              <p className="warning-text">
                {severity === "severe"
                  ? "Kết quả cho thấy bạn đang trải qua mức độ lo âu cao. Chúng tôi thực sự khuyến khích bạn nên tìm kiếm sự giúp đỡ từ chuyên gia tâm lý hoặc bác sĩ tâm thần ngay lập tức."
                  : "Kết quả cho thấy bạn có dấu hiệu lo âu đáng chú ý. Hãy cân nhắc tham khảo ý kiến chuyên gia để được hỗ trợ tốt hơn."}
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="primary-button" onClick={handleBackToDashboard}>
            Về trang chủ
          </button>
          <button className="secondary-button" onClick={handleRetakeAssessment}>
            Làm lại bài đánh giá
          </button>
        </div>

        {/* Disclaimer */}
        <div className="disclaimer">
          <p>
            <strong>Lưu ý:</strong> Kết quả GAD-7 chỉ dựa trên câu trả lời tự
            đánh giá và mang tính chất tham khảo. Để có đánh giá toàn diện và
            chính xác hơn, nên kết hợp với phân tích giọng nói và tham khảo ý
            kiến chuyên gia tâm lý. Kết quả này không thay thế cho chẩn đoán y
            tế chuyên nghiệp.
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

export default ResultsPage;
