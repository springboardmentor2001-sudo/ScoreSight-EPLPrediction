import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import PreMatchPrediction from './pages/PreMatchPrediction';
import TeamAnalysis from './pages/TeamAnalysis';
import ChatBotPage from './pages/ChatBotPage';
import HalfTimePrediction from './pages/HalfTimePrediction';
import ApiStatus from './components/common/ApiStatus';
import PredictionPage from './pages/PredictionPage';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00d4ff',
      light: '#66e3ff',
      dark: '#00a3cc',
    },
    secondary: {
      main: '#ff6bff',
      light: '#ff99ff',
      dark: '#ff3dff',
    },
    background: {
      default: '#0a0a0f',
      paper: '#1a1a2e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b0b0',
    },
    success: {
      main: '#00ff88',
    },
    warning: {
      main: '#ffaa00',
    },
    error: {
      main: '#ff4444',
    },
  },
  typography: {
    h3: {
      fontWeight: 800,
      background: 'linear-gradient(45deg, #00d4ff, #ff6bff)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <ApiStatus />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/predictions/pre-match" element={<PreMatchPrediction />} />
            <Route path="/team-analysis" element={<TeamAnalysis />} />
            // And in routes:
            <Route path="/chat" element={<ChatBotPage />} />
            <Route path="/predictions/half-time" element={<HalfTimePrediction />} />
            <Route path="/prediction" element={<PredictionPage />} />
            <Route 
              path="/chat" 
              element={
                <div style={{
                  background: 'red', 
                  color: 'white', 
                  padding: '50px',
                  fontSize: '24px',
                  fontWeight: 'bold'
                }}>
                  🎯 CHATBOT ROUTE IS WORKING! 🎯
                </div>
              } 
            />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
    
  );
}

export default App;