/**
 * Assessment Detail Modal - Hiển thị chi tiết đầy đủ của một assessment
 */
import React, { useState, useEffect } from "react";
import { format } from "date-fns";
import { vi } from "date-fns/locale";
import {
  AssessmentService,
  type Assessment,
} from "../../../services/assessmentService";
import "./AssessmentDetailModal.css";

// Converts **bold** markers → <strong>
const renderMarkdown = (text: string): React.ReactNode => {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i}>{part.slice(2, -2)}</strong>
    ) : (
      part
    )
  );
};

// Splits multi-paragraph text on \n\n, handles **bold** in each paragraph
const renderAnalysis = (text: string): React.ReactNode =>
  text
    .split(/\n{2,}/g)
    .filter((p) => p.trim())
    .map((paragraph, pi) => (
      <p key={pi} style={{ margin: pi > 0 ? "0.75rem 0 0" : "0" }}>
        {renderMarkdown(paragraph.trim())}
      </p>
    ));

interface AssessmentDetailModalProps {
  isOpen: boolean;
  assessmentId: number | null;
  onClose: () => void;
}

const GAD7_QUESTIONS = [
  "Cảm thấy lo lắng, bồn chồn hoặc căng thẳng",
  "Không thể ngừng lo lắng hoặc kiểm soát được việc lo lắng",
  "Lo lắng quá nhiều về những điều khác nhau",
  "Khó thư giãn",
  "Bồn chồn đến mức khó ngồi yên",
  "Dễ bực tức hoặc cáu kỉnh",
  "Cảm thấy sợ hãi như thể điều gì đó tồi tệ có thể xảy ra",
];

const ANSWER_LABELS = [
  "Không bao giờ",
  "Vài ngày",
  "Hơn một nửa số ngày",
  "Gần như mỗi ngày",
];

const AssessmentDetailModal: React.FC<AssessmentDetailModalProps> = ({
  isOpen,
  assessmentId,
  onClose,
}) => {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && assessmentId) {
      fetchAssessmentDetail();
    }
  }, [isOpen, assessmentId]);

  const fetchAssessmentDetail = async () => {
    if (!assessmentId) return;

    try {
      setLoading(true);
      setError(null);

      const data = await AssessmentService.getAssessmentDetail(assessmentId);
      setAssessment(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Không thể tải chi tiết đánh giá"
      );
      console.error("Error fetching assessment detail:", err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityInfo = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "minimal":
        return {
          label: "Tối thiểu",
          color: "#28a745",
          description: "Mức độ lo âu rất thấp",
        };
      case "mild":
        return {
          label: "Nhẹ",
          color: "#17a2b8",
          description: "Mức độ lo âu nhẹ",
        };
      case "moderate":
        return {
          label: "Vừa phải",
          color: "#ffc107",
          description: "Mức độ lo âu vừa phải",
        };
      case "severe":
        return {
          label: "Nghiêm trọng",
          color: "#dc3545",
          description: "Mức độ lo âu nghiêm trọng",
        };
      default:
        return { label: severity, color: "#6c757d", description: "" };
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "dd/MM/yyyy lúc HH:mm", {
        locale: vi,
      });
    } catch {
      return dateString;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Chi tiết đánh giá GAD-7</h2>
          <button className="modal-close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Đang tải chi tiết...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>{error}</p>
              <button onClick={fetchAssessmentDetail} className="retry-btn">
                Thử lại
              </button>
            </div>
          )}

          {assessment && (
            <div className="assessment-detail">
              {/* Overview Section */}
              <div className="detail-section">
                <h3>Tổng quan</h3>
                <div className="overview-grid">
                  <div className="overview-item">
                    <label>Điểm số:</label>
                    <span className="score-display">
                      {assessment.total_score}/21
                    </span>
                  </div>
                  <div className="overview-item">
                    <label>Mức độ:</label>
                    <span
                      className="severity-display"
                      style={{
                        color: getSeverityInfo(assessment.severity_level).color,
                      }}
                    >
                      {getSeverityInfo(assessment.severity_level).label}
                    </span>
                  </div>
                  <div className="overview-item">
                    <label>Ngày thực hiện:</label>
                    <span>{formatDate(assessment.created_at)}</span>
                  </div>
                  <div className="overview-item">
                    <label>ID đánh giá:</label>
                    <span>#{assessment.id}</span>
                  </div>
                </div>
              </div>

              {/* Questions & Answers */}
              <div className="detail-section">
                <h3>Câu hỏi và câu trả lời</h3>
                <div className="questions-answers">
                  {GAD7_QUESTIONS.map((question, index) => (
                    <div key={index} className="question-answer">
                      <div className="question">
                        <span className="question-number">{index + 1}.</span>
                        <span className="question-text">{question}</span>
                      </div>
                      <div className="answer">
                        <span className="answer-score">
                          {assessment.answers[index]} điểm
                        </span>
                        <span className="answer-text">
                          ({ANSWER_LABELS[assessment.answers[index]]})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Functional Impairment */}
              {assessment.functional_impairment !== null &&
                assessment.functional_impairment !== undefined && (
                  <div className="detail-section">
                    <h3>Mức độ ảnh hưởng đến cuộc sống</h3>
                    <p>
                      Điểm: {assessment.functional_impairment}/3 -{" "}
                      {assessment.functional_impairment === 0 &&
                        "Không ảnh hưởng"}
                      {assessment.functional_impairment === 1 && "Ảnh hưởng ít"}
                      {assessment.functional_impairment === 2 &&
                        "Ảnh hưởng vừa"}
                      {assessment.functional_impairment === 3 &&
                        "Ảnh hưởng nhiều"}
                    </p>
                  </div>
                )}

              {/* Analysis */}
              {assessment.analysis && (
                <div className="detail-section">
                  <h3>Phân tích chi tiết</h3>
                  <div className="analysis-content">
                    {renderAnalysis(assessment.analysis)}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {assessment.recommendations &&
                assessment.recommendations.length > 0 && (
                  <div className="detail-section">
                    <h3>Gợi ý hỗ trợ</h3>
                    <ul className="recommendations-list">
                      {assessment.recommendations.map(
                        (recommendation, index) => (
                          <li key={index}>{renderAnalysis(recommendation)}</li>
                        )
                      )}
                    </ul>
                  </div>
                )}

              {/* Notes */}
              {assessment.notes && (
                <div className="detail-section">
                  <h3>Ghi chú</h3>
                  <p>{assessment.notes}</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="btn btn-secondary">
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssessmentDetailModal;
