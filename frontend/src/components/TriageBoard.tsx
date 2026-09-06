import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider
} from '@mui/material';
import {
  AddCircle as TagIcon,
  Person as PersonIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  AssignmentInd as OfficerIcon
} from '@mui/icons-material';

import { apiClient } from '../api/client';

export interface VictimRecord {
  victim_tag_id: string;
  triage_category: 'RED' | 'YELLOW' | 'GREEN' | 'BLACK';
  triage_label: string;
  color: string;
  priority: number;
  injury_description: string;
  age_group: string;
  location: { latitude: number; longitude: number };
  assigned_hospital_id?: string;
  assigned_ambulance_id?: string;
  transport_status: string;
  triage_timestamp: string;
  triage_officer?: string;
}

interface TriageBoardProps {
  categoryCounts: { RED: number; YELLOW: number; GREEN: number; BLACK: number };
  totalVictims: number;
  triageOfficer?: string;
  onVictimTagged: () => void;
}

const TriageBoard: React.FC<TriageBoardProps> = ({
  categoryCounts,
  totalVictims,
  triageOfficer = 'Officer James Vance (Badge #402)',
  onVictimTagged
}) => {
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [category, setCategory] = useState<'RED' | 'YELLOW' | 'GREEN' | 'BLACK'>('RED');
  const [description, setDescription] = useState('');
  const [ageGroup, setAgeGroup] = useState('adult');
  const [loading, setLoading] = useState(false);

  const handleRegisterTriage = async () => {
    try {
      setLoading(true);
      await apiClient.post('/mass-casualty/victims/triage', {
        triage_category: category,
        injury_description: description || 'Trauma injury reported on scene',
        age_group: ageGroup,
        location: { latitude: 37.7749, longitude: -122.4194 }
      });
      setTagDialogOpen(false);
      setDescription('');
      onVictimTagged();
    } catch (err: any) {
      alert('Failed to register victim triage: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Top Officer & Quick Tag Launcher */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
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
        <Box display="flex" alignItems="center" gap={1.5}>
          <OfficerIcon color="primary" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="subtitle1" fontWeight="bold">
              Triage Officer: {triageOfficer}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              START Algorithm (Simple Triage and Rapid Treatment) Active | Total Tagged: {totalVictims}
            </Typography>
          </Box>
        </Box>

        <Button
          variant="contained"
          color="error"
          startIcon={<TagIcon />}
          onClick={() => setTagDialogOpen(true)}
          sx={{ fontWeight: 'bold', borderRadius: 2 }}
        >
          Tag New Victim (START Triage)
        </Button>
      </Paper>

      {/* 4 START Triage Category Cards */}
      <Grid container spacing={3} mb={3}>
        {/* RED: Immediate */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              borderColor: '#ef4444',
              borderWidth: 2,
              bgcolor: 'rgba(239, 68, 68, 0.03)'
            }}
          >
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2" fontWeight="bold" color="#ef4444">
                  IMMEDIATE (RED)
                </Typography>
                <Chip label="PRIORITY 1" color="error" size="small" sx={{ fontWeight: 'bold', fontSize: 10 }} />
              </Box>
              <Typography variant="h2" fontWeight="bold" color="#ef4444">
                {categoryCounts.RED}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                Life-threatening injuries. Immediate transport needed.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* YELLOW: Delayed */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              borderColor: '#f59e0b',
              borderWidth: 2,
              bgcolor: 'rgba(245, 158, 11, 0.03)'
            }}
          >
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2" fontWeight="bold" color="#b45309">
                  DELAYED (YELLOW)
                </Typography>
                <Chip label="PRIORITY 2" color="warning" size="small" sx={{ fontWeight: 'bold', fontSize: 10 }} />
              </Box>
              <Typography variant="h2" fontWeight="bold" color="#b45309">
                {categoryCounts.YELLOW}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                Serious injuries. Care required within 1-2 hours.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* GREEN: Minor */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              borderColor: '#10b981',
              borderWidth: 2,
              bgcolor: 'rgba(16, 185, 129, 0.03)'
            }}
          >
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2" fontWeight="bold" color="#047857">
                  MINOR (GREEN)
                </Typography>
                <Chip label="PRIORITY 3" color="success" size="small" sx={{ fontWeight: 'bold', fontSize: 10 }} />
              </Box>
              <Typography variant="h2" fontWeight="bold" color="#047857">
                {categoryCounts.GREEN}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                Walking wounded. Ambulatory with minor cuts.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* BLACK: Deceased */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              borderColor: '#1e293b',
              borderWidth: 2,
              bgcolor: 'rgba(30, 41, 59, 0.03)'
            }}
          >
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2" fontWeight="bold" color="#1e293b">
                  EXPECTANT (BLACK)
                </Typography>
                <Chip label="PRIORITY 4" color="default" size="small" sx={{ fontWeight: 'bold', fontSize: 10 }} />
              </Box>
              <Typography variant="h2" fontWeight="bold" color="#1e293b">
                {categoryCounts.BLACK}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                Non-survivable trauma or unresponsive.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Victim Tag Dialog */}
      <Dialog open={tagDialogOpen} onClose={() => setTagDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle fontWeight="bold">Register New START Triage Victim Tag</DialogTitle>
        <DialogContent dividers>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel id="triage-cat-label">Triage Category (START)</InputLabel>
            <Select
              labelId="triage-cat-label"
              value={category}
              label="Triage Category (START)"
              onChange={(e: any) => setCategory(e.target.value)}
            >
              <MenuItem value="RED">🔴 RED - Immediate (Critical Airway/Vitals)</MenuItem>
              <MenuItem value="YELLOW">🟡 YELLOW - Delayed (Serious Injury, Non-walking)</MenuItem>
              <MenuItem value="GREEN">🟢 GREEN - Minor (Walking Wounded)</MenuItem>
              <MenuItem value="BLACK">⚫ BLACK - Expectant / Deceased</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Injury Description & Field Vitals"
            fullWidth
            multiline
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Severe arterial leg bleed, BP 90/60, tourniquet applied"
            sx={{ mb: 2 }}
          />

          <FormControl fullWidth size="small">
            <InputLabel id="age-group-label">Age Group</InputLabel>
            <Select
              labelId="age-group-label"
              value={ageGroup}
              label="Age Group"
              onChange={(e) => setAgeGroup(e.target.value)}
            >
              <MenuItem value="adult">Adult</MenuItem>
              <MenuItem value="pediatric">Pediatric (Child under 12)</MenuItem>
              <MenuItem value="elderly">Elderly (&gt;65)</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setTagDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleRegisterTriage} disabled={loading}>
            {loading ? 'Registering...' : 'Assign Barcode Tag'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TriageBoard;
