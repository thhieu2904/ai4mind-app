import api from "./api";

export interface AdminUser {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string;
}

export interface CreateUserRequest {
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  password: string;
}

export interface UpdateUserRequest {
  full_name?: string;
  phone?: string;
  is_verified?: boolean;
}

const AdminService = {
  listUsers: async (role?: string, search?: string): Promise<AdminUser[]> => {
    const params: Record<string, string> = {};
    if (role) params.role = role;
    if (search) params.search = search;
    const res = await api.get("/admin/users", { params });
    return res.data;
  },

  createUser: async (data: CreateUserRequest): Promise<AdminUser> => {
    const res = await api.post("/admin/users", data);
    return res.data;
  },

  updateUser: async (id: number, data: UpdateUserRequest): Promise<AdminUser> => {
    const res = await api.put(`/admin/users/${id}`, data);
    return res.data;
  },

  resetPassword: async (id: number, newPassword: string): Promise<void> => {
    await api.put(`/admin/users/${id}/reset-password`, { new_password: newPassword });
  },

  toggleActive: async (id: number): Promise<AdminUser> => {
    const res = await api.put(`/admin/users/${id}/toggle-active`);
    return res.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await api.delete(`/admin/users/${id}`);
  },
};

export default AdminService;
