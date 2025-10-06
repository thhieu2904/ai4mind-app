/**
 * Assessment Card Component - Hiển thị thông tin tóm tắt một assessment
 */
import React from "react";
import { format } from "date-fns";
import { vi } from "date-fns/locale";
import { type Assessment } from "../../../services/assessmentService";
import "./AssessmentCard.css";

interface AssessmentCardProps {
  assessment: Assessment;
  onClick?: (assessment: Assessment) => void;
  showVoiceAnalysis?: boolean;
}

const AssessmentCard: React.FC<AssessmentCardProps> = ({
  assessment,
  onClick,
  showVoiceAnalysis = false,
}) => {
  const getSeverityInfo = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "minimal":
        return { label: "Tối thiểu", color: "success", bgColor: "#d4edda" };
      case "mild":
        return { label: "Nhẹ", color: "info", bgColor: "#d1ecf1" };
      case "moderate":
        return { label: "Vừa phải", color: "warning", bgColor: "#fff3cd" };
      case "severe":
        return { label: "Nghiêm trọng", color: "danger", bgColor: "#f8d7da" };
      default:
        return { label: severity, color: "secondary", bgColor: "#e9ecef" };
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "dd/MM/yyyy HH:mm", { locale: vi });
    } catch {
      return dateString;
    }
  };

  const severityInfo = getSeverityInfo(assessment.severity_level);

  return (
    <div
      className={`assessment-card ${onClick ? "clickable" : ""}`}
      onClick={() => onClick?.(assessment)}
    >
      <div className="assessment-card-header">
        <div className="assessment-score">
          <span className="score-number">{assessment.total_score}</span>
          <span className="score-total">/21</span>
        </div>
        <div
          className="severity-badge"
          style={{ backgroundColor: severityInfo.bgColor }}
        >
          <span className={`badge ${severityInfo.color}`}>
            {severityInfo.label}
          </span>
        </div>
      </div>

      <div className="assessment-card-body">
        <div className="assessment-date">
          <i className="icon-calendar"></i>
          <span>Ngày thực hiện: {formatDate(assessment.created_at)}</span>
        </div>

        {assessment.analysis && (
          <div className="assessment-analysis-preview">
            <p>
              {assessment.analysis.length > 100
                ? `${assessment.analysis.substring(0, 100)}...`
                : assessment.analysis}
            </p>
          </div>
        )}

        {assessment.recommendations &&
          assessment.recommendations.length > 0 && (
            <div className="assessment-recommendations-count">
              <i className="icon-lightbulb"></i>
              <span>{assessment.recommendations.length} gợi ý hỗ trợ</span>
            </div>
          )}
      </div>

      <div className="assessment-card-footer">
        <div className="assessment-id">
          <small>ID: {assessment.id}</small>
        </div>

        {showVoiceAnalysis && (
          <div className="voice-analysis-indicator">
            <i className="icon-microphone"></i>
            <small>Có phân tích giọng nói</small>
          </div>
        )}

        {onClick && (
          <div className="view-details">
            <span>Xem chi tiết →</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssessmentCard;
