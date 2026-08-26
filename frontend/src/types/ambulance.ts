import { GeoLocation } from './incident';

/**
 * Types for Ambulances and Emergency Vehicles
 */

/**
 * Classification of ambulance capabilities.
 */
export enum AmbulanceType {
  BASIC = 'BASIC',
  ADVANCED_LIFE_SUPPORT = 'ADVANCED_LIFE_SUPPORT',
  CRITICAL_CARE = 'CRITICAL_CARE',
}

/**
 * Operational status of an ambulance.
 */
export enum AmbulanceStatus {
  AVAILABLE = 'AVAILABLE',
  EN_ROUTE = 'EN_ROUTE',
  ON_SCENE = 'ON_SCENE',
  TRANSPORTING = 'TRANSPORTING',
  AT_HOSPITAL = 'AT_HOSPITAL',
  OFFLINE = 'OFFLINE',
}

/**
 * Core interface representing an ambulance vehicle.
 */
export interface Ambulance {
  id: string;
  unit_number: string;
  type: AmbulanceType;
  status: AmbulanceStatus;
  location: GeoLocation;
  crew_count: number;
  current_incident_id?: string;
  hospital_base_id?: string;
  last_updated: string;
  fuel_level_pct?: number;
}

/**
 * Payload for updating an ambulance's status or location.
 */
export interface AmbulanceUpdate {
  id: string;
  status?: AmbulanceStatus;
  location?: GeoLocation;
  current_incident_id?: string | null;
  timestamp: string;
}
