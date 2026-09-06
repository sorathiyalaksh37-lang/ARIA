import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Checkbox,
  FormControlLabel,
  Paper,
  Button,
  Grid,
  Alert,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  MedicalServices as EquipmentIcon,
  People as StaffIcon,
  MeetingRoom as RoomIcon,
  Bloodtype as BloodIcon,
  Timer as TimerIcon
} from '@mui/icons-material';

import { apiClient } from '../api/client';

export interface ChecklistItem {
  item_id: string;
  category: 'EQUIPMENT' | 'STAFF' | 'ROOM_OR' | 'BLOOD_PRODUCTS';
  description: string;
  is_critical: boolean;
  completed: boolean;
  completed_by_staff_id?: string;
  completed_at?: string;
}

export interface PrepChecklistData {
  incident_id: string;
  patient_name: string;
  emergency_category: string;
  template_name: string;
  target_prep_time_minutes: number;
  eta_minutes: number;
  total_items: number;
  completed_items: number;
  progress_percentage: number;
  prep_status: string;
  critical_warning_alert: boolean;
  missed_critical_count: number;
  items: ChecklistItem[];
}

interface PreparationChecklistProps {
  prepData: PrepChecklistData;
  onItemToggled: () => void;
}

const PreparationChecklist: React.FC<PreparationChecklistProps> = ({
  prepData,
  onItemToggled
}) => {
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [loadingItemId, setLoadingItemId] = useState<string | null>(null);

  const filteredItems = prepData.items.filter((item) => {
    if (categoryFilter === 'ALL') return true;
    return item.category === categoryFilter;
  });

  const handleToggle = async (item: ChecklistItem) => {
    try {
      setLoadingItemId(item.item_id);
      await apiClient.post('/hospital-prep/check-item', {
        incident_id: prepData.incident_id,
        item_id: item.item_id,
        completed: !item.completed,
        staff_id: 'STF-902'
      });
      onItemToggled();
    } catch (err: any) {
      alert('Error toggling checklist item: ' + err.message);
    } finally {
      setLoadingItemId(null);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'EQUIPMENT': return <EquipmentIcon fontSize="small" />;
      case 'STAFF': return <StaffIcon fontSize="small" />;
      case 'ROOM_OR': return <RoomIcon fontSize="small" />;
      case 'BLOOD_PRODUCTS': return <BloodIcon fontSize="small" />;
      default: return <CheckIcon fontSize="small" />;
    }
  };

  return (
    <Card variant="outlined" sx={{ borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header Summary */}
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={2}>
          <Box>
            <Typography variant="h6" fontWeight="bold">
              {prepData.template_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Patient: {prepData.patient_name} | Incident: {prepData.incident_id}
            </Typography>
          </Box>

          <Box display="flex" alignItems="center" gap={1.5}>
            <Chip
              label={`ETA: ${prepData.eta_minutes} MINS`}
              color="warning"
              icon={<TimerIcon />}
              sx={{ fontWeight: 'bold' }}
            />
            <Chip
              label={prepData.prep_status === 'READY' ? 'READY FOR PATIENT' : 'IN PREPARATION'}
              color={prepData.prep_status === 'READY' ? 'success' : 'primary'}
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
        </Box>

        {/* Missed Critical Alert */}
        {prepData.critical_warning_alert && (
          <Alert severity="error" icon={<WarningIcon />} sx={{ mb: 2.5, borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold">
              🚨 CRITICAL READINESS ALERT: {prepData.missed_critical_count} CRITICAL ITEMS UNCOMPLETED!
            </Typography>
            <Typography variant="body2">
              Patient arrival in under 5 minutes. Immediately check off critical airway, blood, and room preparation steps.
            </Typography>
          </Alert>
        )}

        {/* Progress Bar */}
        <Paper variant="outlined" sx={{ p: 2, mb: 3, borderRadius: 2, bgcolor: 'grey.50' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="subtitle2" fontWeight="bold">
              Pre-Arrival Readiness: {prepData.completed_items} of {prepData.total_items} Items Completed
            </Typography>
            <Typography variant="subtitle2" fontWeight="bold" color="primary.main">
              {prepData.progress_percentage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={prepData.progress_percentage}
            color={prepData.progress_percentage === 100 ? 'success' : 'primary'}
            sx={{ height: 10, borderRadius: 5 }}
          />
        </Paper>

        {/* Category Filters */}
        <Box display="flex" gap={1} mb={2.5} flexWrap="wrap">
          {['ALL', 'EQUIPMENT', 'STAFF', 'ROOM_OR', 'BLOOD_PRODUCTS'].map((cat) => (
            <Chip
              key={cat}
              label={cat.replace('_', ' ')}
              color={categoryFilter === cat ? 'primary' : 'default'}
              variant={categoryFilter === cat ? 'filled' : 'outlined'}
              onClick={() => setCategoryFilter(cat)}
              clickable
              sx={{ fontWeight: 'bold' }}
            />
          ))}
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Items List */}
        <Box display="flex" flexDirection="column" gap={1.5}>
          {filteredItems.map((item) => (
            <Paper
              key={item.item_id}
              variant="outlined"
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: item.completed ? 'success.50' : 'background.paper',
                borderColor: item.completed ? 'success.300' : item.is_critical ? 'error.300' : 'divider',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.2s ease'
              }}
            >
              <Box display="flex" alignItems="center" gap={1.5} flexGrow={1}>
                <Checkbox
                  checked={item.completed}
                  onChange={() => handleToggle(item)}
                  disabled={loadingItemId === item.item_id}
                  color="success"
                />

                <Box>
                  <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                    {getCategoryIcon(item.category)}
                    <Typography
                      variant="body1"
                      fontWeight={item.completed ? 'bold' : 'normal'}
                      sx={{ textDecoration: item.completed ? 'line-through' : 'none' }}
                    >
                      {item.description}
                    </Typography>

                    {item.is_critical && (
                      <Chip label="CRITICAL" color="error" size="small" sx={{ fontWeight: 'bold', height: 20 }} />
                    )}
                  </Box>

                  {item.completed && item.completed_by_staff_id && (
                    <Typography variant="caption" color="text.secondary">
                      Checked by Staff ID: <strong>{item.completed_by_staff_id}</strong> at{' '}
                      {new Date(item.completed_at || '').toLocaleTimeString()}
                    </Typography>
                  )}
                </Box>
              </Box>

              <Chip
                label={item.category.replace('_', ' ')}
                size="small"
                variant="outlined"
                sx={{ ml: 1, textTransform: 'capitalize' }}
              />
            </Paper>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default PreparationChecklist;
