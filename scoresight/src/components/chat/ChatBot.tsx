import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Paper,
  Chip
} from '@mui/material';
import { Send, SmartToy, Person } from '@mui/icons-material';

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Array<{id: string, content: string, role: 'user' | 'assistant'}>>([
    {
      id: '1',
      content: "Hello! I'm Scoresight AI. I can explain predictions, analyze teams, and provide football insights.",
      role: 'assistant'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user' as const
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        content: "I can help analyze team form, explain predictions, or compare statistics. What would you like to know?",
        role: 'assistant' as const
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1000);
  };

  const quickQuestions = [
    "Explain today's predictions",
    "Compare two teams", 
    "Best betting value"
  ];

  const handleQuickQuestion = (question: string) => {
    setInput(question);
    setTimeout(() => handleSend(), 100);
  };

  return (
    <Card sx={{ 
      height: '500px', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
    }}>
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
        
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <Typography variant="h6" fontWeight="bold" color="#00d4ff">
            🎯 Scoresight AI Analyst
          </Typography>
        </Box>

        {/* Messages */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, maxWidth: '70%' }}>
                <Avatar sx={{ 
                  width: 32, 
                  height: 32, 
                  bgcolor: message.role === 'user' ? '#00d4ff' : '#ff6bff' 
                }}>
                  {message.role === 'user' ? <Person /> : <SmartToy />}
                </Avatar>
                <Paper sx={{ 
                  p: 1.5, 
                  bgcolor: message.role === 'user' ? '#00d4ff' : 'rgba(41, 40, 40, 1)',
                }}>
                  <Typography variant="body1" sx={{ color: message.role === 'user' ? 'white' : 'white' }}>
    {message.content}
</Typography>
                </Paper>
              </Box>
            </Box>
          ))}
          
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#ff6bff' }}>
                  <SmartToy />
                </Avatar>
                <Paper sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.1)' }}>
                  <Typography variant="body1" sx={{ color: 'white' }}>
                    Thinking...
                  </Typography>
                </Paper>
              </Box>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Quick Questions */}
        <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            {quickQuestions.map((question, index) => (
              <Chip
                key={index}
                label={question}
                size="small"
                onClick={() => handleQuickQuestion(question)}
                sx={{ 
                  borderColor: '#00d4ff', 
                  color: '#00d4ff',
                  '&:hover': { bgcolor: '#00d4ff', color: 'black' }
                }}
              />
            ))}
          </Box>

          {/* Input */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask about predictions or teams..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              disabled={isLoading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': {
                    borderColor: 'rgba(255,255,255,0.3)',
                  },
                  '&:hover fieldset': {
                    borderColor: '#00d4ff',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#00d4ff',
                  },
                },
                '& .MuiInputBase-input': {
                  color: 'white',
                },
                '& .MuiInputLabel-root': {
                  color: 'white',
                },
              }}
              InputProps={{
                sx: {
                  color: 'white',
                  '& input': {
                    color: 'white',
                  },
                },
              }}
              inputProps={{
                style: { color: 'white' }
              }}
            />
            <IconButton 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              sx={{ bgcolor: '#00d4ff', color: 'black' }}
            >
              <Send />
            </IconButton>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ChatBot;