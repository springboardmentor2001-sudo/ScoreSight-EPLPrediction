import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Fade
} from '@mui/material';
import { LoginFormData } from '../../types/auth';
import { useAuth } from '../../contexts/AuthContext';

interface LoginFormProps {
  onToggleMode: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onToggleMode }) => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [localLoading, setLocalLoading] = useState(false);
  const { login, authMessage, clearMessage } = useAuth();

  useEffect(() => {
    // Clear message when component mounts
    clearMessage();
  }, [clearMessage]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    clearMessage();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalLoading(true);
    setError('');
    clearMessage();

    try {
      const success = await login(formData.email, formData.password);
      if (!success) {
        setError('Let\'s try that again! Check your email and password. 🔍');
      }
    } catch (err) {
      setError('Login failed. Even the best strikers miss sometimes! ⚽');
    } finally {
      setLocalLoading(false);
    }
  };

  const funnyPlaceholders = [
    "Enter your email... unless you're a robot 🤖",
    "Your secret password goes here 🕵️",
    "Email address (we promise no spam!) 📧",
    "Shh... password time! 🤫"
  ];

  const getRandomPlaceholder = (field: string) => {
    if (field === 'email') return funnyPlaceholders[0];
    if (field === 'password') return funnyPlaceholders[1];
    return '';
  };

  return (
    <Paper 
      elevation={8}
      sx={{
        p: 4,
        background: 'linear-gradient(135deg, #0a1929 0%, #102a43 100%)',
        border: '1px solid #1e3a5c',
        borderRadius: 3,
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Animated background elements */}
      <Box
        sx={{
          position: 'absolute',
          top: -50,
          right: -50,
          width: 100,
          height: 100,
          background: 'radial-gradient(circle, #2196F3 0%, transparent 70%)',
          opacity: 0.1,
          animation: 'pulse 2s infinite'
        }}
      />
      
      <Typography variant="h4" component="h1" gutterBottom fontWeight="700" color="primary">
        SCORESIGHT
      </Typography>
      <Typography variant="h6" gutterBottom sx={{ color: '#b0bec5', mb: 3 }}>
        Welcome Back to the Prediction Master! 🎯
      </Typography>

      {error && (
        <Fade in={true}>
          <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
            {error}
          </Alert>
        </Fade>
      )}

      {authMessage && !error && (
        <Fade in={true}>
          <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
            {authMessage}
          </Alert>
        </Fade>
      )}

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          required
          margin="normal"
          variant="outlined"
          placeholder={getRandomPlaceholder('email')}
          sx={{
            '& .MuiOutlinedInput-root': {
              color: 'white',
              '& fieldset': {
                borderColor: '#334d6e',
              },
              '&:hover fieldset': {
                borderColor: '#4f8cff',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#4f8cff',
              },
            },
            '& .MuiInputLabel-root': {
              color: '#b0bec5',
            },
          }}
        />
        <TextField
          fullWidth
          label="Password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          required
          margin="normal"
          variant="outlined"
          placeholder={getRandomPlaceholder('password')}
          sx={{
            '& .MuiOutlinedInput-root': {
              color: 'white',
              '& fieldset': {
                borderColor: '#334d6e',
              },
              '&:hover fieldset': {
                borderColor: '#4f8cff',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#4f8cff',
              },
            },
            '& .MuiInputLabel-root': {
              color: '#b0bec5',
            },
          }}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          size="large"
          disabled={localLoading}
          sx={{
            mt: 3,
            mb: 2,
            py: 1.5,
            background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)',
            fontWeight: '600',
            fontSize: '1rem',
            '&:hover': {
              background: 'linear-gradient(135deg, #1976D2 0%, #1565C0 100%)',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 20px rgba(33, 150, 243, 0.4)',
            },
            '&:disabled': {
              background: '#424242',
            },
            transition: 'all 0.3s ease'
          }}
        >
          {localLoading ? (
            <CircularProgress size={24} sx={{ color: 'white' }} />
          ) : (
            'Unlock Predictions! 🔓'
          )}
        </Button>
      </form>

      <Box textAlign="center">
        <Typography variant="body2" sx={{ color: '#b0bec5', mb: 1 }}>
          New to Scoresight?
        </Typography>
        <Button
          onClick={onToggleMode}
          sx={{
            color: '#4f8cff',
            fontWeight: '600',
            textTransform: 'none',
            fontSize: '1rem',
            '&:hover': {
              backgroundColor: 'transparent',
              color: '#2196F3',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.2s ease'
          }}
        >
          Join the Winning Team! 🏆
        </Button>
      </Box>
    </Paper>
  );
};

export default LoginForm;