import api from './api'
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/types/auth'

export const authService = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/v1/auth/login', data)
    return response.data
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/v1/auth/register', data)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },
}
