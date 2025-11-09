import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container,
  Box,
  Button
} from '@mui/material';
import SportsSoccerIcon from '@mui/icons-material/SportsSoccer';
import { Logout } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'AI Predictions', path: '/predictions/pre-match' },
    { label: 'Team Analysis', path: '/team-analysis' },
    { label: 'News & Blogs', path: '/news' }, // ← ADD THIS LINE
    { label: 'AI Analyst', path: '/chat' },
    { label: 'Half-Time Predictions', path: '/predictions/half-time' }
  ];

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <Box sx={{ flexGrow: 1, background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%)', minHeight: '100vh' }}>
      <AppBar 
        position="static" 
        sx={{ 
          background: 'rgba(26, 26, 46, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        <Toolbar>
          <SportsSoccerIcon sx={{ mr: 2, color: '#00d4ff' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 700, color: '#00d4ff' }}>
            SCORESIGHT
          </Typography>
          
          {/* Navigation Items */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                color="inherit"
                onClick={() => navigate(item.path)}
                sx={{ 
                  mx: 0.5,
                  background: location.pathname === item.path 
                    ? 'linear-gradient(45deg, #00d4ff, #ff6bff)' 
                    : 'transparent',
                  color: location.pathname === item.path ? 'black' : 'white',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  px: 2,
                  py: 1,
                  '&:hover': {
                    background: location.pathname === item.path 
                      ? 'linear-gradient(45deg, #00d4ff, #ff6bff)'
                      : 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>

          {/* User welcome and logout button */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, ml: 2 }}>
            {user && (
              <Typography variant="body2" sx={{ color: '#b0bec5', display: { xs: 'none', sm: 'block' } }}>
                Welcome, {user.firstName}
              </Typography>
            )}
            <Button
              color="inherit"
              onClick={handleLogout}
              startIcon={<Logout />}
              sx={{
                color: '#ff6b6b',
                border: '1px solid #ff6b6b',
                px: 2,
                '&:hover': {
                  backgroundColor: 'rgba(255, 107, 107, 0.1)',
                }
              }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout;