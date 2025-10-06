export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "student" | "parent" | "counselor" | "admin";
  is_active: boolean;
  created_at: string;
  updated_at: string;

  // Student profile data (if role is student)
  student?: {
    id: number;
    student_code?: string;
    date_of_birth?: string;
    gender?: "male" | "female" | "other" | "prefer_not_to_say";
    university?: string;
    major?: string;
    education_level?: "high_school" | "undergraduate" | "graduate" | "other";
    grade?: string;
  };
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role: "student" | "parent";

  // Important for GAD-7 assessment
  date_of_birth?: string; // YYYY-MM-DD format
  gender?: "male" | "female" | "other" | "prefer_not_to_say";
  phone?: string;
  address?: string;

  // Student specific
  student_code?: string;
  university?: string;
  major?: string;
  education_level?: "high_school" | "undergraduate" | "graduate" | "other";
  grade?: string;

  // Emergency contact parent email (for students)
  parent_email?: string;

  // Counselor specific (for future use)
  license_number?: string;
  specialization?: string;
  years_of_experience?: number;
}
