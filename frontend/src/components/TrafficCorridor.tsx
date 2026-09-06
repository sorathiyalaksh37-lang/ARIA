import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Paper,
  Alert,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  Map as MapIcon,
  Navigation as NavIcon,
  AltRoute as FallbackIcon,
  Traffic as TrafficIcon,
  CheckCircle as CheckIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import TrafficStatus, { TrafficSignalNode, TimeSavings } from './TrafficStatus';
import { apiClient } from '../api/client';

const TrafficCorridor: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [corridorData, setCorridorData] = useState<any>(null);
  const [signalNodes, setSignalNodes] = useState<TrafficSignalNode[]>([]);
  const [timeSavings, setTimeSavings] = useState<TimeSavings | null>(null);
  const [manualOverrideActive, setManualOverrideActive] = useState(false);
  const [fallbackActive, setFallbackActive] = useState(false);
  const [fallbackData, setFallbackData] = useState<any>(null);

  useEffect(() => {
    loadCorridorData();
  }, []);

  const loadCorridorData = async () => {
    try {
      setLoading(true);
      // 1. Fetch green corridor status
      const statusRes = await apiClient.get('/traffic/corridor/status');
      const data = statusRes.data.data;
      setCorridorData(data);
      setSignalNodes(data.preempted_nodes || []);
      setManualOverrideActive(Boolean(data.manual_override));

      // 2. Fetch time savings
      const savingsRes = await apiClient.get('/traffic/time-savings?distance_km=7.8&normal_stops=8');
      setTimeSavings(savingsRes.data.data);
    } catch (err: any) {
      console.error('Error loading traffic corridor data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleOverride = async (enable: boolean) => {
    try {
      const res = await apiClient.post('/traffic/corridor/override', { enable_override: enable });
      setManualOverrideActive(enable);
      await loadCorridorData();
    } catch (err: any) {
      alert('Failed to toggle override: ' + err.message);
    }
  };

  const handleTriggerFallback = async () => {
    try {
      const res = await apiClient.get('/traffic/fallback-route');
      setFallbackData(res.data.data);
      setFallbackActive(true);
    } catch (err: any) {
      alert('Failed to get fallback route: ' + err.message);
    }
  };

  if (loading && !corridorData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="500px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, margin: '0 auto' }}>
      {/* Header Controls */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          bgcolor: 'primary.50',
          border: '1px solid',
          borderColor: 'primary.200',
          borderRadius: 3,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <TrafficIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h5" fontWeight="bold" color="primary.900">
              Smart Traffic Light Integration (Green Corridor)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time ATCS preemption clears traffic signals ahead of ambulance AMB-402
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1.5}>
          <Button
            variant="outlined"
            onClick={loadCorridorData}
            startIcon={<RefreshIcon />}
          >
            Refresh Route
          </Button>

          <Button
            variant={fallbackActive ? 'contained' : 'outlined'}
            color="warning"
            onClick={handleTriggerFallback}
            startIcon={<FallbackIcon />}
          >
            {fallbackActive ? 'Fallback Active' : 'Test Fallback Route'}
          </Button>
        </Box>
      </Paper>

      {/* Fallback Alert Banner */}
      {fallbackActive && fallbackData && (
        <Alert severity="warning" sx={{ mb: 3, borderRadius: 2 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            🚨 FALLBACK MODE ACTIVATED: {fallbackData.reason}
          </Typography>
          <Typography variant="body2">{fallbackData.fallback_advisory}</Typography>
        </Alert>
      )}

      {/* Map Route Card Placeholder */}
      <Card variant="outlined" sx={{ borderRadius: 3, mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <MapIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Live Ambulance Green Corridor Polyline Map
              </Typography>
            </Box>
            <Chip label="PREEMPTION MATRIX ACTIVE" color="success" size="small" sx={{ fontWeight: 'bold' }} />
          </Box>

          <Paper
            variant="outlined"
            sx={{
              p: 4,
              minHeight: 280,
              bgcolor: 'grey.900',
              color: 'white',
              borderRadius: 3,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {/* Visual Corridor Line Representation */}
            <Box display="flex" alignItems="center" gap={3} width="80%" mb={3}>
              <Paper sx={{ p: 1.5, bgcolor: 'error.main', color: 'white', borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight="bold">🚑 AMB-402</Typography>
                <Typography variant="caption">Speed: 68 km/h</Typography>
              </Paper>

              <Box flexGrow={1} height={6} bgcolor="success.main" borderRadius={3} position="relative">
                <Box
                  position="absolute"
                  top="-6px"
                  left="30%"
                  sx={{ width: 18, height: 18, borderRadius: '50%', bgcolor: 'success.light', border: '2px solid white' }}
                />
                <Box
                  position="absolute"
                  top="-6px"
                  left="60%"
                  sx={{ width: 18, height: 18, borderRadius: '50%', bgcolor: 'success.light', border: '2px solid white' }}
                />
              </Box>

              <Paper sx={{ p: 1.5, bgcolor: 'primary.main', color: 'white', borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight="bold">🏥 General Trauma Center</Typography>
                <Typography variant="caption">ETA: 9 mins</Typography>
              </Paper>
            </Box>

            <Box display="flex" gap={2} flexWrap="wrap">
              {signalNodes.map((n) => (
                <Chip
                  key={n.signal_id}
                  label={`🚦 ${n.intersection_name}: ${n.light_color}`}
                  color={n.light_color === 'GREEN' ? 'success' : 'error'}
                  sx={{ fontWeight: 'bold' }}
                />
              ))}
            </Box>
          </Paper>
        </CardContent>
      </Card>

      {/* Main Status & Override Component */}
      {timeSavings && (
        <TrafficStatus
          signalNodes={signalNodes}
          timeSavings={timeSavings}
          manualOverrideActive={manualOverrideActive}
          onToggleOverride={handleToggleOverride}
          onRefresh={loadCorridorData}
        />
      )}
    </Box>
  );
};

export default TrafficCorridor;
