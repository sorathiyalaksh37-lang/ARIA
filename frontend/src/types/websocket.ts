/**
 * Types for WebSockets and Real-time Communication
 */

/**
 * All supported WebSocket events in the system.
 */
export enum WebSocketEvent {
  INCIDENT_CREATED = 'incident.created',
  INCIDENT_UPDATED = 'incident.updated',
  INCIDENT_PLAN_GENERATED = 'incident.plan_generated',
  INCIDENT_APPROVED = 'incident.approved',
  INCIDENT_DISPATCHED = 'incident.dispatched',
  AMBULANCE_LOCATION_UPDATED = 'ambulance.location_updated',
  HOSPITAL_AVAILABILITY_UPDATED = 'hospital.availability_updated',
  AGENT_STATUS_UPDATED = 'agent.status_updated',
  DASHBOARD_UPDATED = 'dashboard.updated',
  HEARTBEAT = 'heartbeat',
}

/**
 * Generic interface for incoming WebSocket messages.
 */
export interface WebSocketMessage<T = any> {
  event: WebSocketEvent;
  data: T;
  timestamp: string;
}

/**
 * Status representation for backend execution agents.
 */
export interface AgentStatus {
  agent_id: string;
  name: string;
  status: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  incident_id?: string;
  started_at?: string;
  completed_at?: string;
  execution_time_ms?: number;
  error?: string;
}
