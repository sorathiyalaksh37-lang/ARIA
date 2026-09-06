import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Grid,
  Chip,
  Paper,
  Alert
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Sms as SmsIcon,
  WhatsApp as WhatsAppIcon,
  RecordVoiceOver as VoiceIcon,
  Language as LanguageIcon,
  Security as PrivacyIcon
} from '@mui/icons-material';

import { apiClient } from '../api/client';

export interface FamilyContact {
  contact_id?: string;
  incident_id: string;
  name: string;
  phone: string;
  email: string;
  relationship: string;
  is_primary: boolean;
  preferred_channel: 'SMS' | 'EMAIL' | 'WHATSAPP' | 'VOICE';
  language: string;
  privacy_level: 'EMERGENCY_ONLY' | 'FULL_MEDICAL';
  opt_in_notifications?: boolean;
}

interface FamilyContactFormProps {
  incidentId: string;
  onContactSaved: () => void;
  existingContact?: FamilyContact;
}

const FamilyContactForm: React.FC<FamilyContactFormProps> = ({
  incidentId,
  onContactSaved,
  existingContact
}) => {
  const [name, setName] = useState(existingContact?.name || '');
  const [phone, setPhone] = useState(existingContact?.phone || '+1-555-019-2834');
  const [email, setEmail] = useState(existingContact?.email || 'family@example.com');
  const [relationship, setRelationship] = useState(existingContact?.relationship || 'Spouse');
  const [isPrimary, setIsPrimary] = useState(existingContact?.is_primary ?? true);
  const [channel, setChannel] = useState<'SMS' | 'EMAIL' | 'WHATSAPP' | 'VOICE'>(
    existingContact?.preferred_channel || 'WHATSAPP'
  );
  const [language, setLanguage] = useState(existingContact?.language || 'en');
  const [privacyLevel, setPrivacyLevel] = useState<'EMERGENCY_ONLY' | 'FULL_MEDICAL'>(
    existingContact?.privacy_level || 'FULL_MEDICAL'
  );
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await apiClient.post('/family/contacts', {
        incident_id: incidentId,
        name,
        phone,
        email,
        relationship,
        is_primary: isPrimary,
        preferred_channel: channel,
        language,
        privacy_level: privacyLevel
      });

      setSuccessMsg(`✅ Family contact '${name}' saved successfully!`);
      if (onContactSaved) onContactSaved();
    } catch (err: any) {
      alert('Error saving contact: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card variant="outlined" sx={{ borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" gap={1.5} mb={2}>
          <PersonAddIcon color="primary" sx={{ fontSize: 28 }} />
          <Typography variant="h6" fontWeight="bold">
            {existingContact ? 'Edit Family Contact' : 'Register Emergency Family Contact'}
          </Typography>
        </Box>

        {successMsg && (
          <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
            {successMsg}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            {/* Name */}
            <Grid item xs={12} sm={6}>
              <TextField
                label="Contact Full Name"
                fullWidth
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Sarah Miller"
              />
            </Grid>

            {/* Relationship */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel id="relationship-label">Relationship</InputLabel>
                <Select
                  labelId="relationship-label"
                  value={relationship}
                  label="Relationship"
                  onChange={(e) => setRelationship(e.target.value)}
                >
                  <MenuItem value="Spouse">Spouse</MenuItem>
                  <MenuItem value="Parent">Parent</MenuItem>
                  <MenuItem value="Child">Child (Adult)</MenuItem>
                  <MenuItem value="Sibling">Sibling (Brother/Sister)</MenuItem>
                  <MenuItem value="Relative">Relative</MenuItem>
                  <MenuItem value="Friend">Friend</MenuItem>
                  <MenuItem value="Legal Guardian">Legal Guardian</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Phone */}
            <Grid item xs={12} sm={6}>
              <TextField
                label="Phone Number"
                fullWidth
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1-555-019-2834"
              />
            </Grid>

            {/* Email */}
            <Grid item xs={12} sm={6}>
              <TextField
                label="Email Address"
                type="email"
                fullWidth
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="sarah.miller@example.com"
              />
            </Grid>

            {/* Preferred Channel */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="channel-label">Preferred Channel</InputLabel>
                <Select
                  labelId="channel-label"
                  value={channel}
                  label="Preferred Channel"
                  onChange={(e: any) => setChannel(e.target.value)}
                >
                  <MenuItem value="WHATSAPP">💬 WhatsApp (Interactive Cards & Map)</MenuItem>
                  <MenuItem value="SMS">📱 SMS (Short Text Updates)</MenuItem>
                  <MenuItem value="EMAIL">✉️ Email (Detailed HTML Reports)</MenuItem>
                  <MenuItem value="VOICE">📞 Voice Call (Automated Audio Alert)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Language Preference */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="language-label">Language Preference</InputLabel>
                <Select
                  labelId="language-label"
                  value={language}
                  label="Language Preference"
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="hi">Hindi (हिंदी)</MenuItem>
                  <MenuItem value="mr">Marathi (मराठी)</MenuItem>
                  <MenuItem value="ta">Tamil (தமிழ்)</MenuItem>
                  <MenuItem value="te">Telugu (తెలుగు)</MenuItem>
                  <MenuItem value="bn">Bengali (বাংলা)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Privacy Consent Level */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="privacy-label">Privacy Consent Level</InputLabel>
                <Select
                  labelId="privacy-label"
                  value={privacyLevel}
                  label="Privacy Consent Level"
                  onChange={(e: any) => setPrivacyLevel(e.target.value)}
                >
                  <MenuItem value="FULL_MEDICAL">🩺 Full Medical Details (Vitals & Doctor Notes)</MenuItem>
                  <MenuItem value="EMERGENCY_ONLY">🚨 Emergency Only (Basic Status & Hospital Name)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Primary Toggle */}
            <Grid item xs={12} sm={6} display="flex" alignItems="center">
              <Paper variant="outlined" sx={{ p: 1.5, width: '100%', borderRadius: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={isPrimary}
                      onChange={(e) => setIsPrimary(e.target.checked)}
                      color="primary"
                    />
                  }
                  label={
                    <Typography variant="body2" fontWeight="bold">
                      Designate as Primary Emergency Contact
                    </Typography>
                  }
                />
              </Paper>
            </Grid>

            {/* Submit Button */}
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ borderRadius: 2, py: 1.2, fontWeight: 'bold' }}
              >
                {loading ? 'Saving Contact...' : 'Save Emergency Contact'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </CardContent>
    </Card>
  );
};

export default FamilyContactForm;
