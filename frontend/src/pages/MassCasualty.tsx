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
  Paper,
  CircularProgress,
  Chip,
  Divider,
  Snackbar
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  FlashOn as ActivateIcon,
  Timeline as TimelineIcon,
  Forum as CommIcon,
  Assignment as TriageIcon,
  LocalShipping as AmbulanceIcon
} from '@mui/icons-material';

import TriageBoard, { VictimRecord } from '../components/TriageBoard';
import VictimTracker from '../components/VictimTracker';
import ResourceCoordinator from '../components/ResourceCoordinator';
import { apiClient } from '../api/client';

interface CommandSummary {
  mci_active: boolean;
  incident_id: string;
  timestamp: string;
  triage_summary: {
    mci_active: boolean;
    total_victims: number;
    category_counts: { RED: number; YELLOW: number; GREEN: number; BLACK: number };
    triage_officer?: string;
  };
  total_victims_tagged: number;
  victims_list: VictimRecord[];
  hospital_distribution: any;
  blood_bank_reservations: any;
  mass_communications: any;
  timeline_log: Array<{ timestamp: string; event: string; severity: string; author: string }>;
  communication_log: Array<{ timestamp: string; recipient: string; type: string; message: string }>;
}

const MassCasualty: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<CommandSummary | null>(null);
  const [snackbarMsg, setSnackbarMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/mass-casualty/command-summary');
      setSummary(res.data.data);
    } catch (err: any) {
      console.error('Error loading Mass Casualty Command Summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActivation = async () => {
    try {
      if (summary?.mci_active) {
        await apiClient.post('/mass-casualty/deactivate', {});
        setSnackbarMsg('Mass Casualty Mode DEACTIVATED');
      } else {
        await apiClient.post('/mass-casualty/activate', {
          incident_id: 'MCI-INC-1001',
          reason: 'Manual activation by Incident Commander'
        });
        setSnackbarMsg('🚨 MASS CASUALTY MODE ACTIVATED!');
      }
      await loadData();
    } catch (err: any) {
      alert('Failed to toggle MCI activation: ' + err.message);
    }
  };

  if (loading && !summary) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="500px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  const isMciActive = summary?.mci_active ?? false;
  const triageCounts = summary?.triage_summary?.category_counts || { RED: 3, YELLOW: 5, GREEN: 8, BLACK: 1 };
  const totalVictims = summary?.total_victims_tagged || 17;

  return (
    <Box sx={{ p: 3, maxWidth: 1400, margin: '0 auto' }}>
      {/* MCI Command Activation Banner */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          bgcolor: isMciActive ? 'error.main' : 'background.paper',
          color: isMciActive ? 'white' : 'text.primary',
          border: '2px solid',
          borderColor: isMciActive ? 'error.main' : 'divider',
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
              width: 54,
              height: 54,
              borderRadius: '50%',
              bgcolor: isMciActive ? 'white' : 'error.main',
              color: isMciActive ? 'error.main' : 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 28
            }}
          >
            ⚠️
          </Box>
          <Box>
            <Box display="flex" alignItems="center" gap={1.5}>
              <Typography variant="h4" fontWeight="bold">
                Mass Casualty Command Center
              </Typography>
              <Chip
                label={isMciActive ? '🔴 MCI ACTIVE (>10 VICTIMS)' : 'STANDBY MODE'}
                color={isMciActive ? 'default' : 'primary'}
                sx={{
                  bgcolor: isMciActive ? 'white' : undefined,
                  color: isMciActive ? 'error.main' : undefined,
                  fontWeight: 'bold'
                }}
              />
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Incident Ref: {summary?.incident_id || 'MCI-INC-1001'} | START Triage Algorithm Active
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1.5}>
          <Button
            variant="outlined"
            onClick={loadData}
            startIcon={<RefreshIcon />}
            sx={{
              borderColor: isMciActive ? 'white' : undefined,
              color: isMciActive ? 'white' : undefined
            }}
          >
            Refresh
          </Button>

          <Button
            variant="contained"
            color={isMciActive ? 'inherit' : 'error'}
            onClick={handleToggleActivation}
            startIcon={<ActivateIcon />}
            sx={{
              bgcolor: isMciActive ? 'white' : undefined,
              color: isMciActive ? 'error.main' : undefined,
              fontWeight: 'bold'
            }}
          >
            {isMciActive ? 'Deactivate Mass Casualty Mode' : 'Activate Mass Casualty Mode'}
          </Button>
        </Box>
      </Paper>

      {/* Tabs Header */}
      <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, val) => setTabValue(val)}>
          <Tab label="START Triage Board" icon={<TriageIcon />} iconPosition="start" />
          <Tab label="Digital Victim Log" icon={<AmbulanceIcon />} iconPosition="start" />
          <Tab label="Resource Coordinator" icon={<ActivateIcon />} iconPosition="start" />
          <Tab label="Timeline & Comm Audit" icon={<TimelineIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Tab 0: START Triage Board */}
      {tabValue === 0 && (
        <TriageBoard
          categoryCounts={triageCounts}
          totalVictims={totalVictims}
          triageOfficer={summary?.triage_summary?.triage_officer}
          onVictimTagged={loadData}
        />
      )}

      {/* Tab 1: Digital Victim Log */}
      {tabValue === 1 && (
        <VictimTracker
          victims={summary?.victims_list || []}
          onRefresh={loadData}
        />
      )}

      {/* Tab 2: Resource Coordinator */}
      {tabValue === 2 && (
        <ResourceCoordinator
          hospitalDistribution={summary?.hospital_distribution}
          bloodReservations={summary?.blood_bank_reservations}
          massCommunications={summary?.mass_communications}
          onDispatchResources={loadData}
        />
      )}

      {/* Tab 3: Timeline & Comm Audit Log */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          {/* Timeline View */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <TimelineIcon color="primary" />
                  <Typography variant="h6" fontWeight="bold">Incident Timeline Log</Typography>
                </Box>

                <Box display="flex" flexDirection="column" gap={1.5}>
                  {summary?.timeline_log?.map((evt, idx) => (
                    <Paper key={idx} variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Typography variant="subtitle2" fontWeight="bold">{evt.event}</Typography>
                        <Chip
                          label={evt.severity}
                          color={evt.severity === 'CRITICAL' ? 'error' : evt.severity === 'WARNING' ? 'warning' : 'default'}
                          size="small"
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Author: {evt.author} | Time: {new Date(evt.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Communication Log */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <CommIcon color="warning" />
                  <Typography variant="h6" fontWeight="bold">Emergency Communication Audit Log</Typography>
                </Box>

                <Box display="flex" flexDirection="column" gap={1.5}>
                  {summary?.communication_log?.map((comm, idx) => (
                    <Paper key={idx} variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Typography variant="subtitle2" fontWeight="bold">To: {comm.recipient}</Typography>
                        <Chip label={comm.type} color="info" size="small" />
                      </Box>
                      <Typography variant="body2" color="text.secondary">{comm.message}</Typography>
                      <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                        Time: {new Date(comm.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

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

export default MassCasualty;
