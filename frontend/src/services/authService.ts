import api from "./api";
import type { AuthResponse, LoginRequest, RegisterRequest } from "@/types/auth";

const transformUser = (userData: any) => {
  if (userData.profile && userData.role === "STUDENT") {
    return {
      ...userData,
      student: userData.profile,
      role: userData.role as "STUDENT" | "PARENT" | "COUNSELOR" | "ADMIN",
    };
  }
  return {
    ...userData,
    role: userData.role as "STUDENT" | "PARENT" | "COUNSELOR" | "ADMIN",
  };
};

export const authService = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const loginResponse = await api.post("/api/v1/auth/login", data);
    const token = loginResponse.data.access_token;
    const refreshToken = loginResponse.data.refresh_token;

    localStorage.setItem("access_token", token);
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken);

    const userResponse = await api.get("/api/v1/auth/me");
    const user = transformUser(userResponse.data);

    return { access_token: token, refresh_token: refreshToken, token_type: "bearer", user };
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const registerResponse = await api.post("/api/v1/auth/register", data);
    const token = registerResponse.data.access_token;
    const refreshToken = registerResponse.data.refresh_token;

    localStorage.setItem("access_token", token);
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken);

    const userResponse = await api.get("/api/v1/auth/me");
    const user = transformUser(userResponse.data);

    return { access_token: token, refresh_token: refreshToken, token_type: "bearer", user };
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  getCurrentUser: async () => {
    const response = await api.get("/api/v1/auth/me");
    return transformUser(response.data);
  },
};
