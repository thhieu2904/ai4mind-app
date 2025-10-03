/**
 * Overview Cards - Hiển thị thống kê tổng quan
 */
import React from "react";
import "./OverviewCards.css";

interface OverviewCardsProps {
  totalAssessments: number;
  averageScore: number;
  latestScore?: number;
  trend?: "improving" | "worsening" | "stable";
  loading?: boolean;
}

const OverviewCards: React.FC<OverviewCardsProps> = ({
  totalAssessments,
  averageScore,
  latestScore,
  trend,
  loading = false,
}) => {
  const getTrendIcon = () => {
    if (!trend) return "➡️";
    switch (trend) {
      case "improving":
        return "📈";
      case "worsening":
        return "📉";
      case "stable":
        return "➡️";
      default:
        return "➡️";
    }
  };

  const getTrendText = () => {
    if (!trend) return "Chưa có dữ liệu";
    switch (trend) {
      case "improving":
        return "Đang cải thiện";
      case "worsening":
        return "Đang xấu đi";
      case "stable":
        return "Ổn định";
      default:
        return "Chưa xác định";
    }
  };

  const getTrendClass = () => {
    if (!trend) return "";
    return `trend-${trend}`;
  };

  if (loading) {
    return (
      <div className="overview-cards">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="overview-card skeleton">
            <div className="card-skeleton-icon"></div>
            <div className="card-skeleton-text"></div>
            <div className="card-skeleton-value"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="overview-cards">
      {/* Total Assessments */}
      <div className="overview-card card-primary">
        <div className="card-icon">📊</div>
        <div className="card-content">
          <div className="card-label">Tổng số lần đánh giá</div>
          <div className="card-value">{totalAssessments}</div>
        </div>
      </div>

      {/* Average Score */}
      <div className="overview-card card-info">
        <div className="card-icon">📈</div>
        <div className="card-content">
          <div className="card-label">Điểm trung bình</div>
          <div className="card-value">
            {averageScore.toFixed(1)}
            <span className="card-max">/21</span>
          </div>
        </div>
      </div>

      {/* Latest Score */}
      <div className="overview-card card-success">
        <div className="card-icon">🎯</div>
        <div className="card-content">
          <div className="card-label">Điểm gần nhất</div>
          <div className="card-value">
            {latestScore !== undefined ? latestScore : "---"}
            {latestScore !== undefined && <span className="card-max">/21</span>}
          </div>
        </div>
      </div>

      {/* Trend */}
      <div className={`overview-card card-trend ${getTrendClass()}`}>
        <div className="card-icon">{getTrendIcon()}</div>
        <div className="card-content">
          <div className="card-label">Xu hướng</div>
          <div className="card-value-text">{getTrendText()}</div>
        </div>
      </div>
    </div>
  );
};

export default OverviewCards;
