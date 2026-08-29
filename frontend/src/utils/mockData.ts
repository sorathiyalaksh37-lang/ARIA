import { 
  Incident, IncidentSeverity, IncidentStatus,
  Ambulance, AmbulanceStatus, AmbulanceType,
  Hospital,
  BloodBank, BloodType
} from '../types';

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

export const mockHospitals: Hospital[] = [
  {
    id: 'HOSP-SFG',
    name: 'SF General Hospital',
    address: '1001 Potrero Ave, San Francisco',
    location: { lat: 37.7554, lng: -122.4053 },
    phone: '555-0100',
    specialties: ['Trauma Center Level I', 'Burn Center', 'Cardiac'],
    is_active: true,
    availability: {
      total_beds: 400,
      available_beds: 45,
      icu_beds: 50,
      available_icu_beds: 5,
      emergency_capacity: 85,
      last_updated: new Date().toISOString()
    }
  },
  {
    id: 'HOSP-UCSF',
    name: 'UCSF Medical Center',
    address: '505 Parnassus Ave, San Francisco',
    location: { lat: 37.7631, lng: -122.4586 },
    phone: '555-0200',
    specialties: ['Pediatrics', 'Neurology', 'Organ Transplant'],
    is_active: true,
    availability: {
      total_beds: 600,
      available_beds: 120,
      icu_beds: 80,
      available_icu_beds: 15,
      emergency_capacity: 60,
      last_updated: new Date().toISOString()
    }
  },
  {
    id: 'HOSP-KAI',
    name: 'Kaiser Permanente SF',
    address: '2425 Geary Blvd, San Francisco',
    location: { lat: 37.7828, lng: -122.4439 },
    phone: '555-0300',
    specialties: ['General Surgery', 'Obstetrics', 'Orthopedics'],
    is_active: true,
    availability: {
      total_beds: 250,
      available_beds: 10,
      icu_beds: 30,
      available_icu_beds: 2,
      emergency_capacity: 95, // high utilization
      last_updated: new Date().toISOString()
    }
  }
];

export const mockAmbulances: Ambulance[] = [
  {
    id: 'AMB-102',
    unit_number: '102',
    type: AmbulanceType.ADVANCED_LIFE_SUPPORT,
    status: AmbulanceStatus.EN_ROUTE,
    location: { lat: 37.7699, lng: -122.4144 },
    crew_count: 2,
    current_incident_id: '1',
    last_updated: new Date().toISOString(),
    fuel_level_pct: 75
  },
  {
    id: 'AMB-105',
    unit_number: '105',
    type: AmbulanceType.BASIC,
    status: AmbulanceStatus.AVAILABLE,
    location: { lat: 37.7949, lng: -122.4094 },
    crew_count: 2,
    last_updated: new Date().toISOString(),
    fuel_level_pct: 90
  },
  {
    id: 'AMB-201',
    unit_number: '201',
    type: AmbulanceType.CRITICAL_CARE,
    status: AmbulanceStatus.AVAILABLE,
    location: { lat: 37.7849, lng: -122.4394 },
    crew_count: 3,
    last_updated: new Date().toISOString(),
    fuel_level_pct: 45
  },
  {
    id: 'AMB-303',
    unit_number: '303',
    type: AmbulanceType.BASIC,
    status: AmbulanceStatus.TRANSPORTING,
    location: { lat: 37.7519, lng: -122.4224 },
    crew_count: 2,
    last_updated: new Date().toISOString(),
    fuel_level_pct: 60
  }
];

export const mockBloodBanks: BloodBank[] = [
  {
    id: 'BB-001',
    name: 'SF Community Blood Center',
    address: '270 Masonic Ave, San Francisco',
    location: { lat: 37.7788, lng: -122.4468 },
    phone: '555-0400',
    last_updated: new Date().toISOString(),
    inventory: {
      [BloodType.A_POS]: 150,
      [BloodType.A_NEG]: 45,
      [BloodType.B_POS]: 85,
      [BloodType.B_NEG]: 20,
      [BloodType.O_POS]: 220,
      [BloodType.O_NEG]: 30, // Critical
      [BloodType.AB_POS]: 40,
      [BloodType.AB_NEG]: 10
    }
  },
  {
    id: 'BB-002',
    name: 'Red Cross Regional Center',
    address: '1663 Market St, San Francisco',
    location: { lat: 37.7725, lng: -122.4217 },
    phone: '555-0500',
    last_updated: new Date().toISOString(),
    inventory: {
      [BloodType.A_POS]: 300,
      [BloodType.A_NEG]: 90,
      [BloodType.B_POS]: 120,
      [BloodType.B_NEG]: 35,
      [BloodType.O_POS]: 400,
      [BloodType.O_NEG]: 80,
      [BloodType.AB_POS]: 60,
      [BloodType.AB_NEG]: 25
    }
  }
];
