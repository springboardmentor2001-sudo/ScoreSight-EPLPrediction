import React, { useState } from 'react';
import { Box, Container, Typography } from '@mui/material';
import LoginForm from '../components/auth/LoginForm';
import SignupForm from '../components/auth/SignupForm';

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a1929 0%, #0d1b2a 50%, #1b263b 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 4
      }}
    >
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {/* Header Section */}
          <Box textAlign="center" sx={{ mb: 4 }}>
            <Typography 
              variant="h2" 
              component="h1" 
              fontWeight="800" 
              sx={{
                background: 'linear-gradient(135deg, #2196F3 0%, #21CBF3 100%)',
                backgroundClip: 'text',
                textFillColor: 'transparent',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2
              }}
            >
              SCORESIGHT
            </Typography>
            <Typography 
              variant="h6" 
              sx={{ 
                color: '#b0bec5',
                maxWidth: 400,
                mx: 'auto'
              }}
            >
              Advanced Premier League Predictions Powered by AI
            </Typography>
          </Box>

          {/* Auth Form */}
          {isLogin ? (
            <LoginForm onToggleMode={toggleMode} />
          ) : (
            <SignupForm onToggleMode={toggleMode} />
          )}

          {/* Features Section */}
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" sx={{ color: '#78909c', mb: 1 }}>
              • 75.7% Prediction Accuracy • Live Match Updates • AI Insights •
            </Typography>
            <Typography variant="body2" sx={{ color: '#78909c' }}>
              • Premier League Focus • Real-time Analytics • Expert Betting Recommendations •
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default AuthPage;