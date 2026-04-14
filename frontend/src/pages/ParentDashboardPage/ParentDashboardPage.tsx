import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import { ParentService, type ParentChild } from "../../services/parentService";
import "./ParentDashboardPage.css";

const SEVERITY_LABEL: Record<string, string> = {
  minimal: "Tich cuc",
  mild: "Can bang",
  moderate: "Can theo doi",
  severe: "Can uu tien ho tro",
};

const SEVERITY_CLASS: Record<string, string> = {
  minimal: "parent-severity parent-severity--minimal",
  mild: "parent-severity parent-severity--mild",
  moderate: "parent-severity parent-severity--moderate",
  severe: "parent-severity parent-severity--severe",
};

const formatDateTime = (value?: string): string => {
  if (!value) return "Chua co";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Khong hop le";
  return date.toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const ParentDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [children, setChildren] = useState<ParentChild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await ParentService.getMyChildren();
      setChildren(response.children || []);
    } catch (err: any) {
      console.error("Failed to load children", err);
      setError(
        err?.response?.data?.detail ||
          "Khong the tai du lieu phu huynh. Vui long thu lai."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="parent-dashboard">
        <section className="parent-dashboard__hero">
          <h1>Bang dieu khien phu huynh</h1>
          <p>
            Theo doi du lieu danh gia tam ly cua con theo cac ket noi da duoc lien
            ket trong he thong.
          </p>
        </section>

        <section className="parent-dashboard__section-header">
          <h2>Danh sach con lien ket ({children.length})</h2>
          <button onClick={loadChildren} className="parent-dashboard__refresh-btn">
            Lam moi
          </button>
        </section>

        {loading && (
          <div className="parent-dashboard__state-box">
            <p>Dang tai du lieu...</p>
          </div>
        )}

        {!loading && error && (
          <div className="parent-dashboard__state-box parent-dashboard__state-box--error">
            <p>{error}</p>
            <button onClick={loadChildren}>Thu lai</button>
          </div>
        )}

        {!loading && !error && children.length === 0 && (
          <div className="parent-dashboard__state-box">
            <p>Chua co hoc sinh nao duoc lien ket voi tai khoan phu huynh nay.</p>
          </div>
        )}

        {!loading && !error && children.length > 0 && (
          <div className="parent-children-grid">
            {children.map((student) => {
              const latestSeverity = student.latest_assessment?.severity_level || "";
              const severityClass =
                SEVERITY_CLASS[latestSeverity] || "parent-severity parent-severity--none";
              const severityLabel =
                SEVERITY_LABEL[latestSeverity] || "Chua co danh gia";

              return (
                <article key={student.id} className="parent-child-card">
                  <header className="parent-child-card__header">
                    <div>
                      <h3>{student.full_name || `Hoc sinh #${student.id}`}</h3>
                      <p>{student.email || "Khong co email"}</p>
                    </div>
                    <span className={severityClass}>{severityLabel}</span>
                  </header>

                  <div className="parent-child-card__meta">
                    <p>
                      <strong>Ma SV:</strong> {student.student_code || "Chua cap nhat"}
                    </p>
                    <p>
                      <strong>Truong:</strong> {student.university || "Chua cap nhat"}
                    </p>
                    <p>
                      <strong>Nganh:</strong> {student.major || "Chua cap nhat"}
                    </p>
                    <p>
                      <strong>Tong so danh gia:</strong> {student.total_assessments}
                    </p>
                    <p>
                      <strong>Danh gia gan nhat:</strong>{" "}
                      {formatDateTime(student.latest_assessment?.created_at)}
                    </p>
                  </div>

                  <div className="parent-child-card__tags">
                    {student.is_emergency_contact && (
                      <span className="parent-tag parent-tag--emergency">Lien he khan cap</span>
                    )}
                    {student.has_data_consent && (
                      <span className="parent-tag parent-tag--consent">Da duoc dong y du lieu</span>
                    )}
                  </div>

                  <footer className="parent-child-card__actions">
                    <button
                      onClick={() =>
                        navigate(`/parent/children/${student.id}`, {
                          state: {
                            childName: student.full_name || `Hoc sinh #${student.id}`,
                          },
                        })
                      }
                    >
                      Xem lich su danh gia
                    </button>
                  </footer>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default ParentDashboardPage;
