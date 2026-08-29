import { Incident, IncidentSeverity, IncidentStatus } from '../types';

export const mockIncidents: Incident[] = [
  {
    id: '1',
    incident_number: 'INC-2026-001',
    title: 'Multi-vehicle collision on Highway 1',
    description: 'Severe accident involving a truck and two cars. Multiple injuries reported. Needs immediate medical and fire response.',
    severity: IncidentSeverity.CRITICAL,
    status: IncidentStatus.DISPATCHED,
    location: { lat: 37.7749, lng: -122.4194 },
    address: 'Highway 1, near Golden Gate, SF',
    reported_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    updated_at: new Date().toISOString(),
    created_by: 'user_1',
    assigned_ambulance_id: 'AMB-102',
    assigned_hospital_id: 'HOSP-SFG',
    eta_minutes: 8,
    timeline: [
      {
        id: 't1',
        incident_id: '1',
        action: 'INCIDENT_REPORTED',
        description: 'Call received from bystander reporting collision.',
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        actor_role: 'system'
      },
      {
        id: 't2',
        incident_id: '1',
        action: 'UNITS_DISPATCHED',
        description: 'Ambulance AMB-102 dispatched to scene.',
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        actor_role: 'dispatcher'
      }
    ],
    active_plan: {
      id: 'p1',
      incident_id: '1',
      generated_at: new Date(Date.now() - 1000 * 60 * 14).toISOString(),
      recommended_ambulances: ['AMB-102', 'AMB-105'],
      recommended_hospitals: ['HOSP-SFG'],
      estimated_response_time_mins: 10,
      instructions: [
        'Dispatch AMB-102 immediately (closest unit).',
        'Notify SF General Hospital trauma center.',
        'Request fire department for vehicle extrication.'
      ],
      status: 'EXECUTING'
    }
  },
  {
    id: '2',
    incident_number: 'INC-2026-002',
    title: 'Cardiac arrest at Downtown Mall',
    description: 'Elderly male collapsed. Bystanders performing CPR.',
    severity: IncidentSeverity.CRITICAL,
    status: IncidentStatus.AWAITING_APPROVAL,
    location: { lat: 37.7849, lng: -122.4094 },
    address: 'Westfield Mall, Market St',
    reported_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    updated_at: new Date().toISOString(),
    created_by: 'user_2',
    timeline: [
      {
        id: 't3',
        incident_id: '2',
        action: 'AI_PLAN_GENERATED',
        description: 'ARIA has generated an optimal response plan.',
        timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
        actor_role: 'bot'
      }
    ],
    active_plan: {
      id: 'p2',
      incident_id: '2',
      generated_at: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
      recommended_ambulances: ['AMB-201'],
      recommended_hospitals: ['HOSP-UCSF'],
      estimated_response_time_mins: 5,
      instructions: [
        'Dispatch ALS Ambulance AMB-201.',
        'Guide caller to locate nearest AED in mall.',
        'Alert UCSF Cardiology emergency team.'
      ],
      status: 'PENDING'
    }
  },
  {
    id: '3',
    incident_number: 'INC-2026-003',
    title: 'Minor injury at construction site',
    description: 'Worker sustained laceration to arm. Bleeding controlled.',
    severity: IncidentSeverity.LOW,
    status: IncidentStatus.PROCESSING,
    location: { lat: 37.7649, lng: -122.4294 },
    address: '1500 Mission St Construction',
    reported_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    updated_at: new Date().toISOString(),
    created_by: 'user_3',
  },
  {
    id: '4',
    incident_number: 'INC-2026-004',
    title: 'Residential fire with potential smoke inhalation',
    description: 'Kitchen fire in apartment complex. Fire department on scene requesting EMS standby.',
    severity: IncidentSeverity.MODERATE,
    status: IncidentStatus.PENDING,
    location: { lat: 37.7549, lng: -122.4194 },
    address: '24th St & Mission, SF',
    reported_at: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
    updated_at: new Date().toISOString(),
    created_by: 'user_1',
  }
];
