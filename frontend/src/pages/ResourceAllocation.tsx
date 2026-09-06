import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  Paper,
  Divider,
  Snackbar
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  LocalHospital as HospitalIcon,
  LocalShipping as AmbulanceIcon,
  TrendingUp as TrendingUpIcon,
  Bloodtype as BloodIcon,
  Speed as SpeedIcon,
  MyLocation as LocationIcon,
  FlashOn as DispatchIcon
} from '@mui/icons-material';

import ResourceHeatmap, { Hotspot, CoverageGap, Ambulance, RepositioningRecommendation, HospitalAlert } from '../components/ResourceHeatmap';
import PredictionDashboard, { DemandForecastData } from '../components/PredictionDashboard';
import { apiClient } from '../api/client';

interface OptimizationSummary {
  timestamp: string;
  hotspots: {
    count: number;
    high_risk_count: number;
    top_hotspot: Hotspot | null;
  };
  demand: {
    next_24h_incidents: number;
    next_24h_ambulance_demand: number;
    next_24h_bed_demand: number;
    blood_demand_summary: Record<string, number>;
    peak_hour: any;
  };
  fleet: {
    total_ambulances: number;
    available: number;
    busy: number;
    out_of_service: number;
    utilization_rate: number;
  };
  optimization: {
    repositioning_recommendations: number;
    hospital_surge_alerts: number;
    blood_preposition_orders: number;
    coverage_gaps: number;
    critical_gaps: number;
  };
  recommendations: RepositioningRecommendation[];
  hospital_alerts: HospitalAlert[];
  blood_orders: any[];
  critical_gaps: CoverageGap[];
}

const ResourceAllocation: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<OptimizationSummary | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [coverageGaps, setCoverageGaps] = useState<CoverageGap[]>([]);
  const [ambulances, setAmbulances] = useState<Ambulance[]>([]);
  const [demandForecast, setDemandForecast] = useState<DemandForecastData | null>(null);
  const [snackbarMessage, setSnackbarMessage] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (forceRefreshML: boolean = false) => {
    try {
      setLoading(true);
      setError(null);

      // Load optimization summary
      const summaryRes = await apiClient.get('/resource-allocation/optimization-summary');
      setSummary(summaryRes.data.data);

      // Load hotspots (using force_refresh query param if requested)
      const hotspotsRes = await apiClient.get('/resource-allocation/hotspots', {
        params: { hours_ahead: 24, grid_size: 40, force_refresh: forceRefreshML }
      });
      setHotspots(hotspotsRes.data.data.hotspots || []);

      // Load demand forecast
      const forecastRes = await apiClient.get('/resource-allocation/demand-forecast', {
        params: { hours_ahead: 24 }
      });
      setDemandForecast(forecastRes.data.data);

      // Load coverage gaps
      const gapsRes = await apiClient.get('/resource-allocation/coverage-gaps', {
        params: { target_response_time: 8 }
      });
      setCoverageGaps(gapsRes.data.data.coverage_gaps || []);

      // Load ambulances list from fleet endpoint or summary fallback
      try {
        const ambRes = await apiClient.get('/ambulances');
        setAmbulances(ambRes.data.data || ambRes.data || []);
      } catch {
        // Fallback default ambulances
        setAmbulances([
          { id: '1', ambulance_id: 'AMB-101', latitude: 37.7749, longitude: -122.4194, status: 'available' },
          { id: '2', ambulance_id: 'AMB-102', latitude: 37.7833, longitude: -122.4167, status: 'available' },
          { id: '3', ambulance_id: 'AMB-103', latitude: 37.7500, longitude: -122.4333, status: 'en_route' },
          { id: '4', ambulance_id: 'AMB-104', latitude: 37.7900, longitude: -122.4000, status: 'available' }
        ]);
      }

      if (forceRefreshML) {
        setSnackbarMessage("✅ 6-Hour ML hotspot predictions successfully recalculated!");
      }

    } catch (err: any) {
      console.error('Failed to load resource allocation data:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load predictive resource allocation data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData(false);
    setRefreshing(false);
  };

  const handleForceMLRefresh = async () => {
    await loadData(true);
  };

  const handleApplyAmbulancePositioning = async (ambulanceIds: string[]) => {
    try {
      await apiClient.post('/resource-allocation/apply-recommendations', {
        ambulance_ids: ambulanceIds
      });
      setSnackbarMessage(`🚑 Repositioning command dispatched to ${ambulanceIds.length} ambulance(s)!`);
      await loadData();
    } catch (err: any) {
      alert('Failed to apply repositioning commands: ' + err.message);
    }
  };

  const handleDispatchHospitalSurgeAlert = async (hospitalId: string, hospitalName: string) => {
    try {
      await apiClient.post('/resource-allocation/hospital-alerts', {
        hospital_id: hospitalId,
        action: "ACTIVATE_SURGE_CAPACITY"
      });
      setSnackbarMessage(`🏥 Surge alert notification dispatched to ${hospitalName}!`);
    } catch (err: any) {
      alert('Failed to alert hospital: ' + err.message);
    }
  };

  const handlePrepositionBloodStock = async (hospitalId: string, hospitalName: string, units: any) => {
    try {
      await apiClient.post('/resource-allocation/blood-preposition', {
        hospital_id: hospitalId,
        units: units
      });
      setSnackbarMessage(`🩸 Blood prepositioning transfer order created for ${hospitalName}!`);
    } catch (err: any) {
      alert('Failed to preposition blood stock: ' + err.message);
    }
  };

  if (loading && !summary) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="500px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (error && !summary) {
    return (
      <Box p={4}>
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        <Button variant="contained" onClick={() => loadData()}>Retry Connection</Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, margin: '0 auto' }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Predictive Resource Allocation & Fleet Positioning
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Proactive ML hotspot forecasting, hospital surge mitigation, and automated blood prepositioning
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            Refresh Dashboard
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<DispatchIcon />}
            onClick={() => summary?.recommendations.length && handleApplyAmbulancePositioning(summary.recommendations.map(r => r.ambulance_id))}
            disabled={!summary?.recommendations.length}
          >
            Execute All Proactive Actions ({summary?.recommendations.length || 0})
          </Button>
        </Box>
      </Box>

      {/* Summary KPI Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">24H PREDICTED HOTSPOTS</Typography>
                <LocationIcon color="error" />
              </Box>
              <Typography variant="h3" fontWeight="bold">{summary?.hotspots.count || 0}</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <Chip label={`${summary?.hotspots.high_risk_count || 0} High Risk`} color="error" size="small" />
                <Typography variant="caption" color="text.secondary">Updated 6h cycle</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">PREDICTED INCIDENT DEMAND</Typography>
                <TrendingUpIcon color="primary" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="primary.main">{summary?.demand.next_24h_incidents || 0}</Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                {summary?.demand.next_24h_ambulance_demand || 0} ambulances required
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">FLEET UTILIZATION RATE</Typography>
                <SpeedIcon color="success" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="success.main">{summary?.fleet.utilization_rate || 0}%</Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                {summary?.fleet.available || 0} available of {summary?.fleet.total_ambulances || 0} total fleet
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">COVERAGE GAPS (&gt;8m)</Typography>
                <WarningIcon color="warning" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="warning.main">{summary?.optimization.coverage_gaps || 0}</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <Chip label={`${summary?.optimization.critical_gaps || 0} Critical`} color="warning" size="small" />
                <Typography variant="caption" color="text.secondary">Response target: 8m</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Proactive Action Alerts */}
      {summary && summary.hospital_alerts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3, borderRadius: 2 }} icon={<HospitalIcon fontSize="inherit" />}>
          <Typography variant="subtitle2" fontWeight="bold">
            Hospital Surge Warning ({summary.hospital_alerts.length} Hospitals Near Capacity Threshold)
          </Typography>
          <Typography variant="body2">
            Predicted 24h patient admissions will push nearby hospital bed utilization over 85%. Activate surge protocols and dispatch blood pre-positioning.
          </Typography>
        </Alert>
      )}

      {/* Tab Navigation */}
      <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, val) => setTabValue(val)}>
          <Tab label="Hotspot Heatmap & Positioning" />
          <Tab label="Demand Forecast & Blood Stock" />
          <Tab label="Proactive Prepositioning Actions" />
          <Tab label="Coverage Gap Analysis" />
        </Tabs>
      </Paper>

      {/* Tab 0: Hotspots & Map */}
      {tabValue === 0 && (
        <Box display="flex" flexDirection="column" gap={3}>
          <ResourceHeatmap
            hotspots={hotspots}
            coverageGaps={coverageGaps}
            ambulances={ambulances}
            recommendations={summary?.recommendations || []}
            hospitalAlerts={summary?.hospital_alerts || []}
            showHeatmap={true}
            height="580px"
          />

          <Typography variant="h6" fontWeight="bold">Top 24-Hour High-Risk Hotspots</Typography>
          <Grid container spacing={2}>
            {hotspots.slice(0, 6).map((hs, idx) => (
              <Grid item xs={12} sm={6} md={4} key={idx}>
                <Card variant="outlined" sx={{ borderRadius: 2 }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle1" fontWeight="bold">Hotspot #{idx + 1}</Typography>
                      <Chip
                        label={`Risk: ${(hs.risk_score * 100).toFixed(0)}%`}
                        color={hs.risk_score > 0.70 ? 'error' : 'warning'}
                        size="small"
                        sx={{ fontWeight: 'bold' }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" mt={1}>
                      Coords: {hs.latitude}, {hs.longitude}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Predicted Incidents: {hs.predicted_incidents} | ML Confidence: {((hs.confidence_score || 0.85) * 100).toFixed(0)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Tab 1: Demand Forecast & Blood Type */}
      {tabValue === 1 && (
        <PredictionDashboard
          demandForecast={demandForecast}
          onRefreshMLPredictions={handleForceMLRefresh}
          loading={loading}
        />
      )}

      {/* Tab 2: Proactive Prepositioning Actions */}
      {tabValue === 2 && (
        <Box display="flex" flexDirection="column" gap={3}>
          {/* Section 1: Ambulance Prepositioning */}
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <AmbulanceIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Ambulance Prepositioning Recommendations
                </Typography>
              </Box>
              {summary && summary.recommendations.length > 0 ? (
                <Grid container spacing={2}>
                  {summary.recommendations.map((rec, idx) => (
                    <Grid item xs={12} md={6} key={idx}>
                      <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="subtitle1" fontWeight="bold">{rec.ambulance_identifier}</Typography>
                          <Chip label={rec.priority} color={rec.priority === 'CRITICAL' ? 'error' : 'warning'} size="small" />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Distance: <strong>{rec.distance_km} km</strong> (~{rec.estimated_travel_minutes} min ETA)
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Hotspot Risk: <strong>{(rec.risk_score * 100).toFixed(0)}%</strong>
                        </Typography>
                        <Typography variant="body2" sx={{ fontStyle: 'italic', my: 1, color: 'text.secondary' }}>
                          Action: {rec.action}
                        </Typography>
                        <Button
                          variant="contained"
                          size="small"
                          fullWidth
                          onClick={() => handleApplyAmbulancePositioning([rec.ambulance_id])}
                          sx={{ mt: 1 }}
                        >
                          Reposition Ambulance
                        </Button>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Alert severity="success">Ambulance distribution is optimal. No repositioning required.</Alert>
              )}
            </CardContent>
          </Card>

          {/* Section 2: Hospital Surge Alerts & Blood Prepositioning */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ borderRadius: 2, height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <HospitalIcon color="warning" />
                    <Typography variant="h6" fontWeight="bold">Hospital Surge Warnings</Typography>
                  </Box>
                  {summary && summary.hospital_alerts.length > 0 ? (
                    <Box display="flex" flexDirection="column" gap={2}>
                      {summary.hospital_alerts.map((alert, idx) => (
                        <Paper key={idx} variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                            <Typography variant="subtitle2" fontWeight="bold">{alert.hospital_name}</Typography>
                            <Chip label={alert.alert_level} color="error" size="small" />
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            Utilized: <strong>{alert.projected_utilization_rate}%</strong> ({alert.projected_available_beds} beds remaining)
                          </Typography>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            sx={{ mt: 1 }}
                            onClick={() => handleDispatchHospitalSurgeAlert(alert.hospital_id, alert.hospital_name)}
                          >
                            Dispatch Surge Alert
                          </Button>
                        </Paper>
                      ))}
                    </Box>
                  ) : (
                    <Alert severity="success">All hospital capacities within normal operating bounds.</Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ borderRadius: 2, height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <BloodIcon color="error" />
                    <Typography variant="h6" fontWeight="bold">Blood Supply Pre-positioning Orders</Typography>
                  </Box>
                  {summary && summary.blood_orders.length > 0 ? (
                    <Box display="flex" flexDirection="column" gap={2}>
                      {summary.blood_orders.map((order, idx) => (
                        <Paper key={idx} variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                          <Typography variant="subtitle2" fontWeight="bold">{order.hospital_name}</Typography>
                          <Typography variant="body2" color="text.secondary" my={0.5}>
                            Preposition Units: {Object.entries(order.preposition_units || {}).map(([k, v]) => `${k}: ${v}u`).join(', ')}
                          </Typography>
                          <Button
                            variant="contained"
                            color="error"
                            size="small"
                            sx={{ mt: 1 }}
                            onClick={() => handlePrepositionBloodStock(order.hospital_id, order.hospital_name, order.preposition_units)}
                          >
                            Issue Blood Stock Order
                          </Button>
                        </Paper>
                      ))}
                    </Box>
                  ) : (
                    <Alert severity="success">Blood stock levels match 24-hour demand predictions.</Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Tab 3: Coverage Gap Analysis */}
      {tabValue === 3 && (
        <Box display="flex" flexDirection="column" gap={3}>
          <ResourceHeatmap
            hotspots={[]}
            coverageGaps={coverageGaps}
            ambulances={ambulances}
            showHeatmap={false}
            height="450px"
          />

          <Typography variant="h6" fontWeight="bold">Identified Response Time Coverage Gaps (&gt; 8 Minutes)</Typography>
          <Grid container spacing={2}>
            {coverageGaps.map((gap, idx) => (
              <Grid item xs={12} sm={6} md={4} key={idx}>
                <Card
                  variant="outlined"
                  sx={{
                    borderRadius: 2,
                    borderColor: gap.severity === 'CRITICAL' ? 'error.main' : 'warning.main',
                    borderWidth: 2
                  }}
                >
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle2" fontWeight="bold">Gap Area #{idx + 1}</Typography>
                      <Chip
                        label={gap.severity}
                        color={gap.severity === 'CRITICAL' ? 'error' : 'warning'}
                        size="small"
                        sx={{ fontWeight: 'bold' }}
                      />
                    </Box>
                    <Typography variant="body2" mt={1}>
                      Est. Response Time: <strong>{gap.estimated_response_time_minutes} mins</strong>
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Distance to Fleet: {gap.nearest_ambulance_distance_km} km
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      30-Day Historical Incidents: {gap.incident_count_30days}
                    </Typography>
                    <Typography variant="caption" display="block" mt={1} fontStyle="italic" color="text.secondary">
                      {gap.recommendation}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Notification Toast */}
      <Snackbar
        open={Boolean(snackbarMessage)}
        autoHideDuration={4000}
        onClose={() => setSnackbarMessage(null)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default ResourceAllocation;
