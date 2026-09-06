import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Divider,
  Alert,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  LocalHospital as HospitalIcon,
  LocalShipping as AmbulanceIcon,
  Timer as TimerIcon,
  CheckCircle as CheckIcon,
  MedicalServices as DoctorIcon,
  History as HistoryIcon,
  NotificationsActive as NotifyIcon,
  Share as ShareIcon
} from '@mui/icons-material';

import { apiClient } from '../api/client';

export interface TrackingDetail {
  incident_id: string;
  patient_name: string;
  token: string;
  current_status: string;
  status_label: string;
  ambulance_id: string;
  destination_hospital: {
    hospital_id: string;
    name: string;
    address: string;
    er_hotline: string;
    room_number?: string;
    visiting_hours?: string;
  };
  eta_minutes: number;
  green_corridor_active: boolean;
  time_saved_minutes?: number;
  medical_summary: {
    vitals: string;
    triage_category?: string;
    attending_doctor: string;
    doctor_notes: string;
    last_updated?: string;
  };
}

interface FamilyDashboardProps {
  tracking: TrackingDetail;
  notificationHistory: any[];
  onRefresh?: () => void;
}

const MILESTONE_STEPS = [
  'Response Dispatched',
  'Ambulance on Scene',
  'En Route to Hospital',
  'Reached ER Department',
  'Medical Assessment',
  'Visitation Permitted'
];

const FamilyDashboard: React.FC<FamilyDashboardProps> = ({
  tracking,
  notificationHistory,
  onRefresh
}) => {
  const [notifyDialogOpen, setNotifyDialogOpen] = useState(false);
  const [selectedMilestone, setSelectedMilestone] = useState('PATIENT_EN_ROUTE');
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  // Calculate active step index from status
  const getActiveStep = (status: string) => {
    switch (status) {
      case 'RESPONSE_DISPATCHED':
      case 'INCIDENT_CREATED':
        return 0;
      case 'AMBULANCE_ARRIVED':
        return 1;
      case 'EN_ROUTE_TO_HOSPITAL':
      case 'PATIENT_EN_ROUTE':
        return 2;
      case 'HOSPITAL_ARRIVED':
      case 'REACHED_ER':
        return 3;
      case 'STATUS_CHANGED':
      case 'STABLE':
        return 4;
      case 'VISITATION_READY':
        return 5;
      default:
        return 2;
    }
  };

  const activeStep = getActiveStep(tracking.current_status);

  const handleSendMilestone = async () => {
    try {
      setLoading(true);
      await apiClient.post('/family/notify-event', {
        incident_id: tracking.incident_id,
        event_type: selectedMilestone,
        hospital_name: tracking.destination_hospital.name,
        eta_minutes: tracking.eta_minutes,
        patient_status: tracking.current_status,
        doctor_notes: tracking.medical_summary.doctor_notes
      });
      setNotifyDialogOpen(false);
      setStatusMsg(`📢 Milestone alert '${selectedMilestone}' dispatched to family contacts!`);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert('Error dispatching milestone: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const shareableUrl = `https://aria-emergency.com/family-portal?token=${tracking.token}`;

  return (
    <Box>
      {/* Top Banner */}
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
          <Box
            sx={{
              width: 50,
              height: 50,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 26
            }}
          >
            🛡️
          </Box>
          <Box>
            <Typography variant="h5" fontWeight="bold" color="primary.900">
              Patient Live Status: {tracking.patient_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ref ID: {tracking.incident_id} | Live Family Portal Tracking Link Active
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1.5}>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<ShareIcon />}
            onClick={() => {
              navigator.clipboard.writeText(shareableUrl);
              alert('Tracking link copied to clipboard: ' + shareableUrl);
            }}
          >
            Copy Shareable Tracking Link
          </Button>

          <Button
            variant="contained"
            color="primary"
            startIcon={<NotifyIcon />}
            onClick={() => setNotifyDialogOpen(true)}
          >
            Dispatch Family Milestone Alert
          </Button>
        </Box>
      </Paper>

      {statusMsg && (
        <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
          {statusMsg}
        </Alert>
      )}

      {/* Stepper Timeline */}
      <Paper variant="outlined" sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" fontWeight="bold" mb={3}>
          Real-Time Emergency Progress Timeline
        </Typography>
        <Stepper activeStep={activeStep} alternativeLabel>
          {MILESTONE_STEPS.map((label, index) => (
            <Step key={label} completed={index <= activeStep}>
              <StepLabel>
                <Typography variant="body2" fontWeight={index === activeStep ? 'bold' : 'normal'}>
                  {label}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Grid Status Cards */}
      <Grid container spacing={3} mb={3}>
        {/* ETA & Ambulance Tracking */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 3, height: '100%', bgcolor: 'warning.50', borderColor: 'warning.300' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TimerIcon color="warning" sx={{ fontSize: 32 }} />
                <Typography variant="h6" fontWeight="bold" color="warning.900">
                  Estimated Hospital Arrival
                </Typography>
              </Box>

              <Typography variant="h2" fontWeight="bold" color="warning.main" my={1}>
                {tracking.eta_minutes} <Typography component="span" variant="h5">MINS</Typography>
              </Typography>

              <Divider sx={{ my: 1.5 }} />

              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <AmbulanceIcon color="primary" />
                <Typography variant="body2" fontWeight="bold">
                  Ambulance: {tracking.ambulance_id}
                </Typography>
              </Box>

              {tracking.green_corridor_active && (
                <Chip
                  label={`🟢 GREEN CORRIDOR ACTIVE (${tracking.time_saved_minutes || 6} MINS SAVED)`}
                  color="success"
                  size="small"
                  sx={{ fontWeight: 'bold', width: '100%', mt: 0.5 }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Hospital Destination Info */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <HospitalIcon color="error" sx={{ fontSize: 32 }} />
                <Typography variant="h6" fontWeight="bold">
                  Destination Hospital
                </Typography>
              </Box>

              <Typography variant="subtitle1" fontWeight="bold">
                {tracking.destination_hospital.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={1}>
                {tracking.destination_hospital.address}
              </Typography>

              <Paper variant="outlined" sx={{ p: 1.5, mb: 1, bgcolor: 'grey.50', borderRadius: 2 }}>
                <Typography variant="caption" fontWeight="bold" display="block" color="text.secondary">
                  ER EMERGENCY HOTLINE
                </Typography>
                <Typography variant="body1" fontWeight="bold" color="error.main">
                  📞 {tracking.destination_hospital.er_hotline}
                </Typography>
              </Paper>

              {tracking.destination_hospital.room_number && (
                <Chip
                  label={`Room / Ward: ${tracking.destination_hospital.room_number}`}
                  color="primary"
                  size="small"
                  sx={{ fontWeight: 'bold' }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Medical & Doctor Update (Consent Controlled) */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <DoctorIcon color="primary" sx={{ fontSize: 32 }} />
                <Typography variant="h6" fontWeight="bold">
                  Attending Physician Notes
                </Typography>
              </Box>

              <Typography variant="subtitle2" fontWeight="bold">
                👨‍⚕️ {tracking.medical_summary.attending_doctor}
              </Typography>

              <Paper variant="outlined" sx={{ p: 2, my: 1.5, bgcolor: 'success.50', borderColor: 'success.200', borderRadius: 2 }}>
                <Typography variant="caption" fontWeight="bold" color="success.900" display="block" mb={0.5}>
                  LATEST MEDICAL ASSESSMENT:
                </Typography>
                <Typography variant="body2" color="text.primary">
                  "{tracking.medical_summary.doctor_notes}"
                </Typography>
              </Paper>

              <Typography variant="caption" color="text.secondary">
                Vitals: {tracking.medical_summary.vitals}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Notification Communication History Log */}
      <Card variant="outlined" sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <HistoryIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Family Communication Audit Log ({notificationHistory.length})
            </Typography>
          </Box>

          <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell font-weight="bold">EVENT TYPE</TableCell>
                  <TableCell font-weight="bold">RECIPIENT</TableCell>
                  <TableCell font-weight="bold">CHANNEL</TableCell>
                  <TableCell font-weight="bold">MESSAGE SUMMARY</TableCell>
                  <TableCell font-weight="bold">DISPATCH TIME</TableCell>
                  <TableCell font-weight="bold">STATUS</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {notificationHistory.length > 0 ? (
                  notificationHistory.map((nh, idx) => (
                    <TableRow key={idx} hover>
                      <TableCell>
                        <Chip label={nh.event_type} size="small" color="primary" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">{nh.recipient_name}</Typography>
                        <Typography variant="caption" color="text.secondary">{nh.recipient_contact}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={nh.channel}
                          size="small"
                          color={nh.channel === 'WHATSAPP' ? 'success' : nh.channel === 'SMS' ? 'info' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{nh.summary}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(nh.timestamp).toLocaleTimeString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label="DELIVERED" color="success" size="small" icon={<CheckIcon />} />
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                      <Typography color="text.secondary">No notification log entries found.</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Paper>
        </CardContent>
      </Card>

      {/* Trigger Milestone Notification Dialog */}
      <Dialog open={notifyDialogOpen} onClose={() => setNotifyDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle fontWeight="bold">Dispatch Milestone Notification</DialogTitle>
        <DialogContent dividers>
          <FormControl fullWidth size="small" sx={{ my: 1 }}>
            <InputLabel id="milestone-select-label">Select Milestone Event</InputLabel>
            <Select
              labelId="milestone-select-label"
              value={selectedMilestone}
              label="Select Milestone Event"
              onChange={(e) => setSelectedMilestone(e.target.value)}
            >
              <MenuItem value="INCIDENT_CREATED">🚨 INCIDENT_CREATED (Immediate Alert)</MenuItem>
              <MenuItem value="AMBULANCE_ARRIVED">🚑 AMBULANCE_ARRIVED (Paramedics On Scene)</MenuItem>
              <MenuItem value="PATIENT_EN_ROUTE">🚨 PATIENT_EN_ROUTE (En Route with Live ETA)</MenuItem>
              <MenuItem value="HOSPITAL_ARRIVED">🏥 HOSPITAL_ARRIVED (Reached Emergency Room)</MenuItem>
              <MenuItem value="STATUS_CHANGED">📋 STATUS_CHANGED (Medical Status Update)</MenuItem>
              <MenuItem value="VISITATION_READY">💚 VISITATION_READY (Family Permitted to Visit)</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setNotifyDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMilestone}
            disabled={loading}
          >
            {loading ? 'Dispatching...' : 'Dispatch Multi-Channel Alert'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FamilyDashboard;
