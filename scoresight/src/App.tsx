import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, CircularProgress, Typography } from '@mui/material';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import PreMatchPrediction from './pages/PreMatchPrediction';
import TeamAnalysis from './pages/TeamAnalysis';
import ChatBotPage from './pages/ChatBotPage';
import HalfTimePrediction from './pages/HalfTimePrediction';
import ApiStatus from './components/common/ApiStatus';
import PredictionPage from './pages/PredictionPage';
import AuthPage from './pages/AuthPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';

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

// Loading component for initial auth check
const LoadingScreen: React.FC = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      background: 'linear-gradient(135deg, #0a1929 0%, #102a43 100%)',
      flexDirection: 'column',
      gap: 3,
    }}
  >
    <CircularProgress 
      size={60} 
      sx={{ 
        color: '#00d4ff',
        '& .MuiCircularProgress-circle': {
          strokeLinecap: 'round',
        }
      }} 
    />
    <Typography
      variant="h5"
      sx={{
        background: 'linear-gradient(45deg, #00d4ff, #ff6bff)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        fontWeight: 600,
      }}
    >
      Loading Scoresight...
    </Typography>
  </Box>
);

// Protected Route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" />;
};

// Public Route component (redirect to dashboard if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return !isAuthenticated ? <>{children}</> : <Navigate to="/" />;
};

function AppContent() {
  const { loading } = useAuth();

  // Show loading screen during initial auth check
  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      <Routes>
        {/* Public route - only accessible when not logged in */}
        <Route 
          path="/auth" 
          element={
            <PublicRoute>
              <AuthPage />
            </PublicRoute>
          } 
        />
        
        {/* Protected routes - only accessible when logged in */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout>
                <ApiStatus />
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/predictions/pre-match" 
          element={
            <ProtectedRoute>
              <Layout>
                <ApiStatus />
                <PreMatchPrediction />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/team-analysis" 
          element={
            <ProtectedRoute>
              <Layout>
                <ApiStatus />
                <TeamAnalysis />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/chat" 
          element={
            <ProtectedRoute>
              <Layout>
                <ApiStatus />
                <ChatBotPage />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/predictions/half-time" 
          element={
            <ProtectedRoute>
              <Layout>
                <ApiStatus />
                <HalfTimePrediction />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/prediction" 
          element={
            <ProtectedRoute>
              <Layout>
                <ApiStatus />
                <PredictionPage />
              </Layout>
            </ProtectedRoute>
          } 
        />

        {/* Redirect any unknown routes to home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;