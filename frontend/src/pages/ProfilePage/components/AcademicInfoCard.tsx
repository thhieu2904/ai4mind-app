/**
 * Academic Info Card - Hiển thị thông tin học tập
 */
import React from "react";
import type { StudentProfile } from "../../../services/userService";
import "./AcademicInfoCard.css";

interface AcademicInfoCardProps {
  studentProfile?: StudentProfile;
  loading?: boolean;
}

const AcademicInfoCard: React.FC<AcademicInfoCardProps> = ({
  studentProfile,
  loading = false,
}) => {
  const getEducationLabel = (level?: string, grade?: string) => {
    if (!level && !grade) return "Chưa cập nhật";

    const levelLabels: Record<string, string> = {
      high_school: "THPT",
      undergraduate: "Đại học",
      graduate: "Sau đại học",
      other: "Khác",
    };

    const levelLabel = level ? levelLabels[level] || level : "";
    const gradeLabel = grade ? `- Lớp ${grade}` : "";

    return `${levelLabel} ${gradeLabel}`.trim();
  };

  if (loading) {
    return (
      <div className="academic-info-card">
        <div className="card-skeleton">
          <div className="skeleton-line"></div>
          <div className="skeleton-line"></div>
          <div className="skeleton-line short"></div>
        </div>
      </div>
    );
  }

  if (!studentProfile) {
    return null;
  }

  const hasAcademicInfo =
    studentProfile.university ||
    studentProfile.major ||
    studentProfile.education_level ||
    studentProfile.grade;

  const hasEmergencyContact = studentProfile.parent_email;

  if (!hasAcademicInfo && !hasEmergencyContact) {
    return (
      <div className="academic-info-card">
        <div className="card-header">
          <h3 className="card-title">Thông tin học tập</h3>
        </div>
        <div className="empty-state">
          <p>Chưa có thông tin học tập</p>
        </div>
      </div>
    );
  }

  return (
    <div className="academic-info-card">
      {/* Academic Information */}
      {hasAcademicInfo && (
        <>
          <div className="card-header">
            <h3 className="card-title">Thông tin học tập</h3>
          </div>

          <div className="card-content">
            <div className="info-grid">
              {studentProfile.university && (
                <div className="info-item">
                  <span className="info-label">🏫 Trường</span>
                  <span className="info-value">
                    {studentProfile.university}
                  </span>
                </div>
              )}

              {studentProfile.major && (
                <div className="info-item">
                  <span className="info-label">📚 Chuyên ngành</span>
                  <span className="info-value">{studentProfile.major}</span>
                </div>
              )}

              {(studentProfile.education_level || studentProfile.grade) && (
                <div className="info-item">
                  <span className="info-label">📅 Cấp học</span>
                  <span className="info-value">
                    {getEducationLabel(
                      studentProfile.education_level,
                      studentProfile.grade
                    )}
                  </span>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Emergency Contact */}
      {hasEmergencyContact && (
        <>
          <div
            className="card-header"
            style={{ marginTop: hasAcademicInfo ? "1.5rem" : "0" }}
          >
            <h3 className="card-title">Liên hệ khẩn cấp</h3>
          </div>

          <div className="card-content">
            <div className="emergency-contact">
              <div className="emergency-icon">🚨</div>
              <div className="emergency-info">
                {studentProfile.parent_email && (
                  <div className="info-row">
                    <span className="info-label">📧 Email phụ huynh:</span>
                    <span className="info-value">
                      {studentProfile.parent_email}
                    </span>
                  </div>
                )}

                {!studentProfile.parent_email && (
                  <div className="info-row">
                    <span className="info-label" style={{ color: "#999" }}>
                      Chưa cập nhật email phụ huynh
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AcademicInfoCard;
