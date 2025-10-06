import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import type {
  UserProfile,
  StudentProfile,
} from "../../../services/userService";
import AlertModal, { AlertType } from "../../../components/AlertModal";
import "./EditProfileModal.css";

interface EditProfileFormData {
  full_name: string;
  phone?: string;
  date_of_birth?: string;
  gender?: "male" | "female" | "other" | "prefer_not_to_say";
  address?: string;
  university?: string;
  major?: string;
  education_level?: "high_school" | "undergraduate" | "graduate" | "other";
  grade?: string;
  parent_email?: string; // Emergency contact parent email
}

interface EditProfileModalProps {
  isOpen: boolean;
  user: UserProfile;
  studentProfile?: StudentProfile;
  onClose: () => void;
  onSave: (data: EditProfileFormData) => Promise<void>;
  loading?: boolean;
}

const EditProfileModal: React.FC<EditProfileModalProps> = ({
  isOpen,
  user,
  studentProfile,
  onClose,
  onSave,
  loading = false,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<EditProfileFormData>();

  const [alertModal, setAlertModal] = useState<{
    open: boolean;
    type: AlertType;
    title: string;
    message: string;
  }>({
    open: false,
    type: "info",
    title: "",
    message: "",
  });

  const showAlert = (type: AlertType, title: string, message: string) => {
    setAlertModal({ open: true, type, title, message });
  };

  const closeAlert = () => {
    setAlertModal({ ...alertModal, open: false });
  };

  useEffect(() => {
    if (isOpen) {
      reset({
        full_name: user.full_name,
        phone: user.phone || studentProfile?.phone_number || "",
        date_of_birth: studentProfile?.date_of_birth || "",
        gender: studentProfile?.gender || "prefer_not_to_say",
        address: studentProfile?.address || "",
        university: studentProfile?.university || "",
        major: studentProfile?.major || "",
        education_level: studentProfile?.education_level || undefined,
        grade: studentProfile?.grade || "",
        parent_email: studentProfile?.parent_email || "",
      });
    }
  }, [isOpen, user, studentProfile, reset]);

  const onSubmit = async (data: EditProfileFormData) => {
    try {
      // Frontend validation for parent email
      if (data.parent_email) {
        const parentEmail = data.parent_email.trim().toLowerCase();

        // Check if using own email
        if (parentEmail === user.email.toLowerCase()) {
          showAlert(
            "error",
            "Email không hợp lệ",
            "Không thể sử dụng email của chính bạn làm email phụ huynh. Vui lòng nhập email khác."
          );
          return;
        }

        // Validate email format
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(parentEmail)) {
          showAlert(
            "error",
            "Email không hợp lệ",
            "Vui lòng nhập địa chỉ email hợp lệ cho phụ huynh."
          );
          return;
        }

        data.parent_email = parentEmail; // Normalize email
      }

      await onSave(data);
      onClose();
    } catch (error: any) {
      console.error("Error saving profile:", error);

      // Handle backend validation errors
      if (error.response?.data?.detail) {
        const errorMessage = error.response.data.detail;
        showAlert("error", "Không thể cập nhật", errorMessage);
      } else {
        showAlert(
          "error",
          "Lỗi",
          "Đã xảy ra lỗi khi cập nhật thông tin. Vui lòng thử lại."
        );
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Chỉnh sửa thông tin</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="modal-body">
          {/* Personal Information */}
          <div className="form-section">
            <h3 className="section-title">Thông tin cơ bản</h3>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Họ và tên <span className="required">*</span>
                </label>
                <input
                  type="text"
                  className={`form-input ${errors.full_name ? "error" : ""}`}
                  {...register("full_name", {
                    required: "Vui lòng nhập họ tên",
                  })}
                />
                {errors.full_name && (
                  <span className="error-message">
                    {errors.full_name.message}
                  </span>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Số điện thoại</label>
                <input
                  type="tel"
                  className="form-input"
                  placeholder="0123456789"
                  {...register("phone", {
                    pattern: {
                      value: /^[0-9]{10,11}$/,
                      message: "Số điện thoại không hợp lệ",
                    },
                  })}
                />
                {errors.phone && (
                  <span className="error-message">{errors.phone.message}</span>
                )}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Ngày sinh</label>
                <input
                  type="date"
                  className="form-input"
                  {...register("date_of_birth")}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Giới tính</label>
                <select className="form-input" {...register("gender")}>
                  <option value="prefer_not_to_say">Không muốn tiết lộ</option>
                  <option value="male">Nam</option>
                  <option value="female">Nữ</option>
                  <option value="other">Khác</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Địa chỉ</label>
              <textarea
                className="form-input"
                rows={3}
                placeholder="Nhập địa chỉ của bạn"
                {...register("address")}
              />
            </div>
          </div>

          {/* Academic Information */}
          <div className="form-section">
            <h3 className="section-title">Thông tin học tập</h3>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Trường</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Tên trường đại học"
                  {...register("university")}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Chuyên ngành</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Tên chuyên ngành"
                  {...register("major")}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Cấp học</label>
                <select className="form-input" {...register("education_level")}>
                  <option value="">Chọn cấp học</option>
                  <option value="high_school">THPT</option>
                  <option value="undergraduate">Đại học</option>
                  <option value="graduate">Sau đại học</option>
                  <option value="other">Khác</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Lớp/Năm</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Ví dụ: 10, 11, 12, 1, 2, 3, 4, 5"
                  {...register("grade")}
                />
              </div>
            </div>
          </div>

          {/* Emergency Contact */}
          <div className="form-section">
            <h3 className="section-title">Liên hệ khẩn cấp</h3>

            <div className="form-group">
              <label className="form-label">
                Email phụ huynh{" "}
                <span className="important-badge">⚠️ Quan trọng</span>
              </label>
              <input
                type="email"
                className="form-input"
                placeholder="phu.huynh@example.com"
                {...register("parent_email", {
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Email không hợp lệ",
                  },
                })}
              />
              {errors.parent_email && (
                <span className="error-message">
                  {errors.parent_email.message}
                </span>
              )}
              <div className="field-hint">
                <small>
                  🔒 Email phụ huynh sẽ được dùng để liên hệ khẩn cấp. Nếu chưa
                  có tài khoản, hệ thống sẽ tự động tạo.
                </small>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Hủy
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting || loading}
            >
              {isSubmitting ? "Đang lưu..." : "Lưu thay đổi"}
            </button>
          </div>
        </form>
      </div>

      {/* Alert Modal */}
      <AlertModal
        open={alertModal.open}
        onClose={closeAlert}
        type={alertModal.type}
        title={alertModal.title}
        message={alertModal.message}
        confirmText="Đã hiểu"
      />
    </div>
  );
};

export default EditProfileModal;
