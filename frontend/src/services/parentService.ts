import api from "./api";
import type { AssessmentListResponse } from "./assessmentService";

export interface ParentChildLatestAssessment {
  id: number;
  total_score: number;
  severity_level: string;
  created_at: string;
}

export interface ParentChild {
  id: number;
  user_id: number;
  full_name?: string;
  email?: string;
  student_code?: string;
  university?: string;
  major?: string;
  is_emergency_contact: boolean;
  has_data_consent: boolean;
  total_assessments: number;
  latest_assessment?: ParentChildLatestAssessment;
}

export interface ParentChildrenResponse {
  total_children: number;
  children: ParentChild[];
}

export const ParentService = {
  async getMyChildren(): Promise<ParentChildrenResponse> {
    const response = await api.get("/api/v1/parents/me/children");
    return response.data;
  },

  async getChildAssessments(
    studentId: number,
    page = 1,
    pageSize = 10
  ): Promise<AssessmentListResponse> {
    const response = await api.get(
      `/api/v1/parents/me/children/${studentId}/assessments`,
      {
        params: {
          page,
          page_size: pageSize,
        },
      }
    );
    return response.data;
  },
};
