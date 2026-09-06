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
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  LocalHospital as HospitalIcon,
  Bloodtype as BloodIcon,
  LocalShipping as AmbulanceIcon,
  Campaign as BroadcastIcon,
  CheckCircle as CheckIcon,
  Send as SendIcon
} from '@mui/icons-material';

import { apiClient } from '../api/client';

interface ResourceCoordinatorProps {
  hospitalDistribution?: any;
  bloodReservations?: any;
  massCommunications?: any;
  onDispatchResources?: () => void;
}

const ResourceCoordinator: React.FC<ResourceCoordinatorProps> = ({
  hospitalDistribution,
  bloodReservations,
  massCommunications,
  onDispatchResources
}) => {
  const [broadcastOpen, setBroadcastOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const hospitals = hospitalDistribution?.hospital_distribution_plan || [];
  const bloodData = bloodReservations?.units_by_type || { 'O-': 8, 'A+': 12 };

  const handleTriggerDispatch = async () => {
    try {
      setLoading(true);
      await apiClient.post('/mass-casualty/dispatch-resources', {});
      setStatusMsg('✅ Multi-ambulance staging & blood bank reservations executed!');
      if (onDispatchResources) onDispatchResources();
    } catch (err: any) {
      alert('Dispatch error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBroadcast = async () => {
    try {
      setLoading(true);
      await apiClient.post('/mass-casualty/broadcast-notification', { incident_id: 'MCI-INC-1001' });
      setBroadcastOpen(false);
      setStatusMsg('📣 Emergency notifications broadcasted to hospitals, family portal, media & SDMA!');
    } catch (err: any) {
      alert('Broadcast error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Top Banner */}
      <Paper
        elevation={0}
        sx={{
          p: 2.5,
          mb: 3,
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 3,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <AmbulanceIcon color="error" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h6" fontWeight="bold">
              Multi-Resource Coordination Matrix
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Distributes casualties across regional trauma centers to prevent hospital overload.
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1.5}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AmbulanceIcon />}
            onClick={handleTriggerDispatch}
            disabled={loading}
          >
            Execute Resource Dispatch
          </Button>

          <Button
            variant="contained"
            color="error"
            startIcon={<BroadcastIcon />}
            onClick={() => setBroadcastOpen(true)}
          >
            Mass Broadcast Alerts
          </Button>
        </Box>
      </Paper>

      {statusMsg && (
        <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
          {statusMsg}
        </Alert>
      )}

      {/* Grid Content */}
      <Grid container spacing={3}>
        {/* Hospital Distribution Plan */}
        <Grid item xs={12} md={7}>
          <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <HospitalIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Hospital Capacity & Victim Allocation Load Balancer
                </Typography>
              </Box>

              <Box display="flex" flexDirection="column" gap={2}>
                {hospitals.map((h: any, idx: number) => {
                  const redAssigned = h.assigned_victims?.RED || 0;
                  const yellowAssigned = h.assigned_victims?.YELLOW || 0;
                  const greenAssigned = h.assigned_victims?.GREEN || 0;

                  return (
                    <Paper key={idx} variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          🏥 {h.name}
                        </Typography>
                        <Chip label={`${h.distance_km} km`} size="small" />
                      </Box>

                      <Typography variant="body2" color="text.secondary" mb={1}>
                        Trauma Beds: <strong>{h.trauma_beds_available} free</strong> | ICU: <strong>{h.icu_beds_available} free</strong> | Specialties: {h.specialties?.join(', ')}
                      </Typography>

                      <Divider sx={{ my: 1 }} />

                      <Box display="flex" gap={1.5} alignItems="center" flexWrap="wrap">
                        <Typography variant="caption" fontWeight="bold" color="text.secondary">
                          ASSIGNED VICTIMS:
                        </Typography>
                        <Chip label={`${redAssigned} RED (Immediate)`} color="error" size="small" />
                        <Chip label={`${yellowAssigned} YELLOW (Delayed)`} color="warning" size="small" />
                        <Chip label={`${greenAssigned} GREEN (Minor)`} color="success" size="small" />
                      </Box>
                    </Paper>
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Emergency Blood Stock & Ambulance Staging */}
        <Grid item xs={12} md={5}>
          <Card variant="outlined" sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <BloodIcon color="error" />
                <Typography variant="h6" fontWeight="bold">
                  Emergency Blood Bank Reservations
                </Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, textAlign: 'center', bgcolor: 'error.50' }}>
                    <Typography variant="caption" fontWeight="bold" color="error.900">
                      O- NEGATIVE (UNIVERSAL)
                    </Typography>
                    <Typography variant="h3" fontWeight="bold" color="error.main" my={0.5}>
                      {bloodData['O-'] || 8}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">Units Reserved</Typography>
                  </Paper>
                </Grid>

                <Grid item xs={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, textAlign: 'center', bgcolor: 'primary.50' }}>
                    <Typography variant="caption" fontWeight="bold" color="primary.900">
                      A+ POSITIVE (EMERGENCY)
                    </Typography>
                    <Typography variant="h3" fontWeight="bold" color="primary.main" my={0.5}>
                      {bloodData['A+'] || 12}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">Units Reserved</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Card variant="outlined" sx={{ borderRadius: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1.5}>
                <AmbulanceIcon color="success" />
                <Typography variant="h6" fontWeight="bold">Ambulance Staging Status</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                8 Ambulances currently active in multi-casualty staging zone.
              </Typography>
              <LinearProgress variant="determinate" value={75} color="success" sx={{ height: 10, borderRadius: 5, mb: 1 }} />
              <Typography variant="caption" color="text.secondary">
                6 of 8 ambulances in transit to regional trauma centers
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Mass Broadcast Dialog */}
      <Dialog open={broadcastOpen} onClose={() => setBroadcastOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight="bold">Broadcast Mass Emergency Notifications</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Dispatches automated emergency alerts to 4 key communication channels:
          </Typography>

          <Paper variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold">1. Area Hospitals (Surge Warning)</Typography>
            <Typography variant="caption" color="text.secondary">
              Alerts 3 regional hospitals to clear trauma bays and prepare surgical staff.
            </Typography>
          </Paper>

          <Paper variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold">2. Family Reunification Portal</Typography>
            <Typography variant="caption" color="text.secondary">
              Activates hotline 1-800-555-ARIA-HELP and public family info counter.
            </Typography>
          </Paper>

          <Paper variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold">3. Media Communication Template</Typography>
            <Typography variant="caption" color="text.secondary">
              Generates official press release advising public to clear emergency transit routes.
            </Typography>
          </Paper>

          <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold">4. Government Agency Notification</Typography>
            <Typography variant="caption" color="text.secondary">
              Dispatches Level 2 Emergency Alert to State Disaster Management Authority (SDMA).
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setBroadcastOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleBroadcast}
            disabled={loading}
            startIcon={<SendIcon />}
          >
            {loading ? 'Broadcasting...' : 'Broadcast All Notifications'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ResourceCoordinator;
