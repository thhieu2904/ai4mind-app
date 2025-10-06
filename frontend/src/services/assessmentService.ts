/**
 * Assessment Service - API calls for assessment-related data
 */
import api from "./api";

export interface Assessment {
  id: number;
  student_id: number;
  answers: number[];
  total_score: number;
  severity_level: string;
  analysis?: string;
  recommendations?: string[];
  functional_impairment?: number;
  notes?: string;
  created_at: string;
}

export interface AssessmentListResponse {
  items: Assessment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AssessmentStats {
  total_assessments: number;
  average_score: number;
  latest_score?: number;
  latest_severity?: string;
  trend?: "improving" | "worsening" | "stable";
  score_history: Array<{
    date: string;
    score: number;
    severity: string;
  }>;
}

export interface AssessmentDetail extends Assessment {
  questions_with_answers: Array<{
    question: string;
    answer: number;
    answer_text: string;
  }>;
  severity_info: {
    level: string;
    description: string;
    color: string;
  };
}

export class AssessmentService {
  /**
   * Get paginated list of user's assessments
   */
  static async getAssessments(
    page = 1,
    pageSize = 10
  ): Promise<AssessmentListResponse> {
    const response = await api.get("/api/v1/assessments/", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * Get assessment statistics for charts and overview
   */
  static async getStats(): Promise<AssessmentStats> {
    const response = await api.get("/api/v1/assessments/stats");
    return response.data;
  }

  /**
   * Get detailed assessment by ID
   */
  static async getAssessmentDetail(id: number): Promise<AssessmentDetail> {
    const response = await api.get(`/api/v1/assessments/${id}`);
    return response.data;
  }

  /**
   * Create new assessment
   */
  static async createAssessment(data: {
    answers: number[];
    functional_impairment?: number;
    notes?: string;
  }): Promise<Assessment> {
    const response = await api.post("/api/v1/assessments/", data);
    return response.data;
  }
}
