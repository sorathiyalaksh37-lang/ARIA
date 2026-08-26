import { GeoLocation } from './incident';

/**
 * Types for Hospitals and Healthcare Facilities
 */

/**
 * Detailed availability statistics for a hospital.
 */
export interface HospitalAvailability {
  total_beds: number;
  available_beds: number;
  icu_beds: number;
  available_icu_beds: number;
  emergency_capacity: number;
  operating_theaters_available?: number;
  last_updated: string;
}

/**
 * Core interface representing a Hospital facility.
 */
export interface Hospital {
  id: string;
  name: string;
  address: string;
  location: GeoLocation;
  phone: string;
  availability: HospitalAvailability;
  specialties: string[];
  distance_km?: number;
  eta_minutes?: number;
  ranking_score?: number;
  is_active: boolean;
}

/**
 * Filters for searching hospitals.
 */
export interface HospitalSearchFilters {
  specialty?: string;
  min_capacity?: number;
  max_distance_km?: number;
  location?: GeoLocation;
  require_icu?: boolean;
}
