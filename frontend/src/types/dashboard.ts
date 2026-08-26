import { GeoLocation } from './incident';

/**
 * Types for Dashboard Statistics and Overviews
 */

/**
 * High-level statistics for the main dashboard.
 */
export interface DashboardStats {
  active_incidents: number;
  critical_incidents: number;
  ambulances_on_route: number;
  average_response_time_min: number;
  total_incidents_today: number;
  resolved_incidents_today: number;
  dispatchers_online: number;
}

/**
 * Overview of resource allocations.
 */
export interface ResourceStatus {
  total_ambulances: number;
  available_ambulances: number;
  total_hospital_beds: number;
  available_hospital_beds: number;
  total_icu_beds: number;
  available_icu_beds: number;
}

/**
 * A geographical hotspot indicating high incident volume.
 */
export interface Hotspot {
  id: string;
  location: GeoLocation;
  intensity: number; // e.g., 0.0 to 1.0
  incident_count: number;
  radius_meters: number;
}

/**
 * Analytics data for charts and graphs.
 */
export interface AnalyticsData {
  trend: Array<{
    date: string;
    critical: number;
    moderate: number;
    low: number;
    total: number;
  }>;
  response_times: Array<{
    date: string;
    average_min: number;
  }>;
}
