import apiClient from './client';
import { APIResponse, PaginatedResponse, Hospital, HospitalSearchFilters } from '../types';

export const hospitalsApi = {
  getHospitals: (params?: HospitalSearchFilters) =>
    apiClient.get<PaginatedResponse<Hospital>>('/hospitals', { params }),

  getHospitalById: (id: string) =>
    apiClient.get<APIResponse<Hospital>>(`/hospitals/${id}`),

  findNearbyHospitals: (data: { lat: number; lng: number; radius_km?: number }) =>
    apiClient.post<APIResponse<Hospital[]>>('/hospitals/nearby', data),

  rankHospitals: (incidentId: string) =>
    apiClient.post<APIResponse<Hospital[]>>(`/hospitals/rank`, { incident_id: incidentId }),

  updateCapacity: (id: string, data: any) =>
    apiClient.put<APIResponse<Hospital>>(`/hospitals/${id}/capacity`, data),

  getForecast: (id: string) =>
    apiClient.get<APIResponse<any>>(`/hospitals/${id}/forecast`),
};
