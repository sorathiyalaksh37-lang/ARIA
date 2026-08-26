/**
 * Types for Incidents and Incident Management
 */

/**
 * GeoLocation representing latitude and longitude coordinates.
 */
export interface GeoLocation {
  lat: number;
  lng: number;
}

/**
 * Severity level of an incident.
 */
export enum IncidentSeverity {
  LOW = 'LOW',
  MODERATE = 'MODERATE',
  CRITICAL = 'CRITICAL',
}

/**
 * Status of an incident throughout its lifecycle.
 */
export enum IncidentStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  AWAITING_APPROVAL = 'AWAITING_APPROVAL',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  DISPATCHED = 'DISPATCHED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

/**
 * Represents an individual action or event within an incident's timeline.
 */
export interface IncidentTimeline {
  id: string;
  incident_id: string;
  action: string;
  description: string;
  timestamp: string;
  actor_id?: string;
  actor_role?: string;
  metadata?: Record<string, any>;
}

/**
 * AI-generated recommendation for an incident.
 */
export interface AIRecommendation {
  type: 'hospital' | 'resource' | 'route' | 'alert';
  priority: number;
  title: string;
  description: string;
  confidence: number;
  metadata?: Record<string, any>;
}

/**
 * An execution plan generated for an incident response.
 */
export interface ResponsePlan {
  id: string;
  incident_id: string;
  generated_at: string;
  recommended_ambulances: string[];
  recommended_hospitals: string[];
  estimated_response_time_mins: number;
  instructions: string[];
  ai_recommendations?: AIRecommendation[];
  status: 'PENDING' | 'EXECUTING' | 'COMPLETED' | 'SUPERSEDED';
}

/**
 * Core interface representing an emergency incident.
 */
export interface Incident {
  id: string;
  incident_number: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  location: GeoLocation;
  address: string;
  caller_name?: string;
  caller_phone?: string;
  reported_at: string;
  updated_at: string;
  resolved_at?: string;
  dispatched_at?: string;
  assigned_ambulance_id?: string;
  assigned_hospital_id?: string;
  triage_score?: number;
  eta_minutes?: number;
  created_by: string;
  timeline?: IncidentTimeline[];
  active_plan?: ResponsePlan;
}
