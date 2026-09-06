import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  LocalHospital as HospitalIcon,
  LocalShipping as AmbulanceIcon,
  CheckCircle as ReadyIcon,
  Assignment as TemplateIcon,
  Refresh as RefreshIcon,
  Add as AddIcon
} from '@mui/icons-material';

import PreparationChecklist, { PrepChecklistData } from '../components/PreparationChecklist';
import { apiClient } from '../api/client';

const HospitalPrep: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [incidentId, setIncidentId] = useState('INC-1001');
  const [prepData, setPrepData] = useState<PrepChecklistData | null>(null);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('TRAUMA');

  useEffect(() => {
    loadData();
  }, [incidentId]);

  const loadData = async () => {
    try {
      setLoading(true);
      // 1. Fetch checklist for active incident
      const res = await apiClient.get(`/hospital-prep/checklist/${incidentId}`);
      setPrepData(res.data.data);

      // 2. Fetch templates
      const tplRes = await apiClient.get('/hospital-prep/templates');
      setTemplates(tplRes.data.data.templates || []);
    } catch (err: any) {
      console.error('Error loading hospital prep data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchTemplate = async (cat: string) => {
    try {
      setSelectedCategory(cat);
      setLoading(true);
      const res = await apiClient.post('/hospital-prep/generate', {
        incident_id: incidentId,
        emergency_category: cat,
        hospital_id: 'HOSP-01',
        hospital_name: 'General Trauma Center',
        patient_name: 'Michael Miller',
        eta_minutes: 6
      });
      setPrepData(res.data.data);
    } catch (err: any) {
      alert('Error switching emergency template: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !prepData) {
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
          <HospitalIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h5" fontWeight="bold" color="primary.900">
              Hospital Pre-Arrival Preparation Portal
            </Typography>
            <Typography variant="body2" color="text.secondary">
              General Trauma & Medical Center — ER Department Emergency Readiness Dashboard
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1.5}>
          <Button
            variant="outlined"
            onClick={loadData}
            startIcon={<RefreshIcon />}
          >
            Refresh Readiness
          </Button>
        </Box>
      </Paper>

      {/* Main Grid Content */}
      <Grid container spacing={3}>
        {/* Left Column: Template Selector & Incoming Patients List */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TemplateIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Emergency Category Templates (7)
                </Typography>
              </Box>

              <Typography variant="body2" color="text.secondary" mb={2}>
                Switch SOP readiness protocol based on incoming emergency triage assessment:
              </Typography>

              <Box display="flex" flexDirection="column" gap={1}>
                {['TRAUMA', 'CARDIAC', 'STROKE', 'BURN', 'OBSTETRIC', 'PEDIATRIC', 'MASS_CASUALTY'].map((cat) => (
                  <Button
                    key={cat}
                    variant={prepData?.emergency_category === cat ? 'contained' : 'outlined'}
                    color={cat === 'MASS_CASUALTY' ? 'error' : 'primary'}
                    fullWidth
                    onClick={() => handleSwitchTemplate(cat)}
                    sx={{ justifyContent: 'flex-start', py: 1, fontWeight: 'bold' }}
                  >
                    {cat === 'TRAUMA' && '🩸 '}
                    {cat === 'CARDIAC' && '❤️ '}
                    {cat === 'STROKE' && '🧠 '}
                    {cat === 'BURN' && '🔥 '}
                    {cat === 'OBSTETRIC' && '👶 '}
                    {cat === 'PEDIATRIC' && '🧸 '}
                    {cat === 'MASS_CASUALTY' && '🚨 '}
                    {cat.replace('_', ' ')} Checklist
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>

          {/* Incoming Ambulance Card */}
          <Card variant="outlined" sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <AmbulanceIcon color="warning" />
                <Typography variant="h6" fontWeight="bold">
                  Incoming Ambulance AMB-402
                </Typography>
              </Box>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'warning.50', borderColor: 'warning.300' }}>
                <Typography variant="subtitle2" fontWeight="bold" color="warning.900">
                  PATIENT: Michael Miller (Age 42)
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Triage: Severe Motor Vehicle Incident Trauma
                </Typography>
                <Chip label="ETA: 6 MINS (GREEN CORRIDOR ACTIVE)" color="success" size="small" sx={{ mt: 1, fontWeight: 'bold' }} />
              </Paper>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column: Active Preparation Checklist */}
        <Grid item xs={12} md={8}>
          {prepData && (
            <PreparationChecklist
              prepData={prepData}
              onItemToggled={loadData}
            />
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default HospitalPrep;
