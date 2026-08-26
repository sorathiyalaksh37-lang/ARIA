import apiClient from './client';
import { APIResponse, Ambulance, AmbulanceUpdate } from '../types';

export const ambulancesApi = {
  getAmbulances: (params?: any) =>
    apiClient.get<APIResponse<Ambulance[]>>('/ambulances', { params }),

  getAmbulanceById: (id: string) =>
    apiClient.get<APIResponse<Ambulance>>(`/ambulances/${id}`),

  getAvailableAmbulances: () =>
    apiClient.get<APIResponse<Ambulance[]>>('/ambulances/available'),

  findNearestAmbulances: (data: { lat: number; lng: number; count?: number }) =>
    apiClient.post<APIResponse<Ambulance[]>>('/ambulances/nearest', data),

  updateLocation: (id: string, data: Pick<AmbulanceUpdate, 'location' | 'timestamp'>) =>
    apiClient.put<APIResponse<Ambulance>>(`/ambulances/${id}/location`, data),

  updateStatus: (id: string, data: Pick<AmbulanceUpdate, 'status' | 'timestamp'>) =>
    apiClient.put<APIResponse<Ambulance>>(`/ambulances/${id}/status`, data),
};
