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
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  RadioGroup,
  FormControlLabel,
  Radio,
  Snackbar
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Navigation as NavIcon,
  FlashOn as AEDIcon,
  People as CivilianIcon,
  LocalPharmacy as PharmacyIcon,
  LocalHospital as ClinicIcon,
  CheckCircle as ConfirmIcon,
  Warning as EscalateIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import FirstAidInstructions from '../components/FirstAidInstructions';
import { ProtocolDetail } from '../components/ProtocolSteps';
import { apiClient } from '../api/client';

const BystanderGuide: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [protocols, setProtocols] = useState<ProtocolDetail[]>([]);
  const [nearbyResources, setNearbyResources] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string>('BS-INC-1001-0000');
  const [arrivalConfirmed, setArrivalConfirmed] = useState(false);
  const [victimStatus, setVictimStatus] = useState('UNASSESSED');
  const [snackbarMsg, setSnackbarMsg] = useState<string | null>(null);

  // Status update dialog
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('STABLE');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // 1. Fetch protocols
      const protoRes = await apiClient.get('/bystander/protocols?lang=en');
      setProtocols(protoRes.data.data.protocols || []);

      // 2. Fetch nearby bystander resources (AEDs, CPR civilians, clinics)
      const resRes = await apiClient.get('/bystander/nearby-resources?latitude=37.7749&longitude=-122.4194');
      setNearbyResources(resRes.data.data);
    } catch (err: any) {
      console.error('Error loading bystander guide data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmArrival = async () => {
    try {
      await apiClient.post('/bystander/confirm-arrival', { session_id: sessionId });
      setArrivalConfirmed(true);
      setSnackbarMsg('✅ Bystander arrival confirmed on scene! Dispatch notified.');
    } catch (err: any) {
      alert('Failed to confirm arrival: ' + err.message);
    }
  };

  const handleUpdateStatus = async () => {
    try {
      const res = await apiClient.post('/bystander/update-status', {
        session_id: sessionId,
        victim_status: selectedStatus
      });
      setVictimStatus(selectedStatus);
      setStatusDialogOpen(false);

      if (res.data?.data?.auto_escalated_to_ems) {
        setSnackbarMsg('🚨 CRITICAL: Case auto-escalated to EMS dispatch due to unresponsive status!');
      } else {
        setSnackbarMsg(`Victim status updated to '${selectedStatus}'`);
      }
    } catch (err: any) {
      alert('Failed to update status: ' + err.message);
    }
  };

  const handleEscalateToEMS = async () => {
    try {
      await apiClient.post('/bystander/escalate', {
        session_id: sessionId,
        reason: 'Bystander requested high-priority EMS dispatch escalation'
      });
      setSnackbarMsg('🚨 Priority EMS Dispatch Alert Dispatched!');
    } catch (err: any) {
      alert('Failed to escalate: ' + err.message);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="500px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, margin: '0 auto' }}>
      {/* Header Banner */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          bgcolor: 'error.50',
          border: '1px solid',
          borderColor: 'error.200',
          borderRadius: 3,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <Box
            sx={{
              width: 50,
              height: 50,
              borderRadius: '50%',
              bgcolor: 'error.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 26
            }}
          >
            🆘
          </Box>
          <Box>
            <Typography variant="h5" fontWeight="bold" color="error.900">
              Bystander Emergency First Aid Guide
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time guided first aid instructions, nearby AED finder, and EMS escalation portal
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1.5} flexWrap="wrap">
          <Button
            variant={arrivalConfirmed ? 'outlined' : 'contained'}
            color="success"
            startIcon={<ConfirmIcon />}
            onClick={handleConfirmArrival}
            disabled={arrivalConfirmed}
          >
            {arrivalConfirmed ? 'Arrival Confirmed' : 'Confirm I Have Arrived at Scene'}
          </Button>

          <Button
            variant="outlined"
            color="primary"
            onClick={() => setStatusDialogOpen(true)}
          >
            Update Victim Status ({victimStatus})
          </Button>

          <Button
            variant="contained"
            color="error"
            startIcon={<EscalateIcon />}
            onClick={handleEscalateToEMS}
          >
            Escalate to EMS
          </Button>
        </Box>
      </Paper>

      {/* Incident & Nearby Resources Panel */}
      <Grid container spacing={3} mb={3}>
        {/* CPR Civilians & AED Defibrillators */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <AEDIcon color="error" />
                <Typography variant="h6" fontWeight="bold">
                  Nearby AED Defibrillators & CPR Responders
                </Typography>
              </Box>

              {/* AED Units */}
              <Typography variant="subtitle2" fontWeight="bold" color="text.secondary" mb={1}>
                AUTOMATED EXTERNAL DEFIBRILLATORS (AED)
              </Typography>
              {nearbyResources?.aed_locations?.map((aed: any, idx: number) => (
                <Paper key={idx} variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle2" fontWeight="bold">{aed.building_name}</Typography>
                    <Chip label={`Access Code: ${aed.access_code}`} color="warning" size="small" />
                  </Box>
                  <Typography variant="body2" color="text.secondary" mt={0.5}>
                    {aed.address} ({aed.distance_km} km away | ~{aed.walking_eta_minutes} min walk)
                  </Typography>
                  <Button
                    variant="text"
                    size="small"
                    startIcon={<NavIcon />}
                    href={aed.navigation_url}
                    target="_blank"
                    sx={{ mt: 0.5 }}
                  >
                    Google Maps Turn-by-Turn Walk Guide
                  </Button>
                </Paper>
              ))}

              <Divider sx={{ my: 2 }} />

              {/* CPR Civilians */}
              <Typography variant="subtitle2" fontWeight="bold" color="text.secondary" mb={1}>
                NEARBY CPR CERTIFIED CIVILIANS
              </Typography>
              {nearbyResources?.cpr_civilians?.map((civ: any, idx: number) => (
                <Paper key={idx} variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle2" fontWeight="bold">{civ.name}</Typography>
                    <Chip label={civ.status} color="success" size="small" />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {civ.certification} (ETA: {civ.eta_minutes} mins | Phone: {civ.phone})
                  </Typography>
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Nearby Pharmacies & Clinics */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <PharmacyIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Nearby Pharmacies & Emergency Clinics
                </Typography>
              </Box>

              <Typography variant="subtitle2" fontWeight="bold" color="text.secondary" mb={1}>
                EMERGENCY PHARMACIES (FOR TOURNIQUETS & DRESSINGS)
              </Typography>
              {nearbyResources?.pharmacies?.map((ph: any, idx: number) => (
                <Paper key={idx} variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle2" fontWeight="bold">{ph.name}</Typography>
                    <Chip label="24/7 OPEN" color="primary" size="small" />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {ph.address} | Stock: {ph.stock_status}
                  </Typography>
                </Paper>
              ))}

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" fontWeight="bold" color="text.secondary" mb={1}>
                URGENT CARE & EMERGENCY CLINICS
              </Typography>
              {nearbyResources?.emergency_clinics?.map((cl: any, idx: number) => (
                <Paper key={idx} variant="outlined" sx={{ p: 1.5, mb: 1, borderRadius: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle2" fontWeight="bold">{cl.name}</Typography>
                    <Chip label="TRAUMA READY" color="success" size="small" />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {cl.address} (Emergency: {cl.emergency_phone})
                  </Typography>
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main First Aid Protocol Component */}
      <FirstAidInstructions protocols={protocols} />

      {/* Status Update Dialog */}
      <Dialog open={statusDialogOpen} onClose={() => setStatusDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle fontWeight="bold">Update Victim Condition</DialogTitle>
        <DialogContent dividers>
          <RadioGroup value={selectedStatus} onChange={(e) => setSelectedStatus(e.target.value)}>
            <FormControlLabel value="STABLE" control={<Radio color="success" />} label="STABLE (Breathing normally, conscious)" />
            <FormControlLabel value="REVIVED" control={<Radio color="primary" />} label="REVIVED (Responded to CPR / First Aid)" />
            <FormControlLabel value="UNRESPONSIVE" control={<Radio color="error" />} label="UNRESPONSIVE (Not breathing / No pulse -> AUTO EMS ESCALATION)" />
            <FormControlLabel value="DETERIORATING" control={<Radio color="warning" />} label="DETERIORATING (Condition worsening)" />
          </RadioGroup>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setStatusDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="primary" onClick={handleUpdateStatus}>
            Save Victim Status
          </Button>
        </DialogActions>
      </Dialog>

      {/* Toast Notification */}
      <Snackbar
        open={Boolean(snackbarMsg)}
        autoHideDuration={4000}
        onClose={() => setSnackbarMsg(null)}
        message={snackbarMsg}
      />
    </Box>
  );
};

export default BystanderGuide;
