import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Button,
  Divider
} from '@mui/material';
import { 
  Dashboard, 
  Analytics, 
  SmartToy,
  SportsSoccer,
  Logout
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Article } from '@mui/icons-material';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const menuItems = [
    { text: 'DASHBOARD', icon: <Dashboard />, path: '/' },
    { text: 'AI PREDICTIONS', icon: <Analytics />, path: '/predictions/pre-match' },
    { text: 'TEAM ANALYSIS', icon: <SportsSoccer />, path: '/team-analysis' },
    { text: 'NEWS & BLOGS', icon: <Article />, path: '/news' },
    { text: 'AI ANALYST', icon: <SmartToy />, path: '/chat' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
          backgroundColor: '#1e293b',
          color: 'white',
          display: 'flex',
          flexDirection: 'column'
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" fontWeight="bold" color="primary.main">
          SCORESIGHT
        </Typography>
        {user && (
          <Typography variant="body2" sx={{ color: '#b0bec5', mt: 1 }}>
            Welcome, {user.firstName}
          </Typography>
        )}
      </Box>
      
      <Divider sx={{ borderColor: '#334155', mb: 1 }} />
      
      <List sx={{ flexGrow: 1 }}>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            disablePadding
            sx={{
              mb: 1,
              mx: 1
            }}
          >
            <ListItemButton
              onClick={() => navigate(item.path)}
              sx={{
                backgroundColor: location.pathname === item.path ? 'primary.main' : 'transparent',
                '&:hover': {
                  backgroundColor: location.pathname === item.path ? 'primary.main' : 'primary.dark',
                },
                borderRadius: 1,
              }}
            >
              <ListItemIcon sx={{ color: 'white' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Logout Button */}
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<Logout />}
          onClick={handleLogout}
          sx={{
            color: '#f87171',
            borderColor: '#f87171',
            '&:hover': {
              backgroundColor: 'rgba(248, 113, 113, 0.08)',
              borderColor: '#ef4444',
            },
          }}
        >
          LOGOUT
        </Button>
      </Box>
    </Drawer>
  );
};

export default Sidebar;