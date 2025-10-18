import React, { useState } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  MenuItem,
  Chip,
  Avatar,
  LinearProgress,
  Paper,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  PlayArrow,
  Insights,
  AutoAwesome,
  Psychology,
  Share,
  ContentCopy
} from '@mui/icons-material';
import { mockTeams } from '../services/mockData';

const PreMatchPrediction: React.FC = () => {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = () => {
    if (!homeTeam || !awayTeam) return;
    
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const homeWinProb = Math.random() * 0.6 + 0.2;
      const drawProb = Math.random() * 0.3;
      const awayWinProb = 1 - homeWinProb - drawProb;

      setPrediction({
        homeWinProbability: homeWinProb,
        drawProbability: drawProb,
        awayWinProbability: awayWinProb,
        predictedScore: `${Math.round(homeWinProb * 2)}-${Math.round(awayWinProb * 2)}`,
        confidence: homeWinProb > 0.55 || awayWinProb > 0.55 ? 'high' : 'medium',
        keyFactors: [
          'Team form in last 5 matches',
          'Head-to-head record',
          'Home advantage significance',
          'Key player availability'
        ],
        aiExplanation: `Based on current form and historical data, ${
          homeWinProb > awayWinProb ? 'the home team' : 'the away team'
        } has a significant advantage due to recent performance and tactical setup.`
      });
      setLoading(false);
    }, 1500);
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'error';
      default: return 'default';
    }
  };

  const PredictionResult: React.FC = () => (
    <Card sx={{ mt: 4, background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AutoAwesome sx={{ mr: 1, color: '#00ff88' }} />
          <Typography variant="h5" fontWeight="700">
            AI PREDICTION RESULTS
          </Typography>
        </Box>

        {/* Teams and Score */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 4, mb: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                {mockTeams.find(t => t.id === parseInt(homeTeam))?.crest}
              </Avatar>
              <Typography variant="h6" fontWeight="600">
                {mockTeams.find(t => t.id === parseInt(homeTeam))?.shortName}
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="h3" fontWeight="800" color="primary">
                {prediction.predictedScore}
              </Typography>
              <Chip 
                label={`${prediction.confidence.toUpperCase()} CONFIDENCE`}
                color={getConfidenceColor(prediction.confidence) as any}
                sx={{ fontWeight: 600 }}
              />
            </Box>

            <Box sx={{ textAlign: 'center' }}>
              <Avatar sx={{ width: 80, height: 80, bgcolor: 'secondary.main', mx: 'auto', mb: 1 }}>
                {mockTeams.find(t => t.id === parseInt(awayTeam))?.crest}
              </Avatar>
              <Typography variant="h6" fontWeight="600">
                {mockTeams.find(t => t.id === parseInt(awayTeam))?.shortName}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Probability Bars */}
        <Box sx={{ mb: 4 }}>
          {[
            { label: 'Home Win', prob: prediction.homeWinProbability, color: '#00d4ff' },
            { label: 'Draw', prob: prediction.drawProbability, color: '#ff6bff' },
            { label: 'Away Win', prob: prediction.awayWinProbability, color: '#00ff88' }
          ].map((item, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1" fontWeight="600">{item.label}</Typography>
                <Typography variant="body1" fontWeight="600" color={item.color}>
                  {(item.prob * 100).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={item.prob * 100}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: item.color,
                    borderRadius: 6,
                  }
                }}
              />
            </Box>
          ))}
        </Box>

        <Divider sx={{ my: 3, borderColor: 'rgba(255,255,255,0.1)' }} />

        {/* AI Explanation */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Psychology sx={{ mr: 1, color: '#00d4ff' }} />
            <Typography variant="h6" fontWeight="600">
              AI EXPLANATION
            </Typography>
          </Box>
          <Paper sx={{ p: 3, background: 'rgba(0, 212, 255, 0.05)', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
            <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
              {prediction.aiExplanation}
            </Typography>
          </Paper>
        </Box>

        {/* Key Factors */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" fontWeight="600" gutterBottom>
            KEY FACTORS
          </Typography>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
            gap: 2 
          }}>
            {prediction.keyFactors.map((factor: string, index: number) => (
              <Chip 
                key={index}
                label={factor}
                variant="outlined"
                sx={{ 
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  fontWeight: 500
                }}
              />
            ))}
          </Box>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
          <Button 
            variant="contained" 
            startIcon={<Share />}
            sx={{ 
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              fontWeight: 600
            }}
          >
            Share Prediction
          </Button>
          <Button 
            variant="outlined"
            startIcon={<ContentCopy />}
          >
            Copy Results
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          AI Match Predictor
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Get machine learning-powered predictions with 75.7% accuracy
        </Typography>
      </Box>

      {/* Prediction Form */}
      <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Insights sx={{ mr: 1, color: '#00ff88' }} />
            <Typography variant="h5" fontWeight="700">
              PREDICTION INPUT
            </Typography>
          </Box>

          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: '1fr auto 1fr' }, 
            gap: 3,
            alignItems: 'center'
          }}>
            {/* Home Team */}
            <Box>
              <TextField
                select
                fullWidth
                label="Home Team"
                value={homeTeam}
                onChange={(e) => setHomeTeam(e.target.value)}
                variant="outlined"
              >
                {mockTeams.map((team) => (
                  <MenuItem key={team.id} value={team.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ width: 24, height: 24, mr: 2, bgcolor: 'primary.main' }}>
                        {team.crest}
                      </Avatar>
                      {team.name}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            </Box>

            {/* VS */}
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                VS
              </Typography>
            </Box>

            {/* Away Team */}
            <Box>
              <TextField
                select
                fullWidth
                label="Away Team"
                value={awayTeam}
                onChange={(e) => setAwayTeam(e.target.value)}
                variant="outlined"
              >
                {mockTeams.map((team) => (
                  <MenuItem key={team.id} value={team.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ width: 24, height: 24, mr: 2, bgcolor: 'secondary.main' }}>
                        {team.crest}
                      </Avatar>
                      {team.name}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            </Box>
          </Box>

          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={loading ? null : <PlayArrow />}
              onClick={handlePredict}
              disabled={!homeTeam || !awayTeam || loading}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #ff6bff)',
                fontWeight: 700,
                fontSize: '1.1rem',
                px: 4,
                py: 1.5,
                minWidth: 200
              }}
            >
              {loading ? 'ANALYZING...' : 'GET AI PREDICTION'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Prediction Results */}
      {prediction && <PredictionResult />}

      {/* Model Info */}
      <Card sx={{ mt: 4, background: 'rgba(0, 212, 255, 0.05)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Psychology sx={{ mr: 1 }} />
            ABOUT OUR AI MODEL
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • 75.7% accuracy on Premier League matches
            <br />
            • Trained on 10 seasons of historical data (2010-2020)
            <br />
            • 51 carefully engineered features with zero data leakage
            <br />
            • Ensemble model (Random Forest + XGBoost + Logistic Regression)
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PreMatchPrediction;