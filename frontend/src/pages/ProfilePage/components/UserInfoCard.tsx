/**
 * User Info Card - Hiển thị thông tin cơ bản của user
 */
import React from "react";
import { format } from "date-fns";
import { vi } from "date-fns/locale";
import type {
  UserProfile,
  StudentProfile,
} from "../../../services/userService";
import "./UserInfoCard.css";

interface UserInfoCardProps {
  user: UserProfile;
  studentProfile?: StudentProfile;
  onEdit: () => void;
  loading?: boolean;
}

const UserInfoCard: React.FC<UserInfoCardProps> = ({
  user,
  studentProfile,
  onEdit,
  loading = false,
}) => {
  const getGenderLabel = (gender?: string) => {
    const labels: Record<string, string> = {
      male: "Nam",
      female: "Nữ",
      other: "Khác",
      prefer_not_to_say: "Không muốn tiết lộ",
    };
    return gender ? labels[gender] || "Chưa cập nhật" : "Chưa cập nhật";
  };

  const getRoleLabel = (role: string) => {
    const labels: Record<string, string> = {
      student: "Sinh viên",
      parent: "Phụ huynh",
      counselor: "Tư vấn viên",
      admin: "Quản trị viên",
    };
    return labels[role] || role;
  };

  const getAvatarInitials = () => {
    const names = user.full_name.split(" ");
    if (names.length >= 2) {
      return names[0][0] + names[names.length - 1][0];
    }
    return user.full_name.substring(0, 2);
  };

  if (loading) {
    return (
      <div className="user-info-card">
        <div className="card-skeleton">
          <div className="skeleton-avatar"></div>
          <div className="skeleton-content">
            <div className="skeleton-line"></div>
            <div className="skeleton-line short"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-info-card">
      <div className="card-header">
        <h3 className="card-title">Thông tin cá nhân</h3>
      </div>

      <div className="card-content">
        {/* Avatar Section */}
        <div className="avatar-section">
          <div className="avatar">{getAvatarInitials().toUpperCase()}</div>
          <div className="avatar-info">
            <h2 className="user-name">{user.full_name}</h2>
            <span className="user-role">{getRoleLabel(user.role)}</span>
          </div>
        </div>

        {/* Info Grid */}
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">📧 Email</span>
            <span className="info-value">{user.email}</span>
          </div>

          <div className="info-item">
            <span className="info-label">📱 Số điện thoại</span>
            <span className="info-value">
              {user.phone || studentProfile?.phone_number || "Chưa cập nhật"}
            </span>
          </div>

          {studentProfile?.student_code && (
            <div className="info-item">
              <span className="info-label">🎓 Mã sinh viên</span>
              <span className="info-value">{studentProfile.student_code}</span>
            </div>
          )}

          {studentProfile?.gender && (
            <div className="info-item">
              <span className="info-label">👤 Giới tính</span>
              <span className="info-value">
                {getGenderLabel(studentProfile.gender)}
              </span>
            </div>
          )}

          {studentProfile?.date_of_birth && (
            <div className="info-item">
              <span className="info-label">🎂 Ngày sinh</span>
              <span className="info-value">
                {format(new Date(studentProfile.date_of_birth), "dd/MM/yyyy", {
                  locale: vi,
                })}
              </span>
            </div>
          )}

          {studentProfile?.address && (
            <div className="info-item full-width">
              <span className="info-label">📍 Địa chỉ</span>
              <span className="info-value">{studentProfile.address}</span>
            </div>
          )}
          <button className="edit-btn" onClick={onEdit}>
            ✏️ Chỉnh sửa
          </button>
        </div>

        {/* Account Status */}
        <div className="account-status">
          <div className="status-badge">
            <span
              className={`status-dot ${user.is_active ? "active" : "inactive"}`}
            ></span>
            <span className="status-text">
              {user.is_active
                ? "Tài khoản đang hoạt động"
                : "Tài khoản không hoạt động"}
            </span>
          </div>
          {user.created_at && (
            <div className="member-since">
              Tham gia từ{" "}
              {format(new Date(user.created_at), "dd/MM/yyyy", { locale: vi })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserInfoCard;
