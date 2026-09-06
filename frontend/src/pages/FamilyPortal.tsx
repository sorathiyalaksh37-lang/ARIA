import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Paper,
  CircularProgress,
  Button,
  Chip,
  Divider,
  Snackbar,
  Alert
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Refresh as RefreshIcon,
  PersonAdd as AddIcon
} from '@mui/icons-material';

import FamilyDashboard, { TrackingDetail } from '../components/FamilyDashboard';
import FamilyContactForm from '../components/FamilyContactForm';
import { apiClient } from '../api/client';

const FamilyPortal: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [incidentId, setIncidentId] = useState('INC-1001');
  const [tracking, setTracking] = useState<TrackingDetail | null>(null);
  const [contacts, setContacts] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [snackbarMsg, setSnackbarMsg] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadPortalData();
  }, []);

  const loadPortalData = async () => {
    try {
      setLoading(true);
      // 1. Load tracking data
      const trackRes = await apiClient.get('/family/tracking/TRACK-INC-1001-TOKEN');
      setTracking(trackRes.data.data);

      // 2. Load contacts
      const contactRes = await apiClient.get(`/family/contacts/${incidentId}`);
      setContacts(contactRes.data.data.contacts || []);

      // 3. Load notification history
      const histRes = await apiClient.get(`/family/history/${incidentId}`);
      setHistory(histRes.data.data.history || []);
    } catch (err: any) {
      console.error('Error loading Family Portal data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !tracking) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="500px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, margin: '0 auto' }}>
      {/* Header Tabs */}
      <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" px={2} pt={1}>
          <Tabs value={tabValue} onChange={(_, val) => setTabValue(val)}>
            <Tab label="Patient Live Dashboard" icon={<DashboardIcon />} iconPosition="start" />
            <Tab label="Family Contacts Management" icon={<PeopleIcon />} iconPosition="start" />
            <Tab label="Privacy & Consent Settings" icon={<SecurityIcon />} iconPosition="start" />
          </Tabs>

          <Button
            variant="outlined"
            size="small"
            onClick={loadPortalData}
            startIcon={<RefreshIcon />}
          >
            Refresh Portal
          </Button>
        </Box>
      </Paper>

      {/* Tab 0: Live Dashboard */}
      {tabValue === 0 && tracking && (
        <FamilyDashboard
          tracking={tracking}
          notificationHistory={history}
          onRefresh={loadPortalData}
        />
      )}

      {/* Tab 1: Family Contacts Management */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={5}>
            <FamilyContactForm
              incidentId={incidentId}
              onContactSaved={() => {
                loadPortalData();
                setShowForm(false);
              }}
            />
          </Grid>

          <Grid item xs={12} md={7}>
            <Card variant="outlined" sx={{ borderRadius: 3, height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  Registered Emergency Contacts ({contacts.length})
                </Typography>

                <Box display="flex" flexDirection="column" gap={2}>
                  {contacts.map((c: any) => (
                    <Paper key={c.contact_id} variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1" fontWeight="bold">{c.name}</Typography>
                          {c.is_primary && (
                            <Chip label="PRIMARY CONTACT" color="primary" size="small" sx={{ fontWeight: 'bold' }} />
                          )}
                        </Box>
                        <Chip label={c.relationship} variant="outlined" size="small" />
                      </Box>

                      <Typography variant="body2" color="text.secondary">
                        📞 {c.phone} | ✉️ {c.email}
                      </Typography>

                      <Box display="flex" gap={1} mt={1.5} flexWrap="wrap">
                        <Chip label={`Channel: ${c.preferred_channel}`} color="info" size="small" />
                        <Chip label={`Lang: ${c.language.toUpperCase()}`} size="small" />
                        <Chip label={`Privacy: ${c.privacy_level}`} color="secondary" size="small" />
                      </Box>
                    </Paper>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Privacy & Consent Settings */}
      {tabValue === 2 && (
        <Card variant="outlined" sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Patient Privacy & Information Sharing Controls
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Manage what level of medical detail is shared with family emergency contacts.
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 3, borderRadius: 3, bgcolor: 'primary.50', borderColor: 'primary.200' }}>
                  <Typography variant="subtitle1" fontWeight="bold" color="primary.900" gutterBottom>
                    🩺 FULL MEDICAL DETAILS (Opt-In Consent)
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    Shares complete vitals, triage status, attending doctor notes, ER department room numbers, and visitation hours.
                  </Typography>
                  <Chip label="ACTIVE FOR PRIMARY CONTACT" color="success" sx={{ fontWeight: 'bold' }} />
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 3, borderRadius: 3, bgcolor: 'grey.50' }}>
                  <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                    🚨 EMERGENCY ONLY (Restricted Tier)
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    Restricts notifications to basic ambulance dispatch status and destination hospital name. No medical vitals or doctor notes shared.
                  </Typography>
                  <Chip label="AVAILABLE FOR SECONDARY CONTACTS" color="default" sx={{ fontWeight: 'bold' }} />
                </Paper>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
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

export default FamilyPortal;
