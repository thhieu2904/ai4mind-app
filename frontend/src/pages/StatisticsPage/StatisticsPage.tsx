/**
 * Statistics Page - Trang thống kê và phân tích GAD-7
 */
import React, { useState, useEffect } from "react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeaderCard from "../../components/common/PageHeaderCard";
import OverviewCards from "./components/OverviewCards";
import ScoreTrendChart from "./components/ScoreTrendChart";
import SeverityDistributionChart from "./components/SeverityDistributionChart";
import { AssessmentService } from "../../services/assessmentService";
import type { AssessmentStats } from "../../services/assessmentService";
import "./StatisticsPage.css";

type TimePeriod = "7days" | "30days" | "3months" | "all";

const StatisticsPage: React.FC = () => {
  const [stats, setStats] = useState<AssessmentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timePeriod, setTimePeriod] = useState<TimePeriod>("all");

  useEffect(() => {
    fetchStatistics();
  }, [timePeriod]);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await AssessmentService.getStats();
      setStats(data);
    } catch (err: any) {
      console.error("Error fetching statistics:", err);
      setError(err.message || "Không thể tải thống kê");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchStatistics();
  };

  // Calculate severity distribution from score history
  const getSeverityDistribution = () => {
    if (!stats || !stats.score_history || stats.score_history.length === 0) {
      return [];
    }

    const distribution: Record<string, number> = {
      none: 0,
      mild: 0,
      moderate: 0,
      severe: 0,
    };

    stats.score_history.forEach((item) => {
      const score = item.score;
      if (score < 5) {
        distribution["none"]++;
      } else if (score < 10) {
        distribution["mild"]++;
      } else if (score < 15) {
        distribution["moderate"]++;
      } else {
        distribution["severe"]++;
      }
    });

    return Object.entries(distribution).map(([severity, count]) => ({
      severity,
      count,
    }));
  };

  return (
    <MainLayout>
      <div className="statistics-page">
        {/* Page Header */}
        <PageHeaderCard
          icon="📊"
          title="Thống kê & Phân tích"
          subtitle="Theo dõi tiến trình sức khỏe tâm lý"
          description={
            <div className="statistics-header-info">
              <span className="info-item">
                📈 Dữ liệu từ các bài đánh giá GAD-7 của bạn
              </span>
              {stats && stats.total_assessments > 0 && (
                <span className="info-item">
                  📋 Tổng số: <strong>{stats.total_assessments}</strong> lần
                  đánh giá
                </span>
              )}
            </div>
          }
          variant="primary"
          gradient
        />

        {/* Content */}
        <div className="page-content">
          {/* Time Period Filter */}
          <div className="filter-section">
            <div className="filter-label">Khoảng thời gian:</div>
            <div className="filter-options">
              <button
                className={`filter-btn ${timePeriod === "7days" ? "active" : ""}`}
                onClick={() => setTimePeriod("7days")}
                disabled={loading}
              >
                7 ngày
              </button>
              <button
                className={`filter-btn ${timePeriod === "30days" ? "active" : ""}`}
                onClick={() => setTimePeriod("30days")}
                disabled={loading}
              >
                30 ngày
              </button>
              <button
                className={`filter-btn ${timePeriod === "3months" ? "active" : ""}`}
                onClick={() => setTimePeriod("3months")}
                disabled={loading}
              >
                3 tháng
              </button>
              <button
                className={`filter-btn ${timePeriod === "all" ? "active" : ""}`}
                onClick={() => setTimePeriod("all")}
                disabled={loading}
              >
                Tất cả
              </button>
            </div>
            <button
              className="refresh-btn"
              onClick={handleRefresh}
              disabled={loading}
              title="Làm mới dữ liệu"
            >
              🔄
            </button>
          </div>

          {/* Error State */}
          {error && (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h3>Không thể tải thống kê</h3>
              <p>{error}</p>
              <button onClick={handleRefresh} className="btn btn-primary">
                Thử lại
              </button>
            </div>
          )}

          {/* Empty State - No assessments */}
          {!loading && !error && stats && stats.total_assessments === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>Chưa có dữ liệu thống kê</h3>
              <p>
                Bạn chưa thực hiện đánh giá GAD-7 nào trong khoảng thời gian
                này.
              </p>
              <p className="empty-hint">
                Hãy thực hiện đánh giá để xem thống kê của bạn!
              </p>
            </div>
          )}

          {/* Statistics Content */}
          {!error && stats && stats.total_assessments > 0 && (
            <>
              {/* Overview Cards */}
              <OverviewCards
                totalAssessments={stats.total_assessments}
                averageScore={stats.average_score}
                latestScore={stats.latest_score}
                trend={stats.trend}
                loading={loading}
              />

              {/* Charts Grid */}
              <div className="charts-grid">
                {/* Score Trend Chart */}
                <div className="chart-col">
                  <ScoreTrendChart
                    data={stats.score_history || []}
                    loading={loading}
                  />
                </div>

                {/* Severity Distribution Chart */}
                <div className="chart-col">
                  <SeverityDistributionChart
                    data={getSeverityDistribution()}
                    loading={loading}
                  />
                </div>
              </div>

              {/* Additional Info */}
              <div className="info-section">
                <div className="info-card">
                  <h4>💡 Thông tin hữu ích</h4>
                  <ul>
                    <li>
                      <strong>Theo dõi định kỳ:</strong> Thực hiện đánh giá
                      GAD-7 đều đặn để theo dõi sức khỏe tâm lý của bạn.
                    </li>
                    <li>
                      <strong>Xu hướng cải thiện:</strong> Nếu điểm số giảm dần
                      qua thời gian, đó là dấu hiệu tốt cho thấy tình trạng đang
                      cải thiện.
                    </li>
                    <li>
                      <strong>Tìm kiếm hỗ trợ:</strong> Nếu điểm số ở mức Trung
                      bình hoặc Nặng, hãy cân nhắc tìm kiếm sự hỗ trợ từ chuyên
                      gia tâm lý.
                    </li>
                  </ul>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default StatisticsPage;
