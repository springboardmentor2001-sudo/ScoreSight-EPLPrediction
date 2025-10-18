import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography
} from '@mui/material';
import { 
  Dashboard, 
  Analytics, 
  SmartToy,
  SportsSoccer 
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'DASHBOARD', icon: <Dashboard />, path: '/dashboard' },
    { text: 'AI PREDICTIONS', icon: <Analytics />, path: '/predictions/pre-match' },
    { text: 'TEAM ANALYSIS', icon: <SportsSoccer />, path: '/team-analysis' },
    { text: 'AI ANALYST', icon: <SmartToy />, path: '/ai-analyst' },
  ];

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
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" fontWeight="bold" color="primary.main">
          SCORESIGHT
        </Typography>
      </Box>
      
      <List>
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
                  backgroundColor: 'primary.dark',
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
    </Drawer>
  );
};

export default Sidebar;