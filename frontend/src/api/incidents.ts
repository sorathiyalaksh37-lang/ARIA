import apiClient from './client';
import { APIResponse, PaginatedResponse, Incident, IncidentTimeline, ResponsePlan } from '../types';

export const incidentsApi = {
  createIncident: (data: Partial<Incident>) =>
    apiClient.post<APIResponse<Incident>>('/incidents', data),

  getIncidents: (params?: any) =>
    apiClient.get<PaginatedResponse<Incident>>('/incidents', { params }),

  getIncidentById: (id: string) =>
    apiClient.get<APIResponse<Incident>>(`/incidents/${id}`),

  updateIncident: (id: string, data: Partial<Incident>) =>
    apiClient.put<APIResponse<Incident>>(`/incidents/${id}`, data),

  deleteIncident: (id: string) =>
    apiClient.delete<APIResponse<null>>(`/incidents/${id}`),

  processIncident: (id: string) =>
    apiClient.post<APIResponse<ResponsePlan>>(`/incidents/${id}/process`),

  approveIncident: (id: string) =>
    apiClient.post<APIResponse<Incident>>(`/incidents/${id}/approve`),

  rejectIncident: (id: string, reason: string) =>
    apiClient.post<APIResponse<Incident>>(`/incidents/${id}/reject`, { reason }),

  modifyPlan: (id: string, data: Partial<ResponsePlan>) =>
    apiClient.put<APIResponse<ResponsePlan>>(`/incidents/${id}/plan`, data),

  dispatchIncident: (id: string) =>
    apiClient.post<APIResponse<Incident>>(`/incidents/${id}/dispatch`),

  getIncidentStatus: (id: string) =>
    apiClient.get<APIResponse<{ status: string }>>(`/incidents/${id}/status`),

  getIncidentHistory: (id: string) =>
    apiClient.get<APIResponse<IncidentTimeline[]>>(`/incidents/${id}/history`),
};
