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
  Chip,
  CircularProgress
} from '@mui/material';
import { Send, SmartToy, Person, Psychology, AutoAwesome } from '@mui/icons-material';
import { chatService, ChatMessage } from '../../services/chatService';

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: "Hello! I'm Scoresight AI. I can explain predictions, analyze teams using my ML models, and provide general football insights.",
      role: 'assistant',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSuggestions();
    scrollToBottom();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadSuggestions = async () => {
    const sugg = await chatService.getSuggestions();
    setSuggestions(sugg);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Get AI response
      const response = await chatService.sendMessage(input);
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        role: 'assistant',
        timestamp: response.timestamp,
        source: response.source,
        confidence: response.confidence
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I encountered an error. Please try again.",
        role: 'assistant',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
    // Auto-send after a short delay
    setTimeout(() => handleSend(), 100);
  };

  const getSourceIcon = (source?: string) => {
    switch (source) {
      case 'ml_model':
        return <AutoAwesome sx={{ fontSize: 16 }} />;
      case 'team_analyzer':
        return <Psychology sx={{ fontSize: 16 }} />;
      default:
        return <SmartToy sx={{ fontSize: 16 }} />;
    }
  };

  const getSourceColor = (source?: string) => {
    switch (source) {
      case 'ml_model':
        return '#00ff88';
      case 'team_analyzer':
        return '#ffaa00';
      default:
        return '#ff6bff';
    }
  };

  // Clear chat history
  const clearChat = () => {
    setMessages([{
      id: '1',
      content: "Hello! I'm Scoresight AI. I can explain predictions, analyze teams using my ML models, and provide general football insights.",
      role: 'assistant',
      timestamp: new Date().toISOString()
    }]);
  };

  return (
    <Card sx={{ 
      height: '600px', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      overflow: 'hidden'
    }}>
      <CardContent sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        p: 0,
        height: '100%'
      }}>
        
        {/* Header with Clear Button */}
        <Box sx={{ 
          p: 2, 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          flexShrink: 0,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Box>
            <Typography variant="h6" fontWeight="bold" color="#00d4ff">
              🎯 Scoresight AI Analyst
            </Typography>
            <Typography variant="caption" color="rgba(255,255,255,0.7)">
              Powered by ML Models & AI • 75% Prediction Accuracy
            </Typography>
          </Box>
          <Chip
            label="Clear Chat"
            size="small"
            onClick={clearChat}
            sx={{ 
              borderColor: '#ff6b6b', 
              color: '#ff6b6b',
              '&:hover': { bgcolor: '#ff6b6b', color: 'black' }
            }}
          />
        </Box>

        {/* Messages Container with FIXED Scrollbar */}
        <Box 
          ref={messagesContainerRef}
          sx={{ 
            flex: 1,
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column',
            p: 2,
            minHeight: 0, // This is crucial for scrolling to work
            // Custom scrollbar styling
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '4px',
              margin: '4px 0',
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'linear-gradient(180deg, #00d4ff 0%, #0099cc 100%)',
              borderRadius: '4px',
              border: '1px solid rgba(255,255,255,0.1)',
              '&:hover': {
                background: 'linear-gradient(180deg, #00b8e6 0%, #0088aa 100%)',
              },
            },
            // Firefox
            scrollbarWidth: 'thin',
            scrollbarColor: '#00d4ff rgba(255,255,255,0.05)',
          }}
        >
          {/* Messages */}
          <Box sx={{ flex: 1 }}>
            {messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  gap: 1, 
                  maxWidth: '90%',
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row'
                }}>
                  <Avatar sx={{ 
                    width: 32, 
                    height: 32, 
                    bgcolor: message.role === 'user' ? '#00d4ff' : getSourceColor(message.source),
                    flexShrink: 0
                  }}>
                    {message.role === 'user' ? <Person /> : getSourceIcon(message.source)}
                  </Avatar>
                  
                  <Paper sx={{ 
                    p: 1.5, 
                    bgcolor: message.role === 'user' ? '#00d4ff' : 'rgba(41, 40, 40, 1)',
                    border: message.role === 'assistant' ? `1px solid ${getSourceColor(message.source)}` : 'none',
                    maxWidth: '100%',
                    wordBreak: 'break-word',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                  }}>
                    <Typography variant="body1" sx={{ 
                      color: message.role === 'user' ? 'black' : 'white', 
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.4
                    }}>
                      {message.content}
                    </Typography>
                    
                    {message.role === 'assistant' && message.source && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                        <Typography variant="caption" sx={{ 
                          color: getSourceColor(message.source),
                          fontWeight: 'bold'
                        }}>
                          {message.source === 'ml_model' && '🤖 ML Prediction Model'}
                          {message.source === 'team_analyzer' && '📊 Historical Data Analysis'}
                          {message.source === 'chatgpt' && '🌐 General Knowledge'}
                        </Typography>
                      </Box>
                    )}
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
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} sx={{ color: '#00d4ff' }} />
                      <Typography variant="body1" sx={{ color: 'white' }}>
                        Analyzing with AI...
                      </Typography>
                    </Box>
                  </Paper>
                </Box>
              </Box>
            )}
          </Box>
          <div ref={messagesEndRef} />
        </Box>

        {/* Quick Questions & Input - Fixed at bottom */}
        <Box sx={{ 
          p: 2, 
          borderTop: '1px solid rgba(255,255,255,0.1)',
          flexShrink: 0,
          background: 'rgba(0,0,0,0.3)'
        }}>
          <Typography variant="caption" color="rgba(255,255,255,0.7)" sx={{ mb: 1, display: 'block' }}>
            Try asking about:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            {suggestions.slice(0, 6).map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                size="small"
                onClick={() => handleQuickQuestion(suggestion)}
                sx={{ 
                  borderColor: '#00d4ff', 
                  color: '#00d4ff',
                  fontSize: '0.75rem',
                  '&:hover': { bgcolor: '#00d4ff', color: 'black' }
                }}
              />
            ))}
          </Box>

          {/* Input */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask about predictions, teams, rules, or general football..."
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
              }}
              inputProps={{
                style: { color: 'white' }
              }}
            />
            <IconButton 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              sx={{ 
                bgcolor: '#00d4ff', 
                color: 'black',
                '&:hover': {
                  bgcolor: '#00b8e6',
                },
                '&:disabled': {
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'rgba(255,255,255,0.5)'
                }
              }}
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