// src/api/auth.api.ts
import api from './axiosInstance';
import {
  ApiResponse,
  AuthTokens,
  User,
  LoginFormData,
  RegisterFormData,
} from '../types';

export const authApi = {
  login: (data: LoginFormData) =>
    api.post<ApiResponse<AuthTokens>>('/auth/login', data),

  register: (data: RegisterFormData) =>
    api.post<ApiResponse<{ user_id: string; username: string; email: string }>>(
      '/auth/register',
      data
    ),

  getCurrentUser: () =>
    api.get<ApiResponse<User>>('/auth/me'),

  refreshToken: (refreshToken: string) =>
    api.post<ApiResponse<{ access_token: string }>>(
      '/auth/refresh',
      null,
      { headers: { Authorization: `Bearer ${refreshToken}` } }
    ),

  changePassword: (old_password: string, new_password: string) =>
    api.post<ApiResponse<null>>('/auth/change-password', {
      old_password,
      new_password,
    }),

  logout: () =>
    api.post<ApiResponse<null>>('/auth/logout'),
};
