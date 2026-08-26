// src/api/incidents.api.ts
import api from './axiosInstance';
import {
  ApiResponse,
  PaginatedResponse,
  Incident,
  CreateIncidentFormData,
  IncidentFilters,
} from '../types';

export const incidentsApi = {
  getAll: (filters?: IncidentFilters) =>
    api.get<PaginatedResponse<Incident>>('/incidents', { params: filters }),

  getById: (id: string) =>
    api.get<ApiResponse<Incident>>(`/incidents/${id}`),

  create: (data: CreateIncidentFormData) =>
    api.post<ApiResponse<Incident>>('/incidents', data),

  update: (id: string, data: Partial<CreateIncidentFormData>) =>
    api.patch<ApiResponse<Incident>>(`/incidents/${id}`, data),

  updateStatus: (id: string, status: string) =>
    api.patch<ApiResponse<Incident>>(`/incidents/${id}/status`, { status }),

  resolve: (id: string, resolution_notes?: string) =>
    api.post<ApiResponse<Incident>>(`/incidents/${id}/resolve`, {
      resolution_notes,
    }),

  delete: (id: string) =>
    api.delete<ApiResponse<null>>(`/incidents/${id}`),

  assignAmbulance: (incidentId: string, ambulanceId: string) =>
    api.post<ApiResponse<Incident>>(`/incidents/${incidentId}/assign`, {
      ambulance_id: ambulanceId,
    }),

  getMLPredictions: (id: string) =>
    api.get<ApiResponse<Record<string, unknown>>>(`/incidents/${id}/predictions`),
};
