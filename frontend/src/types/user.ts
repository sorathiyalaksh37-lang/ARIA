/**
 * Types for Users and Authentication
 */

/**
 * Access control roles within the platform.
 */
export enum UserRole {
  ADMIN = 'ADMIN',
  COORDINATOR = 'COORDINATOR',
  HOSPITAL = 'HOSPITAL',
  AMBULANCE = 'AMBULANCE',
  BLOOD_BANK = 'BLOOD_BANK',
  READ_ONLY = 'READ_ONLY',
}

/**
 * Core interface representing a system user.
 */
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login?: string;
  avatar_url?: string;
}

/**
 * Authentication tokens payload.
 */
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Representation of the current authentication state.
 */
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
