/**
 * User Profile Service - API calls for user profile data
 */
import api from "./api";

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: "STUDENT" | "PARENT" | "COUNSELOR" | "ADMIN";
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
  education_level?: "high_school" | "undergraduate" | "graduate" | "other";
  grade?: string;
  emergency_contact_parent_id?: number;
  parent_email?: string; // For display/edit
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
  email?: string; // From student.user relationship
  full_name?: string; // From student.user relationship
  created_at?: string; // Timestamp when student was created
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
   * @deprecated Use updateStudentProfile instead (handles both user and student data)
   */
  static async updateUser(_data: {
    full_name?: string;
    phone?: string;
  }): Promise<UserProfile> {
    // This endpoint doesn't exist - use updateStudentProfile instead
    throw new Error("Use updateStudentProfile instead");
  }

  /**
   * Update student profile (includes user basic info like full_name, phone)
   */
  static async updateStudentProfile(
    data: Partial<StudentProfile> & { full_name?: string }
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
