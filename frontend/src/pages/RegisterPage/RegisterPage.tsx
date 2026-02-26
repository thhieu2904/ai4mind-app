import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import type { RegisterRequest } from "../../types/auth";
import "./RegisterPage.css";

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState<RegisterRequest>({
    email: "",
    password: "",
    full_name: "",
    role: "STUDENT",
    date_of_birth: "",
    gender: undefined,
    phone: "",
    student_code: "",
    parent_email: "", // Emergency contact parent email
  });
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const validatePassword = (password: string): string | null => {
    if (password.length < 8) {
      return "Mật khẩu phải có ít nhất 8 ký tự";
    }
    if (!/[A-Z]/.test(password)) {
      return "Mật khẩu phải chứa ít nhất 1 chữ HOA";
    }
    if (!/[a-z]/.test(password)) {
      return "Mật khẩu phải chứa ít nhất 1 chữ thường";
    }
    if (!/\d/.test(password)) {
      return "Mật khẩu phải chứa ít nhất 1 chữ số";
    }
    return null;
  };

  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }
    return age;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (formData.password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp");
      return;
    }

    const passwordError = validatePassword(formData.password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    // Validate date of birth for students (important for GAD-7)
    if (formData.role === "STUDENT" && formData.date_of_birth) {
      const age = calculateAge(formData.date_of_birth);
      if (age < 13) {
        setError("Học sinh phải từ 13 tuổi trở lên");
        return;
      }
      if (age > 100) {
        setError("Ngày sinh không hợp lệ");
        return;
      }
    }

    // Student code is now optional - can be added later in profile
    // No validation needed here

    setLoading(true);

    try {
      // Clean up empty fields before sending to backend
      const cleanedData = { ...formData };

      // Remove empty parent_email to avoid validation error
      if (!cleanedData.parent_email || cleanedData.parent_email.trim() === "") {
        delete cleanedData.parent_email;
      }

      // Remove empty optional fields
      if (!cleanedData.student_code || cleanedData.student_code.trim() === "") {
        delete cleanedData.student_code;
      }

      await register(cleanedData);
      navigate("/dashboard");
    } catch (err: any) {
      // Parse backend validation errors
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // If detail is an array of validation errors (Pydantic format)
        if (Array.isArray(detail)) {
          const firstError = detail[0];
          setError(firstError.msg || firstError.message || "Đăng ký thất bại");
        }
        // If detail is a string
        else if (typeof detail === "string") {
          setError(detail);
        }
        // Fallback
        else {
          setError("Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.");
        }
      } else {
        setError("Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      <div className="register-card">
        <div className="register-header">
          <h1 className="register-title">Tạo tài khoản</h1>
          <p className="register-subtitle">
            Tham gia AI4Mind để được hỗ trợ sức khỏe tinh thần
          </p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          {error && (
            <div className="error-message">
              <svg
                className="error-icon"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Họ và tên
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="Nguyễn Văn A"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="your.email@example.com"
              disabled={loading}
            />
          </div>

          {/* Important for GAD-7 Assessment */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="date_of_birth" className="form-label">
                Ngày sinh <span className="important-badge">Quan trọng</span>
              </label>
              <input
                type="date"
                id="date_of_birth"
                name="date_of_birth"
                value={formData.date_of_birth || ""}
                onChange={handleChange}
                className="form-input"
                max={new Date().toISOString().split("T")[0]}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="gender" className="form-label">
                Giới tính <span className="important-badge">Quan trọng</span>
              </label>
              <select
                id="gender"
                name="gender"
                value={formData.gender || ""}
                onChange={handleChange}
                className="form-select"
                disabled={loading}
              >
                <option value="">Chọn giới tính</option>
                <option value="male">Nam</option>
                <option value="female">Nữ</option>
                <option value="other">Khác</option>
                <option value="prefer_not_to_say">Không muốn nói</option>
              </select>
            </div>
          </div>

          <div className="info-note">
            <small>
              📊 <strong>Ngày sinh</strong> và <strong>Giới tính</strong> giúp
              đánh giá GAD-7 chính xác hơn dựa trên nhóm tuổi và giới.
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="phone" className="form-label">
              Số điện thoại <span className="optional">(không bắt buộc)</span>
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone || ""}
              onChange={handleChange}
              className="form-input"
              placeholder="0912345678"
              disabled={loading}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Mật khẩu
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                className="form-input"
                placeholder="••••••••"
                disabled={loading}
              />
              <div className="password-hint">
                <small>
                  Ít nhất 8 ký tự, bao gồm chữ HOA, chữ thường và số
                </small>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">
                Xác nhận mật khẩu
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setError("");
                }}
                required
                className="form-input"
                placeholder="••••••••"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="role" className="form-label">
              Vai trò
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              className="form-select"
              disabled={loading}
            >
              <option value="STUDENT">Học sinh / Sinh viên</option>
              <option value="PARENT">Phụ huynh</option>
            </select>
          </div>

          {/* Student Code - Optional for students */}
          {formData.role === "STUDENT" && (
            <>
              <div className="form-group">
                <label htmlFor="student_code" className="form-label">
                  Mã sinh viên{" "}
                  <span className="optional">(không bắt buộc)</span>
                </label>
                <input
                  type="text"
                  id="student_code"
                  name="student_code"
                  value={formData.student_code || ""}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="SV12345"
                  disabled={loading}
                />
                <div className="field-hint">
                  <small>
                    💡 Mã sinh viên giúp trường/tư vấn viên dễ dàng tra cứu. Bạn
                    có thể thêm sau trong phần cài đặt.
                  </small>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="parent_email" className="form-label">
                  Email phụ huynh{" "}
                  <span className="important-badge">Liên hệ khẩn cấp</span>
                </label>
                <input
                  type="email"
                  id="parent_email"
                  name="parent_email"
                  value={formData.parent_email || ""}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="phu.huynh@example.com"
                  disabled={loading}
                />
                <div className="field-hint">
                  <small>
                    🔐 Email phụ huynh sẽ được dùng làm liên hệ khẩn cấp. Hệ
                    thống sẽ tự động tạo tài khoản cho phụ huynh nếu chưa tồn
                    tại.
                  </small>
                </div>
              </div>
            </>
          )}

          <div className="form-group">
            <label className="terms-label">
              <input
                type="checkbox"
                className="checkbox"
                required
                disabled={loading}
              />
              <span>
                Tôi đồng ý với{" "}
                <a href="/terms" className="terms-link" target="_blank">
                  Điều khoản sử dụng
                </a>{" "}
                và{" "}
                <a href="/privacy" className="terms-link" target="_blank">
                  Chính sách bảo mật
                </a>
              </span>
            </label>
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? <span className="loading-spinner"></span> : "Đăng ký"}
          </button>
        </form>

        <div className="register-footer">
          <p className="login-prompt">
            Đã có tài khoản?{" "}
            <Link to="/login" className="login-link">
              Đăng nhập ngay
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
