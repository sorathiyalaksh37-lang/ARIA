import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Button,
  TextField,
  InputAdornment,
  Paper
} from '@mui/material';
import {
  Search as SearchIcon,
  LocalShipping as AmbulanceIcon,
  LocalHospital as HospitalIcon,
  CheckCircle as DeliveredIcon,
  AccessTime as WaitingIcon
} from '@mui/icons-material';

import { VictimRecord } from './TriageBoard';

interface VictimTrackerProps {
  victims: VictimRecord[];
  onRefresh?: () => void;
}

const VictimTracker: React.FC<VictimTrackerProps> = ({ victims, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');

  const filteredVictims = victims.filter(v => {
    const matchesSearch =
      v.victim_tag_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.injury_description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = selectedFilter === 'ALL' || v.triage_category === selectedFilter;
    return matchesSearch && matchesCat;
  });

  const getStatusChip = (status: string) => {
    switch (status) {
      case 'DELIVERED':
        return <Chip label="DELIVERED TO HOSPITAL" color="success" size="small" icon={<DeliveredIcon />} />;
      case 'IN_TRANSIT':
        return <Chip label="IN TRANSIT (AMBULANCE)" color="primary" size="small" icon={<AmbulanceIcon />} />;
      default:
        return <Chip label="WAITING FOR DISPATCH" color="warning" size="small" icon={<WaitingIcon />} />;
    }
  };

  const getCategoryChip = (cat: string) => {
    switch (cat) {
      case 'RED':
        return <Chip label="RED - IMMEDIATE" color="error" size="small" sx={{ fontWeight: 'bold' }} />;
      case 'YELLOW':
        return <Chip label="YELLOW - DELAYED" color="warning" size="small" sx={{ fontWeight: 'bold' }} />;
      case 'GREEN':
        return <Chip label="GREEN - MINOR" color="success" size="small" sx={{ fontWeight: 'bold' }} />;
      default:
        return <Chip label="BLACK - EXPECTANT" color="default" size="small" sx={{ fontWeight: 'bold' }} />;
    }
  };

  return (
    <Card variant="outlined" sx={{ borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header & Controls */}
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={3}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6" fontWeight="bold">
              Digital Victim Tracking Log ({filteredVictims.length})
            </Typography>
          </Box>

          <Box display="flex" gap={1.5} alignItems="center" flexWrap="wrap">
            <TextField
              size="small"
              placeholder="Search Tag ID or Injury..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                )
              }}
            />

            <Box display="flex" gap={0.5}>
              {['ALL', 'RED', 'YELLOW', 'GREEN', 'BLACK'].map(cat => (
                <Button
                  key={cat}
                  size="small"
                  variant={selectedFilter === cat ? 'contained' : 'outlined'}
                  color={cat === 'RED' ? 'error' : cat === 'YELLOW' ? 'warning' : cat === 'GREEN' ? 'success' : 'primary'}
                  onClick={() => setSelectedFilter(cat)}
                  sx={{ minWidth: 45, fontWeight: 'bold' }}
                >
                  {cat}
                </Button>
              ))}
            </Box>
          </Box>
        </Box>

        {/* Victims Table */}
        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table>
            <TableHead sx={{ bgcolor: 'grey.50' }}>
              <TableRow>
                <TableCell font-weight="bold">TAG BARCODE ID</TableCell>
                <TableCell font-weight="bold">TRIAGE CATEGORY</TableCell>
                <TableCell font-weight="bold">INJURY NOTES</TableCell>
                <TableCell font-weight="bold">ASSIGNED HOSPITAL</TableCell>
                <TableCell font-weight="bold">TRANSPORT STATUS</TableCell>
                <TableCell font-weight="bold">TRIAGE TIME</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredVictims.length > 0 ? (
                filteredVictims.map(v => (
                  <TableRow key={v.victim_tag_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold" fontFamily="monospace">
                        🏷️ {v.victim_tag_id}
                      </Typography>
                    </TableCell>
                    <TableCell>{getCategoryChip(v.triage_category)}</TableCell>
                    <TableCell>
                      <Typography variant="body2">{v.injury_description}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        🏥 {v.assigned_hospital_id || 'Level 1 Trauma Center'}
                      </Typography>
                    </TableCell>
                    <TableCell>{getStatusChip(v.transport_status)}</TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(v.triage_timestamp).toLocaleTimeString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                    <Typography color="text.secondary">No victims matching filter.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Paper>
      </CardContent>
    </Card>
  );
};

export default VictimTracker;
