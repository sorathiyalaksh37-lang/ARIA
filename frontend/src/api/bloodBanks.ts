import apiClient from './client';
import { APIResponse, BloodBank } from '../types';

export const bloodBanksApi = {
  getBloodBanks: () =>
    apiClient.get<APIResponse<BloodBank[]>>('/blood-banks'),

  getBloodBankById: (id: string) =>
    apiClient.get<APIResponse<BloodBank>>(`/blood-banks/${id}`),

  searchBloodByType: (bloodType: string) =>
    apiClient.get<APIResponse<BloodBank[]>>('/blood-banks/search', { params: { type: bloodType } }),

  reserveBloodUnits: (id: string, data: { type: string; units: number }) =>
    apiClient.post<APIResponse<any>>(`/blood-banks/${id}/reserve`, data),
};
