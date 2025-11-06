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
import { SignupFormData } from '../../types/auth';
import { useAuth } from '../../contexts/AuthContext';

interface SignupFormProps {
  onToggleMode: () => void;
}

const SignupForm: React.FC<SignupFormProps> = ({ onToggleMode }) => {
  const [formData, setFormData] = useState<SignupFormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [localLoading, setLocalLoading] = useState(false);
  const { signup, authMessage, clearMessage } = useAuth();

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
    setError('');
    clearMessage();

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords don\'t match! Are you seeing double? 👀');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password needs at least 6 characters - make it strong! 💪');
      return;
    }

    setLocalLoading(true);

    try {
      const success = await signup(
        formData.email,
        formData.password,
        formData.firstName,
        formData.lastName
      );
      if (!success) {
        setError('Let\'s try that again! The goal is wide open! ⚽');
      }
    } catch (err) {
      setError('Signup failed. Even VAR can\'t help with this one! 🎥');
    } finally {
      setLocalLoading(false);
    }
  };

  const funnyPlaceholders = {
    firstName: "Your first name (no nicknames!) 👤",
    lastName: "Your last name 🏷️",
    email: "Your best email 📧",
    password: "Create a super secret password! 🕵️",
    confirmPassword: "Type it again (no pressure!) 🔁"
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
          top: -30,
          left: -30,
          width: 80,
          height: 80,
          background: 'radial-gradient(circle, #334d6e 0%, transparent 70%)',
          opacity: 0.1,
          animation: 'pulse 3s infinite'
        }}
      />
      
      <Typography variant="h4" component="h1" gutterBottom fontWeight="700" color="primary">
        SCORESIGHT
      </Typography>
      <Typography variant="h6" gutterBottom sx={{ color: '#b0bec5', mb: 3 }}>
        Join the Prediction Elite! 🚀
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
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            label="First Name"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            required
            margin="normal"
            variant="outlined"
            placeholder={funnyPlaceholders.firstName}
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
            label="Last Name"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            required
            margin="normal"
            variant="outlined"
            placeholder={funnyPlaceholders.lastName}
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
        </Box>
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
          placeholder={funnyPlaceholders.email}
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
          placeholder={funnyPlaceholders.password}
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
          label="Confirm Password"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          margin="normal"
          variant="outlined"
          placeholder={funnyPlaceholders.confirmPassword}
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
            color: 'white',
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
            'Start Predicting! 🎯'
          )}
        </Button>
      </form>

      <Box textAlign="center">
        <Typography variant="body2" sx={{ color: '#b0bec5', mb: 1 }}>
          Already have an account?
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
          Welcome Back! 🏆
        </Button>
      </Box>
    </Paper>
  );
};

export default SignupForm;