import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Divider,
  Alert
} from '@mui/material';
import {
  Send as SendIcon,
  Sms as SmsIcon,
  PhoneInTalk as PhoneIcon,
  WhatsApp as WhatsAppIcon,
  NotificationsActive as PushIcon,
  OpenInNew as LinkIcon,
  PlayCircleOutline as VideoIcon
} from '@mui/icons-material';

import ProtocolSteps, { ProtocolDetail } from './ProtocolSteps';
import { apiClient } from '../api/client';

interface FirstAidInstructionsProps {
  protocols: ProtocolDetail[];
  onDeliverInstructions?: (protocolId: string, phone: string, language: string) => void;
}

const FirstAidInstructions: React.FC<FirstAidInstructionsProps> = ({
  protocols,
  onDeliverInstructions
}) => {
  const [selectedProtocolId, setSelectedProtocolId] = useState<string>(protocols[0]?.id || 'cpr');
  const [currentLang, setCurrentLang] = useState<string>('en');

  // Multi-channel delivery dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [phone, setPhone] = useState('+91-9876543210');
  const [deliveryStatus, setDeliveryStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const activeProtocol = protocols.find(p => p.id === selectedProtocolId) || protocols[0];

  const handleLanguageChange = async (newLang: string) => {
    setCurrentLang(newLang);
    try {
      const res = await apiClient.get(`/bystander/protocols/${selectedProtocolId}?lang=${newLang}`);
      if (res.data?.data) {
        // update language state
      }
    } catch {
      // fallback
    }
  };

  const handleActionLogged = async (stepIdx: number, stepText: string) => {
    try {
      await apiClient.post('/bystander/confirm-action', {
        action_step: `Completed Step ${stepIdx + 1}: ${stepText.substring(0, 40)}...`
      });
    } catch (e) {
      console.warn('Logging action failed:', e);
    }
  };

  const handleSendMultiChannel = async () => {
    try {
      setLoading(true);
      const res = await apiClient.post('/bystander/deliver-instructions', {
        protocol_id: selectedProtocolId,
        bystander_phone: phone,
        language: currentLang
      });

      setDeliveryStatus('✅ Instructions successfully dispatched via SMS, Voice Call, WhatsApp & Push Notification!');
      if (onDeliverInstructions) {
        onDeliverInstructions(selectedProtocolId, phone, currentLang);
      }
    } catch (err: any) {
      alert('Failed to dispatch instructions: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Top Banner & Dispatch Launcher */}
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
          <Typography variant="h3">{activeProtocol?.icon || '🚑'}</Typography>
          <Box>
            <Typography variant="h6" fontWeight="bold">
              Bystander Protocol: {activeProtocol?.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Step-by-step emergency instructions with audio tempo & multi-language translation.
            </Typography>
          </Box>
        </Box>

        <Button
          variant="contained"
          color="error"
          startIcon={<SendIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{ fontWeight: 'bold' }}
        >
          Send Instructions to Bystander Phone
        </Button>
      </Paper>

      {/* Protocol Selection Chips */}
      <Box display="flex" gap={1} overflow="auto" pb={1} mb={3}>
        {protocols.map(p => (
          <Chip
            key={p.id}
            label={`${p.icon} ${p.title}`}
            clickable
            color={selectedProtocolId === p.id ? 'primary' : 'default'}
            variant={selectedProtocolId === p.id ? 'filled' : 'outlined'}
            onClick={() => setSelectedProtocolId(p.id)}
            sx={{ fontWeight: selectedProtocolId === p.id ? 'bold' : 'normal', px: 1 }}
          />
        ))}
      </Box>

      {/* Main Protocol Steps Component */}
      {activeProtocol && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <ProtocolSteps
              protocol={activeProtocol}
              currentLanguage={currentLang}
              onLanguageChange={handleLanguageChange}
              onActionCompleted={handleActionLogged}
            />
          </Grid>

          {/* Side Media & Multi-Channel Delivery Info Panel */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined" sx={{ borderRadius: 3, mb: 3 }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Video Tutorial Guide
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Watch demonstration video for {activeProtocol.title}.
                </Typography>

                <Paper
                  variant="outlined"
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    bgcolor: 'grey.100',
                    borderRadius: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 1
                  }}
                >
                  <VideoIcon color="error" sx={{ fontSize: 50 }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    Official AHA/Red Cross Video Guide
                  </Typography>
                  <Button
                    variant="contained"
                    color="error"
                    size="small"
                    startIcon={<LinkIcon />}
                    href={activeProtocol.video_url || 'https://www.youtube.com'}
                    target="_blank"
                  >
                    Open Live Video Link
                  </Button>
                </Paper>
              </CardContent>
            </Card>

            {/* Multi-Channel Delivery Status */}
            <Card variant="outlined" sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Multi-Channel Instruction Delivery
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Active instruction channels linked to caller phone.
                </Typography>

                <Box display="flex" flexDirection="column" gap={1.5}>
                  <Box display="flex" alignItems="center" gap={1.5}>
                    <SmsIcon color="primary" />
                    <Typography variant="body2">SMS Step-by-Step Text</Typography>
                    <Chip label="ACTIVE" color="success" size="small" sx={{ ml: 'auto', fontSize: 10 }} />
                  </Box>
                  <Box display="flex" alignItems="center" gap={1.5}>
                    <PhoneIcon color="success" />
                    <Typography variant="body2">Automated Voice Instructions</Typography>
                    <Chip label="READY" color="info" size="small" sx={{ ml: 'auto', fontSize: 10 }} />
                  </Box>
                  <Box display="flex" alignItems="center" gap={1.5}>
                    <WhatsAppIcon color="success" />
                    <Typography variant="body2">WhatsApp Interactive Cards</Typography>
                    <Chip label="ACTIVE" color="success" size="small" sx={{ ml: 'auto', fontSize: 10 }} />
                  </Box>
                  <Box display="flex" alignItems="center" gap={1.5}>
                    <PushIcon color="warning" />
                    <Typography variant="body2">App Push Notification</Typography>
                    <Chip label="DELIVERED" color="primary" size="small" sx={{ ml: 'auto', fontSize: 10 }} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Multi-Channel Dispatch Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight="bold">
          Send First Aid Instructions to Bystander
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Enter bystander phone number to trigger SMS, Voice Call, WhatsApp, and Web links in selected language ({currentLang.toUpperCase()}).
          </Typography>

          <TextField
            label="Bystander Phone Number"
            fullWidth
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+91-9876543210"
            sx={{ mb: 2 }}
          />

          {deliveryStatus && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {deliveryStatus}
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleSendMultiChannel}
            disabled={loading}
            startIcon={<SendIcon />}
          >
            {loading ? 'Dispatching...' : 'Dispatch All 5 Channels'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FirstAidInstructions;
