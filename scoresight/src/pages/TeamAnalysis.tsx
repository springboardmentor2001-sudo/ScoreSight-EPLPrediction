import React, { useState } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Avatar,
  LinearProgress,
  Paper,
  Tabs,
  Tab,
  Chip,
  Button,
  Grid
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Equalizer,
  EmojiEvents,
  Schedule,
  Group,
  SportsSoccer,
  Insights
} from '@mui/icons-material';
import { mockTeams } from '../services/mockData';

const TeamAnalysis: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState(mockTeams[0]);
  const [activeTab, setActiveTab] = useState(0);

  // Mock team stats
  const teamStats = {
    form: ['W', 'W', 'D', 'L', 'W'],
    attack: 84,
    defense: 76,
    midfield: 79,
    overall: 81,
    position: 3,
    points: 45,
    goalsFor: 38,
    goalsAgainst: 19,
    last5Matches: [
      { opponent: 'MCI', result: 'W', score: '2-1', home: true },
      { opponent: 'ARS', result: 'D', score: '1-1', home: false },
      { opponent: 'CHE', result: 'W', score: '3-0', home: true },
      { opponent: 'TOT', result: 'L', score: '0-2', home: false },
      { opponent: 'NEW', result: 'W', score: '2-0', home: true }
    ],
    upcomingMatches: [
      { opponent: 'LIV', home: false, date: '2024-01-20' },
      { opponent: 'BHA', home: true, date: '2024-01-27' },
      { opponent: 'MUN', home: false, date: '2024-02-03' }
    ]
  };

  const StatCard: React.FC<{ title: string; value: number; max?: number; color?: string }> = 
    ({ title, value, max = 100, color = '#00d4ff' }) => (
    <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" fontWeight="700" color={color}>
          {value}
        </Typography>
        <LinearProgress 
          variant="determinate" 
          value={value} 
          sx={{ 
            mt: 1,
            height: 6,
            borderRadius: 3,
            backgroundColor: 'rgba(255,255,255,0.1)',
            '& .MuiLinearProgress-bar': { backgroundColor: color }
          }}
        />
      </CardContent>
    </Card>
  );

  const FormIndicator: React.FC<{ result: string }> = ({ result }) => {
    const color = result === 'W' ? '#00ff88' : result === 'D' ? '#ffaa00' : '#ff4444';
    return (
      <Avatar sx={{ width: 32, height: 32, bgcolor: color, fontSize: '0.8rem', fontWeight: '700' }}>
        {result}
      </Avatar>
    );
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Team Analysis
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Deep insights into team performance, form, and statistics
        </Typography>
      </Box>

      {/* Team Selection */}
      <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Group sx={{ mr: 1 }} />
            SELECT TEAM
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {mockTeams.map((team) => (
              <Button
                key={team.id}
                variant={selectedTeam.id === team.id ? "contained" : "outlined"}
                onClick={() => setSelectedTeam(team)}
                startIcon={<Avatar sx={{ width: 24, height: 24 }}>{team.crest}</Avatar>}
                sx={{
                  background: selectedTeam.id === team.id 
                    ? 'linear-gradient(45deg, #00d4ff, #0099cc)' 
                    : 'transparent',
                  borderColor: 'primary.main'
                }}
              >
                {team.shortName}
              </Button>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Team Overview */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 4, mb: 4 }}>
        {/* Main Stats */}
        <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Avatar sx={{ width: 60, height: 60, bgcolor: 'primary.main', mr: 2, fontSize: '1.5rem' }}>
                {selectedTeam.crest}
              </Avatar>
              <Box>
                <Typography variant="h4" fontWeight="700">
                  {selectedTeam.name}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                  <Chip 
                    icon={<EmojiEvents />} 
                    label={`Position: ${teamStats.position}`} 
                    color="primary" 
                    variant="outlined"
                  />
                  <Chip 
                    icon={<TrendingUp />} 
                    label={`Points: ${teamStats.points}`} 
                    color="success" 
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Box>

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(4, 1fr)' }, gap: 2 }}>
              <StatCard title="Attack" value={teamStats.attack} color="#00ff88" />
              <StatCard title="Defense" value={teamStats.defense} color="#00d4ff" />
              <StatCard title="Midfield" value={teamStats.midfield} color="#ff6bff" />
              <StatCard title="Overall" value={teamStats.overall} color="#ffaa00" />
            </Box>
          </CardContent>
        </Card>

        {/* Form Guide */}
        <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUp sx={{ mr: 1 }} />
              FORM GUIDE
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
              {teamStats.form.map((result, index) => (
                <FormIndicator key={index} result={result} />
              ))}
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Goals For</Typography>
              <Typography variant="body2" fontWeight="600" color="#00ff88">
                {teamStats.goalsFor}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Goals Against</Typography>
              <Typography variant="body2" fontWeight="600" color="#ff4444">
                {teamStats.goalsAgainst}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Tabs for Detailed Analysis */}
      <Paper sx={{ background: 'transparent' }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            '& .MuiTab-root': { color: 'text.secondary', fontWeight: 600 },
            '& .Mui-selected': { color: 'primary.main' }
          }}
        >
          <Tab icon={<SportsSoccer />} label="Recent Matches" />
          <Tab icon={<Schedule />} label="Upcoming Fixtures" />
          <Tab icon={<Insights />} label="Advanced Stats" />
        </Tabs>

        {/* Recent Matches */}
        {activeTab === 0 && (
          <Box sx={{ mt: 3 }}>
            {teamStats.last5Matches.map((match, index) => (
              <Card key={index} sx={{ mb: 2, background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <FormIndicator result={match.result} />
                      <Box>
                        <Typography variant="body1" fontWeight="600">
                          vs {match.opponent}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {match.home ? 'Home' : 'Away'} • {match.score}
                        </Typography>
                      </Box>
                    </Box>
                    <Chip 
                      label={match.result === 'W' ? 'WIN' : match.result === 'D' ? 'DRAW' : 'LOSS'}
                      color={match.result === 'W' ? 'success' : match.result === 'D' ? 'warning' : 'error'}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        {/* Upcoming Fixtures */}
        {activeTab === 1 && (
          <Box sx={{ mt: 3 }}>
            {teamStats.upcomingMatches.map((match, index) => (
              <Card key={index} sx={{ mb: 2, background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.main' }}>
                        {selectedTeam.crest}
                      </Avatar>
                      <Typography variant="h6" fontWeight="600">
                        VS
                      </Typography>
                      <Avatar sx={{ width: 40, height: 40, bgcolor: 'secondary.main' }}>
                        {mockTeams.find(t => t.shortName === match.opponent)?.crest}
                      </Avatar>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="body1" fontWeight="600">
                        {match.home ? 'Home' : 'Away'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(match.date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        {/* Advanced Stats */}
        {activeTab === 2 && (
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
              <StatCard title="Expected Goals (xG)" value={32} color="#00ff88" />
              <StatCard title="Expected Goals Against (xGA)" value={24} color="#ff4444" />
              <StatCard title="Possession %" value={58} color="#00d4ff" />
              <StatCard title="Shot Conversion" value={12} color="#ff6bff" />
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default TeamAnalysis;