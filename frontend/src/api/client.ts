import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';
import { LS_KEYS, API_BASE_URL } from '../utils/constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
});

// Request interceptor: attach JWT token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(LS_KEYS.ACCESS_TOKEN);
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401, refresh token, global errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Global error toast (excluding 401 which handles refresh/logout)
    if (error.response?.status !== 401) {
       const msg = (error.response?.data as any)?.message || 'An error occurred with the API.';
       toast.error(msg);
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = localStorage.getItem(LS_KEYS.REFRESH_TOKEN);

      if (refreshToken) {
        try {
          const { data } = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            null,
            { headers: { Authorization: `Bearer ${refreshToken}` } }
          );
          const newToken = data.data.access_token;
          localStorage.setItem(LS_KEYS.ACCESS_TOKEN, newToken);
          if (original.headers) {
            original.headers.Authorization = `Bearer ${newToken}`;
          }
          return apiClient(original);
        } catch {
          toast.error('Session expired. Please log in again.');
          localStorage.removeItem(LS_KEYS.ACCESS_TOKEN);
          localStorage.removeItem(LS_KEYS.REFRESH_TOKEN);
          localStorage.removeItem(LS_KEYS.USER);
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem(LS_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(LS_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(LS_KEYS.USER);
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
