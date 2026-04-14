import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import { ParentService } from "../../services/parentService";
import type { Assessment } from "../../services/assessmentService";
import "./ParentChildAssessmentsPage.css";

type PaginationState = {
  page: number;
  pageSize: number;
  totalPages: number;
  total: number;
};

const formatDate = (value: string): string => {
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

const ParentChildAssessmentsPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { studentId } = useParams<{ studentId: string }>();

  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 10,
    totalPages: 1,
    total: 0,
  });

  const childName = useMemo(() => {
    const state = location.state as { childName?: string } | undefined;
    return state?.childName || `Hoc sinh #${studentId || "?"}`;
  }, [location.state, studentId]);

  const studentIdNumber = useMemo(() => {
    const parsed = Number(studentId);
    return Number.isInteger(parsed) ? parsed : null;
  }, [studentId]);

  useEffect(() => {
    if (!studentIdNumber) {
      setError("Ma hoc sinh khong hop le");
      setLoading(false);
      return;
    }

    loadAssessments(studentIdNumber, pagination.page, pagination.pageSize);
  }, [studentIdNumber, pagination.page, pagination.pageSize]);

  const loadAssessments = async (
    studentIdValue: number,
    page: number,
    pageSize: number
  ) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ParentService.getChildAssessments(
        studentIdValue,
        page,
        pageSize
      );
      setAssessments(response.items || []);
      setPagination((prev) => ({
        ...prev,
        totalPages: Math.max(response.total_pages || 1, 1),
        total: response.total || 0,
      }));
    } catch (err: any) {
      console.error("Failed to load child assessments", err);
      setError(
        err?.response?.data?.detail ||
          "Khong the tai lich su danh gia cho hoc sinh nay"
      );
    } finally {
      setLoading(false);
    }
  };

  const goToPage = (nextPage: number) => {
    setPagination((prev) => ({ ...prev, page: nextPage }));
  };

  return (
    <MainLayout>
      <div className="parent-child-assessments">
        <section className="parent-child-assessments__header">
          <button onClick={() => navigate("/parent/dashboard")}>Quay lai</button>
          <div>
            <h1>{childName}</h1>
            <p>Tong so danh gia: {pagination.total}</p>
          </div>
        </section>

        {loading && (
          <div className="parent-child-assessments__state-box">
            <p>Dang tai lich su danh gia...</p>
          </div>
        )}

        {!loading && error && (
          <div className="parent-child-assessments__state-box parent-child-assessments__state-box--error">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && assessments.length === 0 && (
          <div className="parent-child-assessments__state-box">
            <p>Hoc sinh nay chua co ban ghi danh gia nao.</p>
          </div>
        )}

        {!loading && !error && assessments.length > 0 && (
          <div className="parent-child-assessments__list">
            {assessments.map((item) => (
              <article key={item.id} className="parent-assessment-card">
                <header>
                  <h3>Lan danh gia #{item.id}</h3>
                  <span>{formatDate(item.created_at)}</span>
                </header>

                <div className="parent-assessment-card__metrics">
                  <p>
                    <strong>Tong diem:</strong> {item.total_score}/21
                  </p>
                  <p>
                    <strong>Muc do:</strong> {item.severity_level}
                  </p>
                  <p>
                    <strong>Suy giam chuc nang:</strong>{" "}
                    {item.functional_impairment ?? "N/A"}
                  </p>
                </div>

                {item.analysis && (
                  <div className="parent-assessment-card__analysis">
                    <p>{item.analysis}</p>
                  </div>
                )}
              </article>
            ))}
          </div>
        )}

        {!loading && !error && pagination.totalPages > 1 && (
          <div className="parent-child-assessments__pagination">
            <button
              disabled={pagination.page <= 1}
              onClick={() => goToPage(pagination.page - 1)}
            >
              Truoc
            </button>
            <span>
              Trang {pagination.page}/{pagination.totalPages}
            </span>
            <button
              disabled={pagination.page >= pagination.totalPages}
              onClick={() => goToPage(pagination.page + 1)}
            >
              Sau
            </button>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default ParentChildAssessmentsPage;
