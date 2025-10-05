/**
 * Dashboard Service
 * API calls for dashboard welcome card and summary data
 */
import api from "./api";

export interface DashboardWelcomeData {
  user_name: string;
  days_since_registration: number;
  latest_emotion_severity: string | null;
  latest_emotion_text: string | null;
  latest_emotion_date: string | null;
  total_assessments: number;
  has_recent_assessment: boolean;
}

export const DashboardService = {
  /**
   * Get welcome card data for dashboard
   * Returns user name, days since registration, and latest emotion
   */
  async getWelcomeData(): Promise<DashboardWelcomeData> {
    try {
      const response = await api.get("/api/v1/dashboard/welcome");
      return response.data;
    } catch (error: any) {
      console.error("Failed to fetch dashboard welcome data:", error);
      throw error;
    }
  },
};

export default DashboardService;
