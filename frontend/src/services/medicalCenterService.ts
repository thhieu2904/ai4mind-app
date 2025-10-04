/**
 * Medical Center Service
 * API client cho medical centers endpoints
 */

import api from "./api";

// ===========================
// TypeScript Interfaces
// ===========================

export interface MedicalCenter {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  phone?: string;
  email?: string;
  website?: string;
  services: string[];
  opening_hours: Record<string, string>;
  description?: string;
  image_url?: string;
  distance?: number; // Calculated field (km)
  created_at: string;
  updated_at: string;
}

export interface NearbyRequest {
  latitude: number;
  longitude: number;
  radius?: number; // km, default 50
  services?: string[];
  limit?: number; // default 10
}

export interface NearbyResponse {
  centers: MedicalCenter[];
  total: number;
  user_location: {
    latitude: number;
    longitude: number;
  };
}

export interface GetCentersParams {
  skip?: number;
  limit?: number;
  services?: string; // comma-separated
}

// ===========================
// API Service Methods
// ===========================

const medicalCenterService = {
  /**
   * Lấy danh sách tất cả medical centers
   */
  async getAllCenters(params?: GetCentersParams): Promise<MedicalCenter[]> {
    const response = await api.get<MedicalCenter[]>(
      "/api/v1/medical-centers/",
      {
        params,
      }
    );
    return response.data;
  },

  /**
   * Lấy chi tiết 1 medical center
   */
  async getCenterById(id: string): Promise<MedicalCenter> {
    const response = await api.get<MedicalCenter>(
      `/api/v1/medical-centers/${id}`
    );
    return response.data;
  },

  /**
   * Tìm medical centers gần vị trí hiện tại
   */
  async getNearby(request: NearbyRequest): Promise<NearbyResponse> {
    const response = await api.post<NearbyResponse>(
      "/api/v1/medical-centers/nearby",
      request
    );
    return response.data;
  },

  /**
   * Tạo medical center mới (Admin only)
   */
  async createCenter(center: Partial<MedicalCenter>): Promise<MedicalCenter> {
    const response = await api.post<MedicalCenter>(
      "/api/v1/medical-centers/",
      center
    );
    return response.data;
  },

  /**
   * Cập nhật medical center (Admin only)
   */
  async updateCenter(
    id: string,
    center: Partial<MedicalCenter>
  ): Promise<MedicalCenter> {
    const response = await api.put<MedicalCenter>(
      `/api/v1/medical-centers/${id}`,
      center
    );
    return response.data;
  },

  /**
   * Xóa medical center (Admin only)
   */
  async deleteCenter(id: string): Promise<void> {
    await api.delete(`/api/v1/medical-centers/${id}`);
  },
};

export default medicalCenterService;
