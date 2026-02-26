import api from "./api";
import type { AuthResponse, LoginRequest, RegisterRequest } from "@/types/auth";

export const authService = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    // Step 1: Login to get token
    const loginResponse = await api.post("/api/v1/auth/login", data);
    const token = loginResponse.data.access_token;

    // Step 2: Set token for subsequent requests
    localStorage.setItem("access_token", token);

    // Step 3: Fetch user data with /me endpoint
    const userResponse = await api.get("/api/v1/auth/me");
    const userData = userResponse.data;

    // Step 4: Transform backend 'profile' to frontend 'student'
    let user = userData;
    if (userData.profile && userData.role === "STUDENT") {
      user = {
        ...userData,
        student: userData.profile,
        role: userData.role as
          | "STUDENT"
          | "PARENT"
          | "COUNSELOR"
          | "ADMIN",
      };
    } else {
      user = {
        ...userData,
        role: userData.role as
          | "STUDENT"
          | "PARENT"
          | "COUNSELOR"
          | "ADMIN",
      };
    }

    return {
      access_token: token,
      token_type: "bearer",
      user,
    };
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    // Step 1: Register to get token
    const registerResponse = await api.post("/api/v1/auth/register", data);
    const token = registerResponse.data.access_token;

    // Step 2: Set token for subsequent requests
    localStorage.setItem("access_token", token);

    // Step 3: Fetch user data with /me endpoint
    const userResponse = await api.get("/api/v1/auth/me");
    const userData = userResponse.data;

    // Step 4: Transform backend 'profile' to frontend 'student'
    let user = userData;
    if (userData.profile && userData.role === "STUDENT") {
      user = {
        ...userData,
        student: userData.profile,
        role: userData.role as
          | "STUDENT"
          | "PARENT"
          | "COUNSELOR"
          | "ADMIN",
      };
    } else {
      user = {
        ...userData,
        role: userData.role as
          | "STUDENT"
          | "PARENT"
          | "COUNSELOR"
          | "ADMIN",
      };
    }

    return {
      access_token: token,
      token_type: "bearer",
      user,
    };
  },

  logout: () => {
    localStorage.removeItem("access_token");
  },

  getCurrentUser: async () => {
    const response = await api.get("/api/v1/auth/me");
    const userData = response.data;

    // FIX: Transform backend 'profile' to frontend 'student' for type consistency
    // Backend returns: { id, email, role, profile: {...} }
    // Frontend expects: { id, email, role, student: {...} }
    if (userData.profile && userData.role === "STUDENT") {
      return {
        ...userData,
        student: userData.profile,
        role: userData.role as
          | "STUDENT"
          | "PARENT"
          | "COUNSELOR"
          | "ADMIN",
      };
    }

    return {
      ...userData,
      role: userData.role as
        | "STUDENT"
        | "PARENT"
        | "COUNSELOR"
        | "ADMIN",
    };
  },
};
