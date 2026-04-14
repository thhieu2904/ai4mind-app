import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import MainLayout from "../../components/layout/MainLayout";
import AdminService, { AdminUser } from "../../services/adminService";
import "./AdminDashboardPage.css";

interface DashboardStats {
  total: number;
  students: number;
  counselors: number;
  admins: number;
  active: number;
  inactive: number;
}

const EMPTY_STATS: DashboardStats = {
  total: 0,
  students: 0,
  counselors: 0,
  admins: 0,
  active: 0,
  inactive: 0,
};

const AdminDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>(EMPTY_STATS);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState("");

  useEffect(() => {
    void loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const allUsers: AdminUser[] = await AdminService.listUsers();
      const students = allUsers.filter((u) => u.role === "STUDENT").length;
      const counselors = allUsers.filter((u) => u.role === "COUNSELOR").length;
      const admins = allUsers.filter((u) => u.role === "ADMIN").length;
      const active = allUsers.filter((u) => u.is_active).length;
      const inactive = allUsers.length - active;
      setStats({ total: allUsers.length, students, counselors, admins, active, inactive });
      setLastUpdated(
        new Date().toLocaleTimeString("vi-VN", {
          hour: "2-digit",
          minute: "2-digit",
        })
      );
    } catch (err) {
      console.error("Failed to load stats", err);
    } finally {
      setLoading(false);
    }
  };

  const activeRate = stats.total > 0 ? Math.round((stats.active / stats.total) * 100) : 0;

  const statCards = [
    { key: "total", label: "Tổng tài khoản", tone: "total", icon: "📊", value: stats.total },
    { key: "students", label: "Học sinh", tone: "student", icon: "🎓", value: stats.students },
    { key: "counselors", label: "Tư vấn viên", tone: "counselor", icon: "🧑‍⚕️", value: stats.counselors },
    { key: "admins", label: "Quản trị viên", tone: "admin", icon: "🛡️", value: stats.admins },
    { key: "active", label: "Đang hoạt động", tone: "active", icon: "✅", value: stats.active },
    { key: "inactive", label: "Tạm khóa", tone: "inactive", icon: "⏸️", value: stats.inactive },
  ];

  const quickActions = [
    {
      icon: "👥",
      label: "Quản lý người dùng",
      description: "Xem toàn bộ danh sách và thao tác nhanh",
      onClick: () => navigate("/admin/users"),
    },
    {
      icon: "🧑‍⚕️",
      label: "Nhóm tư vấn viên",
      description: "Lọc nhanh các tài khoản COUNSELOR",
      onClick: () => navigate("/admin/users?role=COUNSELOR"),
    },
    {
      icon: "🎓",
      label: "Nhóm học sinh",
      description: "Lọc nhanh các tài khoản STUDENT",
      onClick: () => navigate("/admin/users?role=STUDENT"),
    },
  ];

  return (
    <MainLayout>
      <div className="admin-dashboard">
        <div className="admin-dashboard__hero">
          <div className="admin-dashboard__identity">
            <div className="admin-dashboard__avatar">{(user?.full_name || "Admin").trim().charAt(0).toUpperCase()}</div>
            <div>
              <h2 className="admin-dashboard__name">{user?.full_name || "Admin"}</h2>
              <p className="admin-dashboard__role">Bảng điều khiển quản trị</p>
            </div>
          </div>
          <button className="admin-dashboard__refresh" onClick={loadStats} disabled={loading}>
            {loading ? "Đang tải..." : "Làm mới"}
          </button>
        </div>

        <p className="admin-dashboard__updated">
          Cập nhật gần nhất: {lastUpdated || "--:--"}
        </p>

        <div className="admin-dashboard__spotlight">
          <div className="admin-dashboard__spotlight-head">
            <span className="admin-dashboard__spotlight-label">Tỷ lệ tài khoản hoạt động</span>
            <strong className="admin-dashboard__spotlight-value">{activeRate}%</strong>
          </div>
          <div className="admin-dashboard__progress-track">
            <span className="admin-dashboard__progress-fill" style={{ width: `${activeRate}%` }} />
          </div>
        </div>

        <h3 className="admin-dashboard__section-title">Tổng quan tài khoản</h3>

        {loading ? (
          <div className="admin-dashboard__cards admin-dashboard__cards--loading">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="admin-stat-card admin-stat-card--skeleton" />
            ))}
          </div>
        ) : (
          <div className="admin-dashboard__cards">
            {statCards.map((card) => (
              <div key={card.key} className={`admin-stat-card admin-stat-card--${card.tone}`}>
                <span className="admin-stat-card__icon">{card.icon}</span>
                <span className="admin-stat-card__number">{card.value}</span>
                <span className="admin-stat-card__label">{card.label}</span>
              </div>
            ))}
          </div>
        )}

        <h3 className="admin-dashboard__section-title">Thao tác nhanh</h3>
        <div className="admin-dashboard__actions-grid">
          {quickActions.map((action) => (
            <button key={action.label} className="admin-action-btn" onClick={action.onClick}>
              <span className="admin-action-btn__icon">{action.icon}</span>
              <span className="admin-action-btn__content">
                <span className="admin-action-btn__label">{action.label}</span>
                <span className="admin-action-btn__desc">{action.description}</span>
              </span>
              <span className="admin-action-btn__arrow">›</span>
            </button>
          ))}
        </div>

        {!loading && stats.total === 0 && (
          <div className="admin-dashboard__loading">Chưa có dữ liệu người dùng để hiển thị.</div>
        )}
      </div>
    </MainLayout>
  );
};

export default AdminDashboardPage;
