import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper
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
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const success = await login(formData.email, formData.password);
      if (!success) {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper 
      elevation={8}
      sx={{
        p: 4,
        background: 'linear-gradient(135deg, #0a1929 0%, #102a43 100%)',
        border: '1px solid #1e3a5c',
        borderRadius: 3,
        color: 'white'
      }}
    >
      <Typography variant="h4" component="h1" gutterBottom fontWeight="700" color="primary">
        SCORESIGHT
      </Typography>
      <Typography variant="h6" gutterBottom sx={{ color: '#b0bec5', mb: 3 }}>
        Welcome Back
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
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
          disabled={loading}
          sx={{
            mt: 3,
            mb: 2,
            py: 1.5,
            background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)',
            fontWeight: '600',
            fontSize: '1rem',
            '&:hover': {
              background: 'linear-gradient(135deg, #1976D2 0%, #1565C0 100%)',
              transform: 'translateY(-1px)',
              boxShadow: '0 4px 12px rgba(33, 150, 243, 0.4)',
            },
            '&:disabled': {
              background: '#424242',
            }
          }}
        >
          {loading ? <CircularProgress size={24} /> : 'Sign In'}
        </Button>
      </form>

      <Box textAlign="center">
        <Typography variant="body2" sx={{ color: '#b0bec5' }}>
          Don't have an account?{' '}
          <Button
            onClick={onToggleMode}
            sx={{
              color: '#4f8cff',
              fontWeight: '600',
              textTransform: 'none',
              '&:hover': {
                backgroundColor: 'transparent',
                color: '#2196F3',
              }
            }}
          >
            Sign Up
          </Button>
        </Typography>
      </Box>
    </Paper>
  );
};

export default LoginForm;