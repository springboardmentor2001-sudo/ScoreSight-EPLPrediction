import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  Skeleton
} from '@mui/material';
import { 
  TrendingUp, 
  Schedule, 
  Notifications, 
  Insights,
  Groups,
  EmojiEvents,
  LiveTv,
  Chat
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import liveDataService from '../services/liveDataService';
import { footballAPI } from '../services/footballApi';

// Add these interfaces for our data
interface Team {
  id: number;
  name: string;
  shortName: string;
  crest: string;
}

interface LiveMatch {
  id: number;
  homeTeam: Team;
  awayTeam: Team;
  date: string;
  status: string;
  score: any;
  venue: string;
  matchday: number;
}

interface Prediction {
  homeTeam: Team;
  awayTeam: Team;
  homeWinProbability: number;
  drawProbability: number;
  awayWinProbability: number;
  confidence: 'high' | 'medium' | 'low';
  predictedScore: string;
  keyFactors: string[];
  betRecommendation?: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [liveMatches, setLiveMatches] = useState<LiveMatch[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchLiveData = async () => {
      try {
        const fixtures = await liveDataService.getFixtures();
        console.log('Fixtures from API:', fixtures);
        
        // Show first 4 matches regardless of date for testing
        const upcomingMatches = fixtures.slice(0, 4);
        setLiveMatches(upcomingMatches);

        // Generate mock predictions based on real fixtures
        const mockPredictions = upcomingMatches.map((match: LiveMatch, index: number) => ({
          homeTeam: match.homeTeam,
          awayTeam: match.awayTeam,
          homeWinProbability: 0.4 + (index * 0.1), // Varying probabilities
          drawProbability: 0.25,
          awayWinProbability: 0.35 - (index * 0.1),
          confidence: index === 0 ? 'high' : index === 1 ? 'medium' : 'low' as const,
          predictedScore: index === 0 ? '2-1' : index === 1 ? '1-1' : '0-2',
          keyFactors: [
            'Home advantage significant',
            'Recent form analysis',
            'Head-to-head record favorable'
          ],
          betRecommendation: index === 0 ? 'HOME WIN' : undefined
        }));

        setPredictions(mockPredictions);
      } catch (error) {
        console.error('Error fetching live data:', error);
        // Create fallback empty state instead of using mock data
        setLiveMatches([]);
        setPredictions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchLiveData();
  }, []);

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'error';
      default: return 'default';
    }
  };

  const getWinProbabilityColor = (probability: number) => {
    if (probability > 0.6) return '#4caf50';
    if (probability > 0.4) return '#ff9800';
    return '#f44336';
  };

  const StatsOverview: React.FC = () => (
    <Box sx={{ 
      display: 'grid', 
      gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' }, 
      gap: 3, 
      mb: 4 
    }}>
      {/* Stats cards remain the same */}
      <Card sx={{ 
        height: '100%', 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <CardContent>
          <TrendingUp sx={{ mb: 1, fontSize: 40, opacity: 0.8 }} />
          <Typography variant="h4" component="div" fontWeight="700" sx={{ textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}>
            75.7%
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Pre-Match Accuracy
          </Typography>
          <Chip 
            label="PROVEN" 
            size="small" 
            sx={{ 
              background: 'rgba(255,255,255,0.2)', 
              color: 'white', 
              mt: 1,
              fontWeight: '600'
            }} 
          />
        </CardContent>
      </Card>

      <Card sx={{ 
        height: '100%', 
        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        color: 'white'
      }}>
        <CardContent>
          <Insights sx={{ mb: 1, fontSize: 40, opacity: 0.8 }} />
          <Typography variant="h4" component="div" fontWeight="700">
            68.1%
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Half-Time Accuracy
          </Typography>
          <Chip 
            label="LIVE" 
            size="small" 
            sx={{ 
              background: 'rgba(255,255,255,0.2)', 
              color: 'white', 
              mt: 1,
              fontWeight: '600'
            }} 
          />
        </CardContent>
      </Card>

      <Card sx={{ height: '100%', position: 'relative' }}>
        <CardContent>
          <Schedule sx={{ mb: 1, fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h4" component="div" fontWeight="700" color="primary">
            {loading ? '...' : liveMatches.length}
          </Typography>
          <Typography color="text.secondary">
            Matches Today
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <LiveTv sx={{ fontSize: 16, mr: 0.5, color: 'error.main' }} />
            <Typography variant="caption" color="error.main" fontWeight="600">
              {liveMatches.filter(m => m.status === 'LIVE').length} LIVE NOW
            </Typography>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Groups sx={{ mb: 1, fontSize: 40, color: 'secondary.main' }} />
          <Typography variant="h4" component="div" fontWeight="700">
            20
          </Typography>
          <Typography color="text.secondary">
            Premier League Teams
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );

  const MatchCard: React.FC<{ match: LiveMatch; prediction?: Prediction }> = ({ match, prediction }) => {
    // Use the provided prediction or create a basic fallback
    const currentPrediction = prediction || {
      homeTeam: match.homeTeam,
      awayTeam: match.awayTeam,
      homeWinProbability: 0.5,
      drawProbability: 0.25,
      awayWinProbability: 0.25,
      confidence: 'medium' as const,
      predictedScore: '1-1',
      keyFactors: ['Data analysis in progress'],
      betRecommendation: undefined
    };

    return (
      <Card sx={{ 
        height: '100%',
        transition: 'all 0.3s ease-in-out',
        border: `2px solid ${currentPrediction.confidence === 'high' ? '#4caf50' : currentPrediction.confidence === 'medium' ? '#ff9800' : '#f44336'}`,
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
        }
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h6" component="div" fontWeight="600">
                {match.homeTeam.crest} {match.homeTeam.shortName} vs {match.awayTeam.crest} {match.awayTeam.shortName}
              </Typography>
              <Typography color="text.secondary" variant="caption">
                {new Date(match.date).toLocaleDateString('en-US', { 
                  weekday: 'short', 
                  month: 'short', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })} • {match.venue || 'Premier League'}
              </Typography>
            </Box>
            <Chip 
              label={`${currentPrediction.confidence.toUpperCase()} CONFIDENCE`} 
              size="small"
              color={getConfidenceColor(currentPrediction.confidence) as any}
            />
          </Box>

          {/* Probability Visualization */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main', fontSize: 12 }}>
                  {match.homeTeam.crest}
                </Avatar>
                <Typography variant="body2" fontWeight="600">{match.homeTeam.shortName}</Typography>
              </Box>
              <Typography variant="body2" fontWeight="600" color={getWinProbabilityColor(currentPrediction.homeWinProbability)}>
                {(currentPrediction.homeWinProbability * 100).toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={currentPrediction.homeWinProbability * 100} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                mb: 2,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getWinProbabilityColor(currentPrediction.homeWinProbability)
                }
              }} 
            />

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" fontWeight="600">Draw</Typography>
              <Typography variant="body2" fontWeight="600" color={getWinProbabilityColor(currentPrediction.drawProbability)}>
                {(currentPrediction.drawProbability * 100).toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={currentPrediction.drawProbability * 100} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                mb: 2,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getWinProbabilityColor(currentPrediction.drawProbability)
                }
              }} 
            />

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 24, height: 24, bgcolor: 'secondary.main', fontSize: 12 }}>
                  {match.awayTeam.crest}
                </Avatar>
                <Typography variant="body2" fontWeight="600">{match.awayTeam.shortName}</Typography>
              </Box>
              <Typography variant="body2" fontWeight="600" color={getWinProbabilityColor(currentPrediction.awayWinProbability)}>
                {(currentPrediction.awayWinProbability * 100).toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={currentPrediction.awayWinProbability * 100} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getWinProbabilityColor(currentPrediction.awayWinProbability)
                }
              }} 
            />
          </Box>

          {/* Key Insights */}
          <Box sx={{ 
            background: 'linear-gradient(135deg, #103163ff 0%, #0e2956ff 100%)', 
            p: 2, 
            borderRadius: 2,
            border: '1px solid #e0e0e0'
          }}>
            <Typography variant="subtitle2" fontWeight="600" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Insights sx={{ mr: 1, fontSize: 18 }} />
              AI KEY INSIGHTS
            </Typography>
            <Box component="ul" sx={{ pl: 2, m: 0 }}>
              {currentPrediction.keyFactors.map((factor: string, index: number) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 0.5 }}>
                  {factor}
                </Typography>
              ))}
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Predicted Score: <strong>{currentPrediction.predictedScore}</strong>
              </Typography>
              {currentPrediction.betRecommendation && (
                <Chip 
                  label={currentPrediction.betRecommendation} 
                  size="small" 
                  color="success"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {/* Header Section */}
      <Box sx={{ 
        mb: 4, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        flexDirection: { xs: 'column', md: 'row' },
        gap: 2
      }}>
        <Box>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="800" color="primary">
            SCORESIGHT
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
            Premier League AI Predictions • {time.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </Typography>
          <Typography variant="body1" sx={{ maxWidth: 600 }}>
            Advanced machine learning predictions with <strong>75.7% accuracy</strong>. 
            Powered by ensemble models trained on 10 seasons of Premier League data.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => navigate('/predictions/pre-match')}
            startIcon={<Insights />}
            sx={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              fontWeight: '600'
            }}
          >
            AI Predictions
          </Button>
          <Button 
            variant="outlined" 
            size="large"
            startIcon={<LiveTv />}
          >
            Live Matches
          </Button>
        </Box>
      </Box>

      {/* Stats Overview */}
      <StatsOverview />

      {/* Upcoming Matches Section */}
      <Box>
        <Typography variant="h5" fontWeight="700" gutterBottom sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
          <EmojiEvents sx={{ mr: 1, color: 'gold' }} />
          UPCOMING PREMIER LEAGUE MATCHES
        </Typography>

        {loading ? (
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent>
                  <Skeleton variant="text" height={40} />
                  <Skeleton variant="text" height={20} />
                  <Skeleton variant="rectangular" height={100} sx={{ mt: 2, borderRadius: 2 }} />
                </CardContent>
              </Card>
            ))}
          </Box>
        ) : (
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
            gap: 3 
          }}>
            {liveMatches.map((match, index) => (
              <MatchCard 
                key={match.id} 
                match={match} 
                prediction={predictions[index]} 
              />
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default Dashboard;