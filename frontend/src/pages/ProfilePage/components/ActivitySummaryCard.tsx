/**
 * Activity Summary Card - Hiển thị tóm tắt hoạt động
 */
import React from "react";
import { format } from "date-fns";
import { vi } from "date-fns/locale";
import "./ActivitySummaryCard.css";

interface ActivitySummaryCardProps {
  totalAssessments: number;
  lastAssessmentDate?: string;
  memberSince?: string; // Make optional
  loading?: boolean;
}

const ActivitySummaryCard: React.FC<ActivitySummaryCardProps> = ({
  totalAssessments,
  lastAssessmentDate,
  memberSince,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="activity-summary-card">
        <div className="card-skeleton">
          <div className="skeleton-line"></div>
          <div className="skeleton-line"></div>
          <div className="skeleton-line short"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="activity-summary-card">
      <div className="card-header">
        <h3 className="card-title">Hoạt động</h3>
      </div>

      <div className="card-content">
        <div className="activity-stats">
          {/* Total Assessments */}
          <div className="stat-item">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">{totalAssessments}</div>
              <div className="stat-label">Lần đánh giá</div>
            </div>
          </div>

          {/* Last Assessment */}
          <div className="stat-item">
            <div className="stat-icon">📅</div>
            <div className="stat-content">
              <div className="stat-value">
                {lastAssessmentDate
                  ? format(new Date(lastAssessmentDate), "dd/MM/yyyy", {
                      locale: vi,
                    })
                  : "Chưa có"}
              </div>
              <div className="stat-label">Đánh giá gần nhất</div>
            </div>
          </div>

          {/* Member Since */}
          <div className="stat-item">
            <div className="stat-icon">⭐</div>
            <div className="stat-content">
              <div className="stat-value">
                {memberSince && memberSince.trim() !== ""
                  ? format(new Date(memberSince), "dd/MM/yyyy", { locale: vi })
                  : "Chưa có"}
              </div>
              <div className="stat-label">Thành viên từ</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <div className="action-label">Thao tác nhanh</div>
          <div className="actions-grid">
            <a href="/assessment" className="action-btn">
              <span className="action-icon">📝</span>
              <span className="action-text">Đánh giá mới</span>
            </a>
            <a href="/history" className="action-btn">
              <span className="action-icon">📋</span>
              <span className="action-text">Lịch sử</span>
            </a>
            <a href="/statistics" className="action-btn">
              <span className="action-icon">📈</span>
              <span className="action-text">Thống kê</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivitySummaryCard;
