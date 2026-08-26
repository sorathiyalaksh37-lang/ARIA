import apiClient from './client';
import { APIResponse, DashboardStats, ResourceStatus, Hotspot, AnalyticsData, Incident } from '../types';

export const dashboardApi = {
  getStats: () =>
    apiClient.get<APIResponse<DashboardStats>>('/dashboard/stats'),

  getActiveIncidentsMap: () =>
    apiClient.get<APIResponse<Incident[]>>('/dashboard/active-incidents'),

  getResourceStatus: () =>
    apiClient.get<APIResponse<ResourceStatus>>('/dashboard/resources'),

  getHotspots: () =>
    apiClient.get<APIResponse<Hotspot[]>>('/dashboard/hotspots'),

  getAnalytics: () =>
    apiClient.get<APIResponse<AnalyticsData>>('/dashboard/analytics'),
};
