import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import MainLayout from "../../components/layout/MainLayout";
import AdminService, { AdminUser } from "../../services/adminService";
import "./AdminDashboardPage.css";

const AdminDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total: 0, students: 0, counselors: 0, admins: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const allUsers: AdminUser[] = await AdminService.listUsers();
      const students = allUsers.filter((u) => u.role === "STUDENT").length;
      const counselors = allUsers.filter((u) => u.role === "COUNSELOR").length;
      const admins = allUsers.filter((u) => u.role === "ADMIN").length;
      setStats({ total: allUsers.length, students, counselors, admins });
    } catch (err) {
      console.error("Failed to load stats", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="admin-dashboard">
        <div className="admin-dashboard__header">
          <div className="admin-dashboard__avatar">A</div>
          <div>
            <h2 className="admin-dashboard__name">{user?.full_name || "Admin"}</h2>
            <p className="admin-dashboard__role">Quản trị viên</p>
          </div>
        </div>

        <h3 className="admin-dashboard__section-title">Tổng quan</h3>

        {loading ? (
          <div className="admin-dashboard__loading">Đang tải...</div>
        ) : (
          <div className="admin-dashboard__cards">
            <div className="admin-stat-card admin-stat-card--total">
              <span className="admin-stat-card__number">{stats.total}</span>
              <span className="admin-stat-card__label">Tổng người dùng</span>
            </div>
            <div className="admin-stat-card admin-stat-card--student">
              <span className="admin-stat-card__number">{stats.students}</span>
              <span className="admin-stat-card__label">Học sinh</span>
            </div>
            <div className="admin-stat-card admin-stat-card--counselor">
              <span className="admin-stat-card__number">{stats.counselors}</span>
              <span className="admin-stat-card__label">Tư vấn viên</span>
            </div>
            <div className="admin-stat-card admin-stat-card--admin">
              <span className="admin-stat-card__number">{stats.admins}</span>
              <span className="admin-stat-card__label">Quản trị viên</span>
            </div>
          </div>
        )}

        <h3 className="admin-dashboard__section-title">Thao tác nhanh</h3>
        <div className="admin-dashboard__actions">
          <button
            className="admin-action-btn"
            onClick={() => navigate("/admin/users")}
          >
            <span className="admin-action-btn__icon">👥</span>
            <span className="admin-action-btn__label">Quản lý người dùng</span>
            <span className="admin-action-btn__arrow">›</span>
          </button>
          <button
            className="admin-action-btn"
            onClick={() => navigate("/admin/users?role=COUNSELOR")}
          >
            <span className="admin-action-btn__icon">🧑‍⚕️</span>
            <span className="admin-action-btn__label">Tư vấn viên</span>
            <span className="admin-action-btn__arrow">›</span>
          </button>
          <button
            className="admin-action-btn"
            onClick={() => navigate("/admin/users?role=STUDENT")}
          >
            <span className="admin-action-btn__icon">🎓</span>
            <span className="admin-action-btn__label">Học sinh</span>
            <span className="admin-action-btn__arrow">›</span>
          </button>
        </div>
      </div>
    </MainLayout>
  );
};

export default AdminDashboardPage;
