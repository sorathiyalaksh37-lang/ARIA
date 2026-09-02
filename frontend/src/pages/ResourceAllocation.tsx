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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  LocalHospital as HospitalIcon,
  LocalShipping as AmbulanceIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

import ResourceHeatmap from '../components/ResourceHeatmap';
import { apiClient } from '../api/client';

// Fix leaflet default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface OptimizationSummary {
  timestamp: string;
  hotspots: {
    count: number;
    high_risk_count: number;
    top_hotspot: any;
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
  recommendations: any[];
  critical_gaps: any[];
}

interface Hotspot {
  latitude: number;
  longitude: number;
  risk_score: number;
  predicted_incidents: number;
}

interface CoverageGap {
  latitude: number;
  longitude: number;
  nearest_ambulance_distance_km: number;
  estimated_response_time_minutes: number;
  incident_count_30days: number;
  severity: string;
  recommendation: string;
}

const ResourceAllocation: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [summary, setSummary] = useState<OptimizationSummary | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [coverageGaps, setCoverageGaps] = useState<CoverageGap[]>([]);
  const [forecastHours, setForecastHours] = useState(24);
  const [demandForecast, setDemandForecast] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load optimization summary
      const summaryResponse = await apiClient.get('/resource-allocation/optimization-summary');
      setSummary(summaryResponse.data.data);

      // Load detailed hotspots
      const hotspotsResponse = await apiClient.get('/resource-allocation/hotspots', {
        params: { hours_ahead: 6, grid_size: 40 }
      });
      setHotspots(hotspotsResponse.data.data.hotspots);

      // Load coverage gaps
      const gapsResponse = await apiClient.get('/resource-allocation/coverage-gaps', {
        params: { target_response_time: 8 }
      });
      setCoverageGaps(gapsResponse.data.data.coverage_gaps);

      // Load demand forecast
      const forecastResponse = await apiClient.get('/resource-allocation/demand-forecast', {
        params: { hours_ahead: forecastHours }
      });
      setDemandForecast(forecastResponse.data.data);

    } catch (err: any) {
      console.error('Failed to load resource allocation data:', err);
      setError(err.response?.data?.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleApplyRecommendations = async (ambulanceIds: string[]) => {
    try {
      await apiClient.post('/resource-allocation/apply-recommendations', {
        ambulance_ids: ambulanceIds
      });
      alert('Repositioning recommendations sent to selected ambulances');
      await loadData();
    } catch (err: any) {
      alert('Failed to apply recommendations: ' + err.message);
    }
  };

  if (loading && !summary) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !summary) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
        <Button onClick={loadData} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Resource Allocation & Optimization
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ML-powered predictive resource positioning
          </Typography>
        </Box>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <WarningIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Hotspots</Typography>
              </Box>
              <Typography variant="h4">{summary?.hotspots.count || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                {summary?.hotspots.high_risk_count || 0} high risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Predicted Demand</Typography>
              </Box>
              <Typography variant="h4">
                {summary?.demand.next_24h_incidents || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                incidents next 24h
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AmbulanceIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Fleet Status</Typography>
              </Box>
              <Typography variant="h4">
                {summary?.fleet.available || 0}/{summary?.fleet.total_ambulances || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {summary?.fleet.utilization_rate || 0}% utilization
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Coverage Gaps</Typography>
              </Box>
              <Typography variant="h4">
                {summary?.optimization.coverage_gaps || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {summary?.optimization.critical_gaps || 0} critical
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts */}
      {summary && summary.optimization.critical_gaps > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Critical Coverage Gaps Detected
          </Typography>
          <Typography variant="body2">
            {summary.optimization.critical_gaps} areas have response times exceeding 15 minutes.
            Immediate repositioning recommended.
          </Typography>
        </Alert>
      )}

      {summary && summary.optimization.repositioning_recommendations > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Repositioning Recommendations Available
          </Typography>
          <Typography variant="body2">
            {summary.optimization.repositioning_recommendations} ambulances can be repositioned
            to improve coverage. View recommendations in the Optimization tab.
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Hotspots Map" />
          <Tab label="Coverage Analysis" />
          <Tab label="Demand Forecast" />
          <Tab label="Optimization" />
        </Tabs>
      </Box>

      {/* Hotspots Tab */}
      <TabPanel value={tabValue} index={0}>
        <ResourceHeatmap
          hotspots={hotspots}
          coverageGaps={[]}
          ambulances={[]}
          showHeatmap={true}
        />
        
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Top Risk Areas
          </Typography>
          <Grid container spacing={2}>
            {hotspots.slice(0, 6).map((hotspot, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle2">
                        Area #{index + 1}
                      </Typography>
                      <Chip
                        label={`Risk: ${(hotspot.risk_score * 100).toFixed(0)}%`}
                        color={hotspot.risk_score > 0.7 ? 'error' : 'warning'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" mt={1}>
                      Location: {hotspot.latitude.toFixed(4)}, {hotspot.longitude.toFixed(4)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Predicted incidents: {hotspot.predicted_incidents}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </TabPanel>

      {/* Coverage Analysis Tab */}
      <TabPanel value={tabValue} index={1}>
        <ResourceHeatmap
          hotspots={[]}
          coverageGaps={coverageGaps}
          ambulances={[]}
          showHeatmap={false}
        />
        
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Coverage Gaps
          </Typography>
          {coverageGaps.length === 0 ? (
            <Alert severity="success" icon={<CheckCircleIcon />}>
              Excellent! No significant coverage gaps detected.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {coverageGaps.slice(0, 6).map((gap, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card
                    variant="outlined"
                    sx={{
                      borderColor: gap.severity === 'critical' ? 'error.main' : 'warning.main',
                      borderWidth: 2
                    }}
                  >
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="subtitle2">
                          Gap #{index + 1}
                        </Typography>
                        <Chip
                          label={gap.severity.toUpperCase()}
                          color={gap.severity === 'critical' ? 'error' : 'warning'}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" mt={1}>
                        Response time: {gap.estimated_response_time_minutes.toFixed(1)} min
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Distance: {gap.nearest_ambulance_distance_km.toFixed(2)} km
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Incidents (30d): {gap.incident_count_30days}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                        {gap.recommendation}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </TabPanel>

      {/* Demand Forecast Tab */}
      <TabPanel value={tabValue} index={2}>
        <Box mb={3}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Forecast Horizon</InputLabel>
            <Select
              value={forecastHours}
              onChange={(e) => setForecastHours(e.target.value as number)}
              label="Forecast Horizon"
            >
              <MenuItem value={12}>12 hours</MenuItem>
              <MenuItem value={24}>24 hours</MenuItem>
              <MenuItem value={48}>48 hours</MenuItem>
              <MenuItem value={72}>72 hours</MenuItem>
            </Select>
          </FormControl>
          <Button onClick={loadData} sx={{ ml: 2 }} variant="contained">
            Update Forecast
          </Button>
        </Box>

        {demandForecast && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Forecast Summary
                  </Typography>
                  <Box mt={2}>
                    <Typography variant="body2" color="text.secondary">
                      Total Predicted Incidents
                    </Typography>
                    <Typography variant="h4">
                      {demandForecast.total_predicted_incidents?.toFixed(0) || 0}
                    </Typography>
                  </Box>
                  <Box mt={2}>
                    <Typography variant="body2" color="text.secondary">
                      Peak Hour
                    </Typography>
                    <Typography variant="h6">
                      {demandForecast.peak_hour?.hour || 'N/A'}:00
                    </Typography>
                    <Typography variant="body2">
                      {demandForecast.peak_hour?.predicted_incidents?.toFixed(1) || 0} incidents expected
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Resource Requirements (Next Hour)
                  </Typography>
                  {demandForecast.forecasts && demandForecast.forecasts[0] && (
                    <Box>
                      <Box mt={2}>
                        <Typography variant="body2" color="text.secondary">
                          Ambulances Needed
                        </Typography>
                        <Typography variant="h4">
                          {demandForecast.forecasts[0].ambulance_demand}
                        </Typography>
                      </Box>
                      <Box mt={2}>
                        <Typography variant="body2" color="text.secondary">
                          Hospital Beds Needed
                        </Typography>
                        <Typography variant="h4">
                          {demandForecast.forecasts[0].bed_demand}
                        </Typography>
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Hourly Forecast
                  </Typography>
                  <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                    {demandForecast.forecasts?.slice(0, 24).map((forecast: any, index: number) => (
                      <Box
                        key={index}
                        display="flex"
                        justifyContent="space-between"
                        alignItems="center"
                        p={1}
                        sx={{
                          borderBottom: '1px solid',
                          borderColor: 'divider',
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                      >
                        <Typography variant="body2">
                          Hour {forecast.hour}:00
                        </Typography>
                        <Box display="flex" gap={2}>
                          <Chip
                            label={`${forecast.predicted_incidents} incidents`}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Chip
                            label={`${forecast.ambulance_demand} ambulances`}
                            size="small"
                            color="secondary"
                            variant="outlined"
                          />
                          <Chip
                            label={`${forecast.bed_demand} beds`}
                            size="small"
                            color="info"
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      {/* Optimization Tab */}
      <TabPanel value={tabValue} index={3}>
        <Typography variant="h6" gutterBottom>
          Repositioning Recommendations
        </Typography>

        {summary && summary.recommendations.length === 0 ? (
          <Alert severity="success" icon={<CheckCircleIcon />}>
            No repositioning needed. Current ambulance distribution is optimal.
          </Alert>
        ) : (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              The following ambulances can be repositioned to improve coverage and reduce response times.
            </Alert>

            <Grid container spacing={2}>
              {summary?.recommendations.map((rec, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">
                          {rec.ambulance_identifier}
                        </Typography>
                        <Chip
                          label={rec.priority.toUpperCase()}
                          color={rec.priority === 'high' ? 'error' : 'warning'}
                          size="small"
                        />
                      </Box>

                      <Box mb={2}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Current Location
                        </Typography>
                        <Typography variant="body2">
                          {rec.current_location.latitude.toFixed(4)}, {rec.current_location.longitude.toFixed(4)}
                        </Typography>
                      </Box>

                      <Box mb={2}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Recommended Location
                        </Typography>
                        <Typography variant="body2">
                          {rec.recommended_location.latitude.toFixed(4)}, {rec.recommended_location.longitude.toFixed(4)}
                        </Typography>
                      </Box>

                      <Box mb={2}>
                        <Typography variant="body2" color="text.secondary">
                          Distance: {rec.distance_km} km
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Hotspot Risk: {(rec.hotspot_risk_score * 100).toFixed(0)}%
                        </Typography>
                      </Box>

                      <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 2 }}>
                        {rec.reason}
                      </Typography>

                      <Button
                        variant="contained"
                        size="small"
                        fullWidth
                        onClick={() => handleApplyRecommendations([rec.ambulance_identifier])}
                      >
                        Apply Recommendation
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {summary && summary.recommendations.length > 0 && (
              <Box mt={3}>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={() => handleApplyRecommendations(
                    summary.recommendations.map(r => r.ambulance_identifier)
                  )}
                >
                  Apply All Recommendations
                </Button>
              </Box>
            )}
          </Box>
        )}
      </TabPanel>
    </Box>
  );
};

export default ResourceAllocation;
