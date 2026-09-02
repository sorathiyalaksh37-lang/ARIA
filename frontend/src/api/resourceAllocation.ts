import apiClient from './client';

export interface Hotspot {
  latitude: number;
  longitude: number;
  risk_score: number;
  predicted_incidents: number;
  hour: number;
  timestamp: string;
}

export interface CoverageGap {
  latitude: number;
  longitude: number;
  nearest_ambulance_distance_km: number;
  estimated_response_time_minutes: number;
  incident_count_30days: number;
  severity: string;
  recommendation: string;
}

export interface RepositioningRecommendation {
  ambulance_id: number;
  ambulance_identifier: string;
  current_location: {
    latitude: number;
    longitude: number;
  };
  recommended_location: {
    latitude: number;
    longitude: number;
  };
  hotspot_risk_score: number;
  distance_km: number;
  priority: string;
  reason: string;
}

export interface DemandForecast {
  forecast_generated_at: string;
  hours_ahead: number;
  forecasts: Array<{
    timestamp: string;
    hour: number;
    predicted_incidents: number;
    ambulance_demand: number;
    bed_demand: number;
    confidence: number;
  }>;
  total_predicted_incidents: number;
  peak_hour: {
    hour: number;
    predicted_incidents: number;
  };
}

export interface OptimizationSummary {
  timestamp: string;
  hotspots: {
    count: number;
    high_risk_count: number;
    top_hotspot: Hotspot | null;
  };
  demand: {
    next_24h_incidents: number;
    peak_hour: any;
  };
  fleet: {
    total_ambulances: number;
    available: number;
    utilization_rate: number;
  };
  optimization: {
    repositioning_recommendations: number;
    coverage_gaps: number;
    critical_gaps: number;
  };
  recommendations: RepositioningRecommendation[];
  critical_gaps: CoverageGap[];
}

export interface HeatmapData {
  type: string;
  data: Array<{
    location: [number, number];
    weight: number;
  }>;
  max_weight?: number;
  gradient?: Record<number, string>;
  time_range?: string;
}

export interface HospitalCapacityForecast {
  forecast_hours: number;
  total_predicted_admissions: number;
  hospital_projections: Array<{
    hospital_id: number;
    hospital_name: string;
    current_available_beds: number;
    expected_admissions: number;
    projected_available_beds: number;
    capacity_status: string;
  }>;
  hospitals_at_capacity: number;
}

/**
 * Get predicted incident hotspots
 */
export const getHotspots = async (
  hoursAhead: number = 24,
  gridSize: number = 50
) => {
  const response = await apiClient.get<{
    data: {
      hotspots: Hotspot[];
      hours_ahead: number;
      count: number;
      prediction_time: string;
    };
  }>('/resource-allocation/hotspots', {
    params: { hours_ahead: hoursAhead, grid_size: gridSize }
  });
  return response.data.data;
};

/**
 * Get incident demand forecast
 */
export const getDemandForecast = async (hoursAhead: number = 24) => {
  const response = await apiClient.get<{ data: DemandForecast }>(
    '/resource-allocation/demand-forecast',
    { params: { hours_ahead: hoursAhead } }
  );
  return response.data.data;
};

/**
 * Get ambulance repositioning recommendations
 */
export const getAmbulancePositioning = async (hoursAhead: number = 6) => {
  const response = await apiClient.get<{
    data: {
      recommendations: RepositioningRecommendation[];
      total_recommendations: number;
      available_ambulances: number;
      hotspots_analyzed: number;
    };
  }>('/resource-allocation/ambulance-positioning', {
    params: { hours_ahead: hoursAhead }
  });
  return response.data.data;
};

/**
 * Get coverage gaps
 */
export const getCoverageGaps = async (targetResponseTime: number = 8) => {
  const response = await apiClient.get<{
    data: {
      coverage_gaps: CoverageGap[];
      total_gaps: number;
      critical_gaps: number;
      high_priority_gaps: number;
      target_response_time: number;
      active_ambulances: number;
    };
  }>('/resource-allocation/coverage-gaps', {
    params: { target_response_time: targetResponseTime }
  });
  return response.data.data;
};

/**
 * Get heatmap data
 */
export const getHeatmap = async (
  metric: 'risk' | 'demand' | 'coverage' | 'incidents' = 'risk'
) => {
  const response = await apiClient.get<{ data: HeatmapData }>(
    '/resource-allocation/heatmap',
    { params: { metric } }
  );
  return response.data.data;
};

/**
 * Get comprehensive optimization summary
 */
export const getOptimizationSummary = async () => {
  const response = await apiClient.get<{ data: OptimizationSummary }>(
    '/resource-allocation/optimization-summary'
  );
  return response.data.data;
};

/**
 * Apply repositioning recommendations
 */
export const applyRecommendations = async (ambulanceIds: string[]) => {
  const response = await apiClient.post<{
    data: {
      applied_recommendations: Array<{
        ambulance_id: string;
        new_position: { latitude: number; longitude: number };
        status: string;
      }>;
      count: number;
    };
  }>('/resource-allocation/apply-recommendations', {
    ambulance_ids: ambulanceIds
  });
  return response.data.data;
};

/**
 * Get hospital capacity forecast
 */
export const getHospitalCapacityForecast = async (hoursAhead: number = 12) => {
  const response = await apiClient.get<{ data: HospitalCapacityForecast }>(
    '/resource-allocation/hospital-capacity-forecast',
    { params: { hours_ahead: hoursAhead } }
  );
  return response.data.data;
};

export default {
  getHotspots,
  getDemandForecast,
  getAmbulancePositioning,
  getCoverageGaps,
  getHeatmap,
  getOptimizationSummary,
  applyRecommendations,
  getHospitalCapacityForecast,
};
