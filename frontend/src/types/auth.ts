export interface User {
  id: number
  email: string
  full_name: string
  role: 'student' | 'parent' | 'counselor' | 'admin'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  role: 'student' | 'parent'
}
