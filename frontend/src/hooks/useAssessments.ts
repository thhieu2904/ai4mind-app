/**
 * Custom hook for managing assessments data
 */
import { useState, useEffect } from "react";
import {
  AssessmentService,
  type Assessment,
  type AssessmentListResponse,
} from "../services/assessmentService";

interface UseAssessmentsProps {
  page?: number;
  pageSize?: number;
  autoFetch?: boolean;
}

interface UseAssessmentsReturn {
  assessments: Assessment[];
  loading: boolean;
  error: string | null;
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
  fetchAssessments: (page?: number, pageSize?: number) => Promise<void>;
  refresh: () => Promise<void>;
}

export const useAssessments = ({
  page = 1,
  pageSize = 10,
  autoFetch = true,
}: UseAssessmentsProps = {}): UseAssessmentsReturn => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    pageSize: 10,
    totalPages: 0,
  });

  const fetchAssessments = async (
    currentPage = page,
    currentPageSize = pageSize
  ) => {
    try {
      setLoading(true);
      setError(null);

      const response: AssessmentListResponse =
        await AssessmentService.getAssessments(currentPage, currentPageSize);

      setAssessments(response.items);
      setPagination({
        total: response.total,
        page: response.page,
        pageSize: response.page_size,
        totalPages: response.total_pages,
      });

      console.log(
        `📋 Loaded ${response.items.length} assessments (page ${response.page}/${response.total_pages})`
      );
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Không thể tải danh sách đánh giá";
      setError(errorMessage);
      console.error("❌ Error fetching assessments:", err);
    } finally {
      setLoading(false);
    }
  };

  const refresh = () => fetchAssessments(pagination.page, pagination.pageSize);

  useEffect(() => {
    if (autoFetch) {
      fetchAssessments(page, pageSize);
    }
  }, [page, pageSize, autoFetch]);

  return {
    assessments,
    loading,
    error,
    pagination,
    fetchAssessments,
    refresh,
  };
};
