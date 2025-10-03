/**
 * User Profile Service - API calls for user profile data
 */
import api from "./api";

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: "student" | "parent" | "counselor" | "admin";
  is_active: boolean;
  created_at: string;
  last_login?: string;
  profile?: StudentProfile | ParentProfile | CounselorProfile;
}

export interface StudentProfile {
  student_code?: string;
  date_of_birth?: string;
  gender?: "male" | "female" | "other" | "prefer_not_to_say";
  phone_number?: string;
  address?: string;
  university?: string;
  major?: string;
  year_of_study?: number;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
}

export interface ParentProfile {
  id: number;
  occupation?: string;
  relationship?: string;
}

export interface CounselorProfile {
  license_number?: string;
  specialization?: string;
  years_of_experience?: number;
  bio?: string;
}

export interface StudentDetails extends StudentProfile {
  id: number;
  user_id: number;
}

export class UserService {
  /**
   * Get current user profile with role-specific data
   */
  static async getCurrentUser(): Promise<UserProfile> {
    const response = await api.get("/api/v1/auth/me");
    return response.data;
  }

  /**
   * Get detailed student profile (for students only)
   */
  static async getStudentProfile(): Promise<StudentDetails> {
    const response = await api.get("/api/v1/students/me");
    return response.data;
  }

  /**
   * Update user basic information
   */
  static async updateUser(data: {
    full_name?: string;
    phone?: string;
  }): Promise<UserProfile> {
    const response = await api.put("/api/v1/auth/me", data);
    return response.data;
  }

  /**
   * Update student profile
   */
  static async updateStudentProfile(
    data: Partial<StudentProfile>
  ): Promise<StudentDetails> {
    const response = await api.put("/api/v1/students/me", data);
    return response.data;
  }

  /**
   * Get user activity summary
   */
  static async getActivitySummary(): Promise<{
    total_assessments: number;
    total_voice_analyses: number;
    last_activity: string;
    member_since: string;
  }> {
    // This endpoint might need to be created in backend if doesn't exist
    const response = await api.get("/api/v1/auth/activity-summary");
    return response.data;
  }
}
