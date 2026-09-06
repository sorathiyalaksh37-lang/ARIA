import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Translate as LanguageIcon,
  Timer as TimerIcon,
  VolumeUp as SoundIcon,
  ArrowForward as NextIcon,
  ArrowBack as PrevIcon
} from '@mui/icons-material';

export interface ProtocolDetail {
  id: string;
  category: string;
  severity: string;
  icon: string;
  video_url?: string;
  compression_rate_bpm?: string;
  language: string;
  language_name: string;
  title: string;
  summary: string;
  key_stats?: string;
  steps: string[];
  warnings?: string;
}

interface ProtocolStepsProps {
  protocol: ProtocolDetail;
  onLanguageChange: (lang: string) => void;
  onActionCompleted: (stepIndex: number, stepText: string) => void;
  currentLanguage: string;
}

const ProtocolSteps: React.FC<ProtocolStepsProps> = ({
  protocol,
  onLanguageChange,
  onActionCompleted,
  currentLanguage
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});

  // CPR Metronome State (110 BPM visual pulsing)
  const [cprActive, setCprActive] = useState(false);
  const [pulse, setPulse] = useState(false);

  // Cooling Timer State (10 minute burn timer)
  const [timerSeconds, setTimerSeconds] = useState(600);
  const [timerActive, setTimerActive] = useState(false);

  // CPR Metronome interval
  useEffect(() => {
    let interval: any = null;
    if (cprActive) {
      // 110 BPM = ~545ms per beat
      interval = setInterval(() => {
        setPulse(p => !p);
      }, 545);
    } else {
      setPulse(false);
    }
    return () => clearInterval(interval);
  }, [cprActive]);

  // Burn Cooling Timer interval
  useEffect(() => {
    let interval: any = null;
    if (timerActive && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds(sec => sec - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timerActive, timerSeconds]);

  const handleNext = () => {
    handleStepComplete(activeStep);
    setActiveStep(prev => Math.min(prev + 1, protocol.steps.length - 1));
  };

  const handleBack = () => {
    setActiveStep(prev => Math.max(prev - 1, 0));
  };

  const handleStepComplete = (stepIdx: number) => {
    setCompletedSteps(prev => ({ ...prev, [stepIdx]: true }));
    onActionCompleted(stepIdx, protocol.steps[stepIdx]);
  };

  const formatTimer = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const remainder = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`;
  };

  const isCPR = protocol.id === 'cpr';
  const isBurn = protocol.id === 'burn_treatment';

  return (
    <Card variant="outlined" sx={{ borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header & Language Selector */}
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={2}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <Typography variant="h3">{protocol.icon}</Typography>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                {protocol.title}
              </Typography>
              <Chip
                label={`SEVERITY: ${protocol.severity.toUpperCase()}`}
                color={protocol.severity === 'critical' ? 'error' : 'warning'}
                size="small"
                sx={{ fontWeight: 'bold', mt: 0.5 }}
              />
            </Box>
          </Box>

          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel id="lang-select-label">Language / भाषा</InputLabel>
            <Select
              labelId="lang-select-label"
              value={currentLanguage}
              label="Language / भाषा"
              onChange={(e) => onLanguageChange(e.target.value)}
              startAdornment={<LanguageIcon sx={{ mr: 1, color: 'text.secondary' }} />}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="hi">Hindi (हिंदी)</MenuItem>
              <MenuItem value="mr">Marathi (मराठी)</MenuItem>
              <MenuItem value="ta">Tamil (தமிழ்)</MenuItem>
              <MenuItem value="te">Telugu (తెలుగు)</MenuItem>
              <MenuItem value="bn">Bengali (বাংলা)</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {protocol.key_stats && (
          <Paper variant="outlined" sx={{ p: 1.5, mb: 3, bgcolor: 'primary.50', borderColor: 'primary.200', borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" color="primary.900">
              ⚡ KEY EMERGENCY STATS: {protocol.key_stats}
            </Typography>
          </Paper>
        )}

        {/* CPR Metronome Helper Widget */}
        {isCPR && (
          <Paper
            elevation={0}
            sx={{
              p: 2,
              mb: 3,
              bgcolor: pulse ? 'error.main' : 'error.50',
              color: pulse ? 'white' : 'error.900',
              borderRadius: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              transition: 'all 0.15s ease'
            }}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <SoundIcon sx={{ fontSize: 32 }} />
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  CPR Compression Tempo Metronome (110 BPM)
                </Typography>
                <Typography variant="body2">
                  Match chest compressions to this rhythm ('Stayin Alive' beat).
                </Typography>
              </Box>
            </Box>
            <Button
              variant={cprActive ? 'contained' : 'outlined'}
              color="error"
              startIcon={cprActive ? <PauseIcon /> : <PlayIcon />}
              onClick={() => setCprActive(!cprActive)}
              sx={{ bgcolor: cprActive ? 'white' : 'transparent', color: cprActive ? 'error.main' : 'inherit' }}
            >
              {cprActive ? 'Pause Beats' : 'Start CPR Beats'}
            </Button>
          </Paper>
        )}

        {/* Burn Cooling Timer Helper Widget */}
        {isBurn && (
          <Paper
            elevation={0}
            sx={{
              p: 2,
              mb: 3,
              bgcolor: 'info.50',
              border: '1px solid',
              borderColor: 'info.200',
              borderRadius: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <TimerIcon color="info" sx={{ fontSize: 32 }} />
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  10-Minute Burn Cooling Countdown: {formatTimer(timerSeconds)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Keep clean cool running water flowing over the burn area.
                </Typography>
              </Box>
            </Box>
            <Button
              variant="contained"
              color="info"
              startIcon={timerActive ? <PauseIcon /> : <PlayIcon />}
              onClick={() => setTimerActive(!timerActive)}
            >
              {timerActive ? 'Pause Timer' : 'Start 10m Cool'}
            </Button>
          </Paper>
        )}

        {/* Interactive Step Wizard */}
        <Stepper activeStep={activeStep} orientation="vertical">
          {protocol.steps.map((stepText, index) => (
            <Step key={index} completed={Boolean(completedSteps[index])}>
              <StepLabel
                optional={
                  completedSteps[index] ? (
                    <Chip label="Completed" color="success" size="small" sx={{ fontSize: 10, height: 18 }} />
                  ) : null
                }
              >
                <Typography variant="subtitle1" fontWeight={activeStep === index ? 'bold' : 'normal'}>
                  Step {index + 1}
                </Typography>
              </StepLabel>
              <StepContent>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 2, mb: 2 }}>
                  <Typography variant="body1" fontSize={16} lineHeight={1.6}>
                    {stepText}
                  </Typography>
                </Paper>
                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNext}
                    endIcon={<NextIcon />}
                    size="small"
                  >
                    {index === protocol.steps.length - 1 ? 'Finish Protocol' : 'Complete & Next'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    startIcon={<PrevIcon />}
                    size="small"
                  >
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>

        {/* Warnings Alert */}
        {protocol.warnings && (
          <Alert severity="warning" sx={{ mt: 3, borderRadius: 2 }} icon={<WarningIcon />}>
            <Typography variant="subtitle2" fontWeight="bold">CRITICAL WARNING:</Typography>
            <Typography variant="body2">{protocol.warnings}</Typography>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ProtocolSteps;
