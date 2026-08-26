// ============================================================
// src/types/index.ts  —  All shared TypeScript types for ARIA
// ============================================================

// ---- Enums -----------------------------------------------

export enum IncidentSeverity {
  CRITICAL = 'CRITICAL',
  HIGH     = 'HIGH',
  MEDIUM   = 'MEDIUM',
  LOW      = 'LOW',
}

export enum IncidentStatus {
  REPORTED    = 'REPORTED',
  DISPATCHED  = 'DISPATCHED',
  RESPONDING  = 'RESPONDING',
  RESOLVED    = 'RESOLVED',
  CLOSED      = 'CLOSED',
}

export enum AmbulanceStatus {
  AVAILABLE   = 'AVAILABLE',
  DISPATCHED  = 'DISPATCHED',
  RESPONDING  = 'RESPONDING',
  AT_SCENE    = 'AT_SCENE',
  TRANSPORTING= 'TRANSPORTING',
  MAINTENANCE = 'MAINTENANCE',
  OFFLINE     = 'OFFLINE',
}

export enum UserRole {
  ADMIN       = 'ADMIN',
  DISPATCHER  = 'DISPATCHER',
  SUPERVISOR  = 'SUPERVISOR',
  VIEWER      = 'VIEWER',
}

export enum BloodGroup {
  A_POS = 'A+',
  A_NEG = 'A-',
  B_POS = 'B+',
  B_NEG = 'B-',
  AB_POS= 'AB+',
  AB_NEG= 'AB-',
  O_POS = 'O+',
  O_NEG = 'O-',
}

// ---- Core Models -----------------------------------------

export interface GeoLocation {
  lat: number;
  lng: number;
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

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
  dispatched_at?: string;
  resolved_at?: string;
  assigned_ambulance_id?: string;
  assigned_hospital_id?: string;
  triage_score?: number;
  eta_minutes?: number;
  ai_recommendations?: AIRecommendation[];
  created_by: string;
  updated_at: string;
}

export interface Ambulance {
  id: string;
  unit_number: string;
  status: AmbulanceStatus;
  location: GeoLocation;
  crew_count: number;
  equipment_level: 'BLS' | 'ALS' | 'MICU';
  current_incident_id?: string;
  hospital_base_id?: string;
  last_updated: string;
}

export interface Hospital {
  id: string;
  name: string;
  address: string;
  location: GeoLocation;
  phone: string;
  total_beds: number;
  available_beds: number;
  icu_beds: number;
  available_icu_beds: number;
  emergency_capacity: number;
  specialties: string[];
  distance_km?: number;
  eta_minutes?: number;
  ranking_score?: number;
}

export interface BloodBank {
  id: string;
  name: string;
  address: string;
  location: GeoLocation;
  phone: string;
  inventory: Record<BloodGroup, number>;
  last_updated: string;
}

export interface AIRecommendation {
  type: 'hospital' | 'resource' | 'route' | 'alert';
  priority: number;
  title: string;
  description: string;
  confidence: number;
  metadata?: Record<string, unknown>;
}

// ---- Dashboard -------------------------------------------

export interface DashboardStats {
  active_incidents: number;
  available_ambulances: number;
  total_ambulances: number;
  responding_units: number;
  average_response_time_min: number;
  incidents_today: number;
  resolved_today: number;
  critical_incidents: number;
  hospital_capacity_pct: number;
}

export interface IncidentTrend {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

export interface HotspotData {
  location: GeoLocation;
  intensity: number;
  incident_count: number;
  label?: string;
}

// ---- API Response wrappers -------------------------------

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ApiError {
  success: false;
  message: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

// ---- WebSocket events ------------------------------------

export type WSEventType =
  | 'incident.created'
  | 'incident.updated'
  | 'incident.resolved'
  | 'ambulance.location_updated'
  | 'ambulance.status_changed'
  | 'hospital.capacity_updated'
  | 'agent.started'
  | 'agent.completed'
  | 'dashboard.stats_updated'
  | 'heartbeat';

export interface WSMessage<T = unknown> {
  type: WSEventType;
  data: T;
  timestamp: string;
}

// ---- Form types ------------------------------------------

export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  full_name: string;
  role: UserRole;
}

export interface CreateIncidentFormData {
  title: string;
  description: string;
  severity: IncidentSeverity;
  address: string;
  location: GeoLocation;
  caller_name?: string;
  caller_phone?: string;
}

// ---- Pagination & Filters --------------------------------

export interface IncidentFilters {
  status?: IncidentStatus;
  severity?: IncidentSeverity;
  from_date?: string;
  to_date?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface AmbulanceFilters {
  status?: AmbulanceStatus;
  equipment_level?: string;
  page?: number;
  per_page?: number;
}
