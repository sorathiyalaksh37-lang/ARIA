// src/utils/constants.ts

export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

export const WS_URL =
  process.env.REACT_APP_WS_URL || 'ws://localhost:8000/api/v1/ws';

export const APP_NAME = process.env.REACT_APP_APP_NAME || 'ARIA';

export const JWT_REFRESH_THRESHOLD = Number(
  process.env.REACT_APP_JWT_REFRESH_THRESHOLD ?? 300
);

export const TOAST_DURATION = Number(
  process.env.REACT_APP_TOAST_DURATION ?? 4000
);

export const MAP_DEFAULTS = {
  lat:  Number(process.env.REACT_APP_MAP_DEFAULT_LAT  ?? 20.5937),
  lng:  Number(process.env.REACT_APP_MAP_DEFAULT_LNG  ?? 78.9629),
  zoom: Number(process.env.REACT_APP_MAP_DEFAULT_ZOOM ?? 5),
};

// Local storage keys
export const LS_KEYS = {
  ACCESS_TOKEN:  'aria_access_token',
  REFRESH_TOKEN: 'aria_refresh_token',
  USER:          'aria_user',
  THEME:         'aria_theme',
} as const;

// Polling intervals (ms)
export const POLL_INTERVAL = {
  DASHBOARD:    10_000,
  INCIDENTS:    15_000,
  AMBULANCES:    5_000,
  HOSPITALS:    30_000,
} as const;
