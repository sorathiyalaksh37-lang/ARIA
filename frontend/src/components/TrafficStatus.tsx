import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Paper,
  Divider,
  Alert,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  LinearProgress
} from '@mui/material';
import {
  Traffic as TrafficIcon,
  Timer as TimerIcon,
  FlashOn as OverrideIcon,
  CheckCircle as GreenIcon,
  Warning as RedIcon,
  Speed as SpeedIcon,
  Sensors as SensorsIcon
} from '@mui/icons-material';

import { apiClient } from '../api/client';

export interface TrafficSignalNode {
  signal_id: string;
  intersection_name: string;
  status: string;
  light_color: 'GREEN' | 'RED' | 'YELLOW';
  time_to_preemption_sec: number;
  preemption_active: boolean;
}

export interface TimeSavings {
  distance_km: number;
  normal_route: { estimated_minutes: number; traffic_light_stops: number; avg_speed_kmh: number };
  green_corridor_route: { estimated_minutes: number; traffic_light_stops: number; avg_speed_kmh: number };
  time_saved_minutes: number;
  percentage_time_saved: number;
}

interface TrafficStatusProps {
  signalNodes: TrafficSignalNode[];
  timeSavings: TimeSavings;
  manualOverrideActive: boolean;
  onToggleOverride: (enable: boolean) => void;
  onRefresh?: () => void;
}

const TrafficStatus: React.FC<TrafficStatusProps> = ({
  signalNodes,
  timeSavings,
  manualOverrideActive,
  onToggleOverride,
  onRefresh
}) => {
  const [loading, setLoading] = useState(false);

  const handleToggleOverrideClick = async () => {
    try {
      setLoading(true);
      await onToggleOverride(!manualOverrideActive);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Top Preemption & Time Savings Banner */}
      <Grid container spacing={3} mb={3}>
        {/* Time Savings Gauge Card */}
        <Grid item xs={12} md={7}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              height: '100%',
              bgcolor: 'success.50',
              borderColor: 'success.300'
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Box display="flex" alignItems="center" gap={1.5}>
                  <SpeedIcon color="success" sx={{ fontSize: 32 }} />
                  <Typography variant="h6" fontWeight="bold" color="success.900">
                    Green Corridor Route Time Savings
                  </Typography>
                </Box>
                <Chip
                  label={`${timeSavings.percentage_time_saved}% FASTER`}
                  color="success"
                  sx={{ fontWeight: 'bold', fontSize: 14 }}
                />
              </Box>

              <Grid container spacing={2} my={1}>
                <Grid item xs={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'white' }}>
                    <Typography variant="caption" fontWeight="bold" color="text.secondary" display="block">
                      NORMAL ROUTE (WITH LIGHT STOPS)
                    </Typography>
                    <Typography variant="h3" fontWeight="bold" color="error.main" my={0.5}>
                      {timeSavings.normal_route.estimated_minutes} <Typography component="span" variant="h6">mins</Typography>
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Stops: {timeSavings.normal_route.traffic_light_stops} Red Lights | Avg {timeSavings.normal_route.avg_speed_kmh} km/h
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'white', borderColor: 'success.main', borderWidth: 2 }}>
                    <Typography variant="caption" fontWeight="bold" color="success.main" display="block">
                      GREEN CORRIDOR (PREEMPTED)
                    </Typography>
                    <Typography variant="h3" fontWeight="bold" color="success.main" my={0.5}>
                      {timeSavings.green_corridor_route.estimated_minutes} <Typography component="span" variant="h6">mins</Typography>
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Stops: 0 Red Lights | Avg {timeSavings.green_corridor_route.avg_speed_kmh} km/h
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              <Paper variant="outlined" sx={{ p: 1.5, mt: 1, bgcolor: 'white', borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight="bold" color="success.900">
                  ⚡ NET TIME SAVED: {timeSavings.time_saved_minutes} MINUTES ({timeSavings.distance_km} km ambulance corridor)
                </Typography>
              </Paper>
            </CardContent>
          </Card>
        </Grid>

        {/* Manual Override Control Panel */}
        <Grid item xs={12} md={5}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              height: '100%',
              bgcolor: manualOverrideActive ? 'error.50' : 'background.paper',
              borderColor: manualOverrideActive ? 'error.main' : 'divider'
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" gap={1.5} mb={2}>
                <OverrideIcon color={manualOverrideActive ? 'error' : 'primary'} sx={{ fontSize: 32 }} />
                <Typography variant="h6" fontWeight="bold">
                  Coordinator Signal Override
                </Typography>
              </Box>

              <Typography variant="body2" color="text.secondary" mb={2}>
                Force permanent green light signal state across all city intersections along the active ambulance route.
              </Typography>

              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  mb: 2.5,
                  borderRadius: 2,
                  bgcolor: manualOverrideActive ? 'white' : 'grey.50',
                  textAlign: 'center'
                }}
              >
                <Chip
                  label={manualOverrideActive ? '🚨 MANUAL OVERRIDE ENGAGED' : 'AUTOMATIC ATCS PREEMPTION ACTIVE'}
                  color={manualOverrideActive ? 'error' : 'success'}
                  sx={{ fontWeight: 'bold', mb: 1 }}
                />
                <Typography variant="caption" color="text.secondary" display="block">
                  {manualOverrideActive
                    ? 'All signal nodes forced GREEN via high-priority preemption override.'
                    : 'System pre-clears signals 30 seconds ahead of ambulance arrival.'}
                </Typography>
              </Paper>

              <Button
                variant="contained"
                color={manualOverrideActive ? 'error' : 'primary'}
                fullWidth
                size="large"
                onClick={handleToggleOverrideClick}
                disabled={loading}
                startIcon={<OverrideIcon />}
                sx={{ fontWeight: 'bold', py: 1.2, borderRadius: 2 }}
              >
                {manualOverrideActive ? 'Deactivate Manual Override' : 'Engage Manual Green Override'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Traffic Light Node Grid Table */}
      <Card variant="outlined" sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={2}>
            <Box display="flex" alignItems="center" gap={1.5}>
              <SensorsIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                City Traffic Light Node Status ({signalNodes.length} Intersections)
              </Typography>
            </Box>
            <Chip label="CITY ATCS API ONLINE" color="success" size="small" icon={<GreenIcon />} />
          </Box>

          <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell font-weight="bold">SIGNAL NODE ID</TableCell>
                  <TableCell font-weight="bold">INTERSECTION NAME</TableCell>
                  <TableCell font-weight="bold">PREEMPTION STATUS</TableCell>
                  <TableCell font-weight="bold">LIGHT COLOR</TableCell>
                  <TableCell font-weight="bold">TIME TO PREEMPTION</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {signalNodes.map((node) => (
                  <TableRow key={node.signal_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold" fontFamily="monospace">
                        🚦 {node.signal_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">{node.intersection_name}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={node.status}
                        color={node.status === 'PREEMPTED' ? 'success' : 'warning'}
                        size="small"
                        sx={{ fontWeight: 'bold' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={node.light_color}
                        color={node.light_color === 'GREEN' ? 'success' : 'error'}
                        size="small"
                        icon={node.light_color === 'GREEN' ? <GreenIcon /> : <RedIcon />}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {node.time_to_preemption_sec === 0 ? 'ACTIVE NOW' : `${node.time_to_preemption_sec}s countdown`}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TrafficStatus;
