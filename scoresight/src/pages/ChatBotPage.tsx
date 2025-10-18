import React from 'react';
import { Typography, Box } from '@mui/material';
import ChatBot from '../components/chat/ChatBot';

const ChatBotPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        AI Football Analyst
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Get expert insights and prediction explanations
      </Typography>
      
      <ChatBot />
    </Box>
  );
};

export default ChatBotPage;