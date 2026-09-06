import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Button,
  Divider,
  Paper,
  Tooltip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  LocalHospital as HospitalIcon,
  LocalShipping as AmbulanceIcon,
  Bloodtype as BloodIcon,
  AccessTime as TimeIcon,
  Speed as SpeedIcon,
  AutoRenew as RefreshIcon
} from '@mui/icons-material';

export interface DemandForecastData {
  forecast_generated_at: string;
  hours_ahead: number;
  total_predicted_incidents: number;
  total_ambulance_demand: number;
  total_bed_demand: number;
  peak_hour?: {
    hour: number;
    timestamp: string;
    predicted_incidents: number;
    ambulance_demand: number;
  };
  blood_demand_summary?: Record<string, number>;
  forecasts: Array<{
    timestamp: string;
    hour: number;
    predicted_incidents: number;
    ambulance_demand: number;
    bed_demand: number;
    blood_type_demand?: Record<string, number>;
    confidence: number;
  }>;
  next_cache_update?: string;
}

interface PredictionDashboardProps {
  demandForecast: DemandForecastData | null;
  onRefreshMLPredictions: () => void;
  loading?: boolean;
}

const PredictionDashboard: React.FC<PredictionDashboardProps> = ({
  demandForecast,
  onRefreshMLPredictions,
  loading = false
}) => {
  if (!demandForecast) {
    return (
      <Box p={4} textAlign="center">
        <Typography color="text.secondary">No ML forecast data loaded.</Typography>
      </Box>
    );
  }

  const bloodTypes = demandForecast.blood_demand_summary || {};
  const maxBloodUnits = Math.max(...Object.values(bloodTypes), 1);

  return (
    <Box>
      {/* Top Banner: 6-Hour Update Cycle Indicator */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 3,
          bgcolor: 'primary.50',
          border: '1px solid',
          borderColor: 'primary.200',
          borderRadius: 2,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <Box display="flex" alignItems="center" gap={1.5}>
          <TimeIcon color="primary" sx={{ fontSize: 28 }} />
          <Box>
            <Typography variant="subtitle1" fontWeight="bold" color="primary.900">
              6-Hour ML Hotspot & Demand Prediction Engine
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Last updated: {new Date(demandForecast.forecast_generated_at).toLocaleTimeString()} | Next scheduled sync in ~6 hours
            </Typography>
          </Box>
        </Box>
        <Button
          variant="contained"
          size="small"
          startIcon={<RefreshIcon />}
          onClick={onRefreshMLPredictions}
          disabled={loading}
        >
          {loading ? 'Recalculating ML...' : 'Force ML Recalculation'}
        </Button>
      </Paper>

      {/* Summary KPI Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">
                  24H PREDICTED INCIDENTS
                </Typography>
                <TrendingUpIcon color="primary" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="primary.main">
                {demandForecast.total_predicted_incidents}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                Peak at {demandForecast.peak_hour?.hour}:00 ({demandForecast.peak_hour?.predicted_incidents} inc/hr)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">
                  AMBULANCE DISPATCH NEED
                </Typography>
                <AmbulanceIcon color="success" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="success.main">
                {demandForecast.total_ambulance_demand}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                85% immediate dispatch probability
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">
                  HOSPITAL BED DEMAND
                </Typography>
                <HospitalIcon color="warning" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="warning.main">
                {demandForecast.total_bed_demand}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                60% expected admission rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" fontWeight="bold">
                  TRAUMA BLOOD UNITS
                </Typography>
                <BloodIcon color="error" />
              </Box>
              <Typography variant="h3" fontWeight="bold" color="error.main">
                {Object.values(bloodTypes).reduce((a, b) => a + b, 0).toFixed(0)}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                Universal O- & A+ priority allocation
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Breakdown Section */}
      <Grid container spacing={3}>
        {/* Blood Type Demand Breakdown */}
        <Grid item xs={12} md={5}>
          <Card variant="outlined" sx={{ borderRadius: 2, height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <BloodIcon color="error" />
                <Typography variant="h6" fontWeight="bold">
                  Blood Type Demand Forecast
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Predicted blood unit requirements across trauma centers based on incident severity profiles.
              </Typography>

              <Grid container spacing={2}>
                {Object.entries(bloodTypes).map(([btype, units]) => {
                  const isUniversal = btype === 'O-';
                  const percent = Math.min(100, Math.round((units / maxBloodUnits) * 100));

                  return (
                    <Grid item xs={12} key={btype}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip
                            label={btype}
                            size="small"
                            color={isUniversal ? 'error' : 'default'}
                            sx={{ fontWeight: 'bold', width: 45 }}
                          />
                          {isUniversal && (
                            <Chip label="UNIVERSAL DONOR" size="small" color="error" variant="outlined" sx={{ fontSize: 10, height: 18 }} />
                          )}
                        </Box>
                        <Typography variant="body2" fontWeight="bold">
                          {units.toFixed(1)} Units
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={percent}
                        color={isUniversal ? 'error' : 'primary'}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Hourly Forecast Chart & Table */}
        <Grid item xs={12} md={7}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" fontWeight="bold">
                  24-Hour Demand Breakdown by Hour
                </Typography>
                <Chip label="ML Confidence: 85%" color="info" size="small" />
              </Box>

              <Box sx={{ maxHeight: 420, overflowY: 'auto', pr: 1 }}>
                {demandForecast.forecasts.slice(0, 24).map((fc, idx) => (
                  <Paper
                    key={idx}
                    variant="outlined"
                    sx={{
                      p: 1.5,
                      mb: 1,
                      bgcolor: fc.hour === demandForecast.peak_hour?.hour ? 'warning.50' : 'background.paper',
                      borderColor: fc.hour === demandForecast.peak_hour?.hour ? 'warning.300' : 'divider',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      borderRadius: 1.5
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="subtitle2" fontWeight="bold" sx={{ width: 65 }}>
                        {fc.hour.toString().padStart(2, '0')}:00
                      </Typography>
                      {fc.hour === demandForecast.peak_hour?.hour && (
                        <Chip label="PEAK SURGE" color="warning" size="small" sx={{ fontSize: 10, height: 20 }} />
                      )}
                    </Box>

                    <Box display="flex" gap={1.5} alignItems="center">
                      <Tooltip title="Predicted Incidents">
                        <Chip
                          icon={<TrendingUpIcon />}
                          label={`${fc.predicted_incidents} inc`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Tooltip>
                      <Tooltip title="Ambulance Demand">
                        <Chip
                          icon={<AmbulanceIcon />}
                          label={`${fc.ambulance_demand} amb`}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </Tooltip>
                      <Tooltip title="Hospital Bed Demand">
                        <Chip
                          icon={<HospitalIcon />}
                          label={`${fc.bed_demand} beds`}
                          size="small"
                          color="warning"
                          variant="outlined"
                        />
                      </Tooltip>
                    </Box>
                  </Paper>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PredictionDashboard;
