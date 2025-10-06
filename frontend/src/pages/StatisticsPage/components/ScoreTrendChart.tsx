/**
 * Score Trend Chart - Biểu đồ xu hướng điểm GAD-7 theo thời gian
 */
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts";
import { format } from "date-fns";
import { vi } from "date-fns/locale";
import "./ScoreTrendChart.css";

interface ScoreDataPoint {
  date: string;
  score: number;
  severity: string;
}

interface ScoreTrendChartProps {
  data: ScoreDataPoint[];
  loading?: boolean;
}

const ScoreTrendChart: React.FC<ScoreTrendChartProps> = ({
  data,
  loading = false,
}) => {
  // Format data for chart
  const chartData = data.map((item) => ({
    ...item,
    formattedDate: format(new Date(item.date), "dd/MM", { locale: vi }),
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">
            {format(new Date(data.date), "dd/MM/yyyy", { locale: vi })}
          </p>
          <p className="tooltip-score">
            Điểm: <strong>{data.score}/21</strong>
          </p>
          <p className="tooltip-severity">
            Mức độ: <strong>{data.severity}</strong>
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3 className="chart-title">Xu hướng điểm GAD-7</h3>
        </div>
        <div className="chart-skeleton">
          <div className="skeleton-bars"></div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3 className="chart-title">Xu hướng điểm GAD-7</h3>
        </div>
        <div className="chart-empty">
          <div className="empty-icon">📊</div>
          <p>Chưa có dữ liệu để hiển thị biểu đồ</p>
          <p className="empty-hint">
            Thực hiện ít nhất 2 lần đánh giá để xem xu hướng
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3 className="chart-title">Xu hướng điểm GAD-7</h3>
        <p className="chart-subtitle">
          Theo dõi sự thay đổi điểm số qua thời gian
        </p>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="formattedDate"
              stroke="#64748b"
              style={{ fontSize: "0.875rem" }}
            />
            <YAxis
              domain={[0, 21]}
              ticks={[0, 5, 10, 15, 21]}
              stroke="#64748b"
              style={{ fontSize: "0.875rem" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: "20px", fontSize: "0.875rem" }}
            />

            {/* Reference lines for severity levels */}
            <ReferenceLine
              y={5}
              stroke="#10b981"
              strokeDasharray="5 5"
              label={{
                value: "Nhẹ (5)",
                position: "right",
                fill: "#10b981",
                fontSize: 12,
              }}
            />
            <ReferenceLine
              y={10}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              label={{
                value: "Trung bình (10)",
                position: "right",
                fill: "#f59e0b",
                fontSize: 12,
              }}
            />
            <ReferenceLine
              y={15}
              stroke="#ef4444"
              strokeDasharray="5 5"
              label={{
                value: "Nặng (15)",
                position: "right",
                fill: "#ef4444",
                fontSize: 12,
              }}
            />

            <Line
              type="monotone"
              dataKey="score"
              stroke="#667eea"
              strokeWidth={3}
              dot={{ fill: "#667eea", strokeWidth: 2, r: 5 }}
              activeDot={{ r: 7 }}
              name="Điểm GAD-7"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend-info">
        <div className="legend-item">
          <span
            className="legend-color"
            style={{ background: "#10b981" }}
          ></span>
          <span>Không có/Nhẹ (0-9)</span>
        </div>
        <div className="legend-item">
          <span
            className="legend-color"
            style={{ background: "#f59e0b" }}
          ></span>
          <span>Trung bình (10-14)</span>
        </div>
        <div className="legend-item">
          <span
            className="legend-color"
            style={{ background: "#ef4444" }}
          ></span>
          <span>Nặng (15-21)</span>
        </div>
      </div>
    </div>
  );
};

export default ScoreTrendChart;
