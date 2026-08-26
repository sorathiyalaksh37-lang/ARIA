/**
 * Export all types from the domain modules
 */

export * from './incident';
export * from './hospital';
export * from './ambulance';
export * from './bloodBank';
export * from './user';
export * from './websocket';
export * from './api';
export * from './dashboard';

// Form Types
export interface LoginFormData {
  username: string;
  password?: string;
}
