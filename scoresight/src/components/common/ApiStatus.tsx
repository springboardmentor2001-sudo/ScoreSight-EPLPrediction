import React, { useEffect, useState } from 'react';
import { Chip, Box, Typography } from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';
import liveDataService from '../../services/liveDataService';

const ApiStatus: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'connected' | 'error'>('loading');

  useEffect(() => {
    const testConnection = async () => {
      try {
        await liveDataService.getTeams();
        setStatus('connected');
      } catch (error) {
        setStatus('error');
      }
    };

    testConnection();
  }, []);

  return (
    <Box sx={{ position: 'fixed', top: 70, right: 16, zIndex: 1000 }}>
      <Chip
        icon={status === 'connected' ? <CheckCircle /> : status === 'error' ? <Error /> : undefined}
        label={
          status === 'connected' ? 'API Connected' :
          status === 'error' ? 'API Offline' : 'Checking API...'
        }
        color={
          status === 'connected' ? 'success' :
          status === 'error' ? 'error' : 'default'
        }
        variant="outlined"
      />
    </Box>
  );
};

export default ApiStatus;