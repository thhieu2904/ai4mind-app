/**
 * Assessment History Page - Trang lịch sử các lần đánh giá GAD-7
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAssessments } from "../../hooks/useAssessments";
import { type Assessment } from "../../services/assessmentService";
import MainLayout from "../../components/layout/MainLayout";
import PageHeaderCard from "../../components/common/PageHeaderCard";
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
        {/* Page Header */}
        <PageHeaderCard
          icon="📋"
          title="Lịch sử đánh giá GAD-7"
          subtitle="Theo dõi tình trạng lo âu"
          description={
            <div className="history-header-info">
              <span className="info-item">
                📊 Xem lại các lần đánh giá tình trạng lo âu của bạn
              </span>
              {pagination && (
                <span className="info-item">
                  📝 Tổng số: <strong>{pagination.total}</strong> lần đánh giá
                </span>
              )}
            </div>
          }
          actions={
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button
                onClick={handleNewAssessment}
                className="btn btn-primary"
                style={{ padding: "0.75rem 1.5rem" }}
              >
                <span className="btn-icon">+</span>
                Đánh giá mới
              </button>
              <button
                onClick={refresh}
                className="btn btn-outline"
                disabled={loading}
                style={{ padding: "0.75rem 1.5rem" }}
              >
                <span className="btn-icon">🔄</span>
                Làm mới
              </button>
            </div>
          }
          variant="primary"
          gradient
        />

        {/* Content */}
        <div className="page-content">
          {/* Loading State */}
          {loading && assessments.length === 0 && (
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
