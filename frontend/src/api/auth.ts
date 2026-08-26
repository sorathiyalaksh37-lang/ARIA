import apiClient from './client';
import { APIResponse, AuthTokens, User, LoginFormData } from '../types';

export const authApi = {
  login: (data: LoginFormData) =>
    apiClient.post<APIResponse<AuthTokens>>('/auth/login', data),

  register: (data: any) =>
    apiClient.post<APIResponse<User>>('/auth/register', data),

  refreshToken: (token: string) =>
    apiClient.post<APIResponse<AuthTokens>>('/auth/refresh', null, {
      headers: { Authorization: `Bearer ${token}` }
    }),

  logout: () => apiClient.post<APIResponse<null>>('/auth/logout'),

  getCurrentUser: () => apiClient.get<APIResponse<User>>('/auth/me'),

  changePassword: (data: any) =>
    apiClient.put<APIResponse<null>>('/auth/password', data),
};
