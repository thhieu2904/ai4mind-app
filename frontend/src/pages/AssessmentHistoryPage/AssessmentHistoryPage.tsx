/**
 * Assessment History Page - Trang lịch sử các lần đánh giá GAD-7
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAssessments } from "../../hooks/useAssessments";
import { type Assessment } from "../../services/assessmentService";
import MainLayout from "../../components/layout/MainLayout";
import AssessmentCard from "./components/AssessmentCard";
import Pagination from "./components/Pagination";
import AssessmentDetailModal from "./components/AssessmentDetailModal";
import "./AssessmentHistoryPage.css";

const AssessmentHistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<
    number | null
  >(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const { assessments, loading, error, pagination, fetchAssessments, refresh } =
    useAssessments({
      page: currentPage,
      pageSize: pageSize,
      autoFetch: true,
    });

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    fetchAssessments(page, pageSize);
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1);
    fetchAssessments(1, newPageSize);
  };

  const handleAssessmentClick = (assessment: Assessment) => {
    setSelectedAssessmentId(assessment.id);
    setShowDetailModal(true);
  };

  const handleCloseModal = () => {
    setShowDetailModal(false);
    setSelectedAssessmentId(null);
  };

  const handleNewAssessment = () => {
    navigate("/assessment");
  };

  return (
    <MainLayout>
      <div className="assessment-history-page">
        {/* Header */}
        <div className="page-header">
          <div className="header-content">
            <h1 className="page-title">Lịch sử đánh giá GAD-7</h1>
            <p className="page-subtitle">
              Xem lại các lần đánh giá tình trạng lo âu của bạn
            </p>
          </div>
          <div className="header-actions">
            <button onClick={handleNewAssessment} className="btn btn-primary">
              <span className="btn-icon">+</span>
              Đánh giá mới
            </button>
            <button
              onClick={refresh}
              className="btn btn-outline"
              disabled={loading}
            >
              <span className="btn-icon">🔄</span>
              Làm mới
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="page-content">
          {/* Statistics Summary */}
          {assessments.length > 0 && (
            <div className="stats-summary">
              <div className="stat-item">
                <span className="stat-number">{pagination.total}</span>
                <span className="stat-label">Tổng số lần đánh giá</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {assessments.length > 0
                    ? Math.round(
                        (assessments.reduce(
                          (sum, a) => sum + a.total_score,
                          0
                        ) /
                          assessments.length) *
                          10
                      ) / 10
                    : 0}
                </span>
                <span className="stat-label">Điểm trung bình (trang này)</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {assessments[0]?.total_score || 0}
                </span>
                <span className="stat-label">Điểm gần nhất</span>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Đang tải danh sách đánh giá...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h3>Không thể tải danh sách đánh giá</h3>
              <p>{error}</p>
              <button onClick={refresh} className="btn btn-primary">
                Thử lại
              </button>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && assessments.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <h3>Chưa có đánh giá nào</h3>
              <p>
                Bạn chưa thực hiện đánh giá GAD-7 nào. Hãy bắt đầu đánh giá đầu
                tiên!
              </p>
              <button onClick={handleNewAssessment} className="btn btn-primary">
                Bắt đầu đánh giá GAD-7
              </button>
            </div>
          )}

          {/* Assessment List */}
          {!loading && !error && assessments.length > 0 && (
            <>
              <div className="assessments-list">
                {assessments.map((assessment) => (
                  <AssessmentCard
                    key={assessment.id}
                    assessment={assessment}
                    onClick={handleAssessmentClick}
                    showVoiceAnalysis={false} // TODO: Check if has voice analysis
                  />
                ))}
              </div>

              {/* Pagination */}
              <Pagination
                currentPage={pagination.page}
                totalPages={pagination.totalPages}
                totalItems={pagination.total}
                pageSize={pagination.pageSize}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
                loading={loading}
              />
            </>
          )}
        </div>

        {/* Assessment Detail Modal */}
        <AssessmentDetailModal
          isOpen={showDetailModal}
          assessmentId={selectedAssessmentId}
          onClose={handleCloseModal}
        />
      </div>
    </MainLayout>
  );
};

export default AssessmentHistoryPage;
