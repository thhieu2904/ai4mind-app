/**
 * Severity Distribution Chart - Biểu đồ phân bố mức độ nghiêm trọng
 */
import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import "./SeverityDistributionChart.css";

interface SeverityDistributionChartProps {
  data: Array<{
    severity: string;
    count: number;
  }>;
  loading?: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  "Không có": "#10b981",
  Nhẹ: "#3b82f6",
  "Trung bình": "#f59e0b",
  Nặng: "#ef4444",
};

const SEVERITY_LABELS: Record<string, string> = {
  none: "Không có",
  mild: "Nhẹ",
  moderate: "Trung bình",
  severe: "Nặng",
};

const SeverityDistributionChart: React.FC<SeverityDistributionChartProps> = ({
  data,
  loading = false,
}) => {
  // Normalize data and translate severity levels
  const normalizedData = data
    .map((item) => ({
      name: SEVERITY_LABELS[item.severity] || item.severity,
      value: item.count,
      severity: item.severity,
    }))
    .filter((item) => item.value > 0);

  const total = normalizedData.reduce((sum, item) => sum + item.value, 0);

  // Custom label for pie chart
  const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos((-midAngle * Math.PI) / 180);
    const y = cy + radius * Math.sin((-midAngle * Math.PI) / 180);

    if (percent < 0.05) return null; // Hide labels for small slices

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        style={{ fontWeight: "bold", fontSize: "0.875rem" }}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{data.name}</p>
          <p className="tooltip-value">
            <strong>{data.value}</strong> lần
            {total > 0 && (
              <span className="tooltip-percent">
                ({((data.value / total) * 100).toFixed(1)}%)
              </span>
            )}
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
          <h3 className="chart-title">Phân bố mức độ lo âu</h3>
        </div>
        <div className="chart-skeleton">
          <div className="skeleton-circle"></div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0 || total === 0) {
    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3 className="chart-title">Phân bố mức độ lo âu</h3>
        </div>
        <div className="chart-empty">
          <div className="empty-icon">📊</div>
          <p>Chưa có dữ liệu để hiển thị biểu đồ</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3 className="chart-title">Phân bố mức độ lo âu</h3>
        <p className="chart-subtitle">Tỷ lệ các mức độ trong tất cả đánh giá</p>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={normalizedData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {normalizedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={SEVERITY_COLORS[entry.name] || "#94a3b8"}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              wrapperStyle={{ fontSize: "0.875rem", paddingTop: "10px" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="severity-summary">
        {normalizedData.map((item) => (
          <div key={item.name} className="severity-item">
            <div
              className="severity-color"
              style={{ background: SEVERITY_COLORS[item.name] }}
            ></div>
            <div className="severity-info">
              <span className="severity-label">{item.name}</span>
              <span className="severity-count">
                {item.value} lần
                {total > 0 && (
                  <span className="severity-percent">
                    ({((item.value / total) * 100).toFixed(1)}%)
                  </span>
                )}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SeverityDistributionChart;
