/**
 * Profile Page - Trang thông tin cá nhân
 */
import React, { useState, useEffect } from "react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeaderCard from "../../components/common/PageHeaderCard";
import UserInfoCard from "./components/UserInfoCard";
import AcademicInfoCard from "./components/AcademicInfoCard";
import ActivitySummaryCard from "./components/ActivitySummaryCard";
import EditProfileModal from "./components/EditProfileModal";
import { UserService } from "../../services/userService";
import { AssessmentService } from "../../services/assessmentService";
import type { UserProfile, StudentProfile } from "../../services/userService";
import "./ProfilePage.css";

const ProfilePage: React.FC = () => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [studentProfile, setStudentProfile] = useState<StudentProfile | null>(
    null
  );
  const [totalAssessments, setTotalAssessments] = useState(0);
  const [lastAssessmentDate, setLastAssessmentDate] = useState<
    string | undefined
  >();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      setError(null);

      // For students, use /students/me which has all data including user info
      // This avoids the bug in /auth/me endpoint
      try {
        const studentData = await UserService.getStudentProfile();
        setStudentProfile(studentData);

        // Construct user profile from student data
        // Note: We could also call getCurrentUser() but students/me has everything we need
        setUser({
          id: studentData.user_id,
          email: studentData.email || "",
          full_name: studentData.full_name || "",
          role: "STUDENT",
          is_active: true,
          created_at: studentData.created_at || new Date().toISOString(),
          last_login: undefined,
          phone: studentData.phone_number,
          profile: studentData,
        });
      } catch (err) {
        console.log("Student profile not found, trying basic profile");
        // Fallback to /auth/me if students/me fails
        const userData = await UserService.getCurrentUser();
        setUser(userData);
      }

      // Fetch assessment stats for activity summary
      try {
        const stats = await AssessmentService.getStats();
        setTotalAssessments(stats.total_assessments);
        if (stats.score_history && stats.score_history.length > 0) {
          setLastAssessmentDate(stats.score_history[0].date);
        }
      } catch (err) {
        console.log("Assessment stats not available");
      }
    } catch (err: any) {
      console.error("Error fetching profile:", err);
      setError(err.message || "Không thể tải thông tin cá nhân");
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = () => {
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
  };

  const handleSaveProfile = async (data: any) => {
    try {
      setSaveLoading(true);

      // Update student profile (single API call with all data including full_name)
      if (user?.role === "STUDENT") {
        const studentData: Partial<StudentProfile> & { full_name?: string } = {
          full_name: data.full_name, // Include user basic info
          date_of_birth: data.date_of_birth,
          gender: data.gender,
          phone_number: data.phone,
          address: data.address,
          university: data.university,
          major: data.major,
          education_level: data.education_level,
          grade: data.grade,
          parent_email: data.parent_email, // Pass parent email to backend
        };

        const updatedStudentProfile =
          await UserService.updateStudentProfile(studentData);
        setStudentProfile(updatedStudentProfile);

        // Update user info in state
        if (data.full_name || data.phone) {
          setUser((prev) =>
            prev
              ? {
                  ...prev,
                  full_name: data.full_name || prev.full_name,
                  phone: data.phone || prev.phone,
                }
              : null
          );
        }
      }

      // Refresh profile data
      await fetchProfileData();
    } catch (err: any) {
      console.error("Error saving profile:", err);
      throw err;
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="profile-page">
        {/* Page Header */}
        <PageHeaderCard
          icon="👤"
          title="Thông tin cá nhân"
          subtitle={user ? `Xin chào, ${user.full_name}` : "Quản lý hồ sơ"}
          description={
            <div className="profile-header-info">
              <span className="info-item">
                📧 {user?.email || "Đang tải..."}
              </span>
              {studentProfile && (
                <>
                  {studentProfile.university && (
                    <span className="info-item">
                      🎓 {studentProfile.university}
                    </span>
                  )}
                  {studentProfile.major && (
                    <span className="info-item">📚 {studentProfile.major}</span>
                  )}
                </>
              )}
            </div>
          }
          actions={
            !loading &&
            user && (
              <button
                onClick={handleEditProfile}
                className="btn btn-primary"
                style={{ padding: "0.75rem 1.5rem" }}
              >
                ✏️ Chỉnh sửa
              </button>
            )
          }
          variant="primary"
          gradient
        />

        {/* Content */}
        <div className="page-content">
          {/* Loading State */}
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Đang tải thông tin...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h3>Không thể tải thông tin cá nhân</h3>
              <p>{error}</p>
              <button onClick={fetchProfileData} className="btn btn-primary">
                Thử lại
              </button>
            </div>
          )}

          {/* Profile Content */}
          {!loading && !error && user && (
            <div className="profile-grid">
              {/* Left Column */}
              <div className="profile-col">
                <UserInfoCard
                  user={user}
                  studentProfile={studentProfile || undefined}
                  onEdit={handleEditProfile}
                  loading={loading}
                />

                {user.role === "STUDENT" && (
                  <AcademicInfoCard
                    studentProfile={studentProfile || undefined}
                    loading={loading}
                  />
                )}
              </div>

              {/* Right Column */}
              <div className="profile-col">
                <ActivitySummaryCard
                  totalAssessments={totalAssessments}
                  lastAssessmentDate={lastAssessmentDate}
                  memberSince={user.created_at}
                  loading={loading}
                />
              </div>
            </div>
          )}
        </div>

        {/* Edit Profile Modal */}
        {user && (
          <EditProfileModal
            isOpen={showEditModal}
            user={user}
            studentProfile={studentProfile || undefined}
            onClose={handleCloseEditModal}
            onSave={handleSaveProfile}
            loading={saveLoading}
          />
        )}
      </div>
    </MainLayout>
  );
};

export default ProfilePage;
