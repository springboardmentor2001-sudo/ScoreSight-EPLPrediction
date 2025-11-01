import React, { useState, useEffect } from 'react';
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
  Grid,
  CircularProgress,
  Alert
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
import { footballAPI } from '../services/footballApi';

// Add interface for Team
interface Team {
  id: number;
  name: string;
  shortName: string;
  crest: string;
}

interface TeamStats {
  team_name: string;
  total_matches: number;
  wins: number;
  draws: number;
  losses: number;
  win_percentage: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  avg_goals_for: number;
  avg_goals_against: number;
  clean_sheets: number;
  total_points: number;
  points_per_game: number;
  recent_form: string[];
  attack_strength: number;
  defense_strength: number;
  overall_strength: number;
  home_record: {
    wins: number;
    draws: number;
    losses: number;
    goals_for: number;
    goals_against: number;
  };
  away_record: {
    wins: number;
    draws: number;
    losses: number;
    goals_for: number;
    goals_against: number;
  };
  recent_matches?: any[];
  analysis?: string;
}

const TeamAnalysis: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [teamStats, setTeamStats] = useState<TeamStats | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [teamsLoading, setTeamsLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch teams from API
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const teamsData = await footballAPI.getTeams();
        const teamsList = teamsData.teams || [];
        setTeams(teamsList);
        if (teamsList.length > 0) {
          setSelectedTeam(teamsList[0]);
        }
      } catch (error) {
        console.error('Error fetching teams:', error);
        setTeams([]);
        setError('Failed to load teams');
      } finally {
        setTeamsLoading(false);
      }
    };

    fetchTeams();
  }, []);

  // Fetch team stats when selected team changes
  useEffect(() => {
    const fetchTeamStats = async () => {
      if (!selectedTeam) return;
      
      setStatsLoading(true);
      setError(null);
      
      try {
        const stats = await footballAPI.getTeamAnalysis(selectedTeam.name);
        setTeamStats(stats);
      } catch (error) {
        console.error('Error fetching team stats:', error);
        setError('Failed to load team statistics');
        setTeamStats(null);
      } finally {
        setStatsLoading(false);
      }
    };

    fetchTeamStats();
  }, [selectedTeam]);
 
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

  if (teamsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!selectedTeam) {
    return (
      <Box>
        <Typography variant="h3" component="h1" gutterBottom>
          Team Analysis
        </Typography>
        <Alert severity="error">No teams available</Alert>
      </Box>
    );
  }

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

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Team Selection */}
      <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Group sx={{ mr: 1 }} />
            SELECT TEAM
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {teams.map((team) => (
              <Button
                key={team.id}
                variant={selectedTeam.id === team.id ? "contained" : "outlined"}
                onClick={() => setSelectedTeam(team)}
                startIcon={<Avatar sx={{ width: 24, height: 24 }} src={team.crest} />}
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

      {statsLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>
            Loading {selectedTeam.name} statistics...
          </Typography>
        </Box>
      ) : teamStats ? (
        <>
          {/* Team Overview */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 4, mb: 4 }}>
            {/* Main Stats */}
            <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Avatar sx={{ width: 60, height: 60, bgcolor: 'primary.main', mr: 2, fontSize: '1.5rem' }}>
                    {selectedTeam.shortName.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="700">
                      {selectedTeam.name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                      <Chip 
                        icon={<EmojiEvents />} 
                        label={`Win Rate: ${teamStats.win_percentage}%`} 
                        color="primary" 
                        variant="outlined"
                      />
                      <Chip 
                        icon={<TrendingUp />} 
                        label={`PPG: ${teamStats.points_per_game}`} 
                        color="success" 
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </Box>

                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(4, 1fr)' }, gap: 2 }}>
                  <StatCard title="Attack" value={teamStats.attack_strength} color="#00ff88" />
                  <StatCard title="Defense" value={teamStats.defense_strength} color="#00d4ff" />
                  <StatCard title="Overall" value={teamStats.overall_strength} color="#ffaa00" />
                  <StatCard title="Clean Sheets" value={teamStats.clean_sheets} color="#ff6bff" />
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
                  {teamStats.recent_form.map((result, index) => (
                    <FormIndicator key={index} result={result} />
                  ))}
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Goals For</Typography>
                  <Typography variant="body2" fontWeight="600" color="#00ff88">
                    {teamStats.goals_for}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Goals Against</Typography>
                  <Typography variant="body2" fontWeight="600" color="#ff4444">
                    {teamStats.goals_against}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Goal Difference</Typography>
                  <Typography variant="body2" fontWeight="600" color={teamStats.goal_difference >= 0 ? "#00ff88" : "#ff4444"}>
                    {teamStats.goal_difference > 0 ? '+' : ''}{teamStats.goal_difference}
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
              <Tab icon={<Equalizer />} label="Performance" />
              <Tab icon={<Insights />} label="Analysis" />
            </Tabs>

            {/* Recent Matches */}
            {activeTab === 0 && (
              <Box sx={{ mt: 3 }}>
                {teamStats.recent_matches && teamStats.recent_matches.length > 0 ? (
                  teamStats.recent_matches.map((match, index) => (
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
                                {match.match_type === 'home' ? 'Home' : 'Away'} • {match.goals_for}-{match.goals_against}
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
                  ))
                ) : (
                  <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                    No recent matches data available.
                  </Typography>
                )}
              </Box>
            )}
            {/* Performance */}
{activeTab === 1 && (
  <Box sx={{ mt: 3 }}>
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
      <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Home Record</Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Wins:</Typography>
            <Typography fontWeight="600">{teamStats.home_record.wins}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Draws:</Typography>
            <Typography fontWeight="600">{teamStats.home_record.draws}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Losses:</Typography>
            <Typography fontWeight="600">{teamStats.home_record.losses}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography>Goals:</Typography>
            <Typography fontWeight="600">{teamStats.home_record.goals_for}-{teamStats.home_record.goals_against}</Typography>
          </Box>
        </CardContent>
      </Card>
      <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Away Record</Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Wins:</Typography>
            <Typography fontWeight="600">{teamStats.away_record.wins}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Draws:</Typography>
            <Typography fontWeight="600">{teamStats.away_record.draws}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Losses:</Typography>
            <Typography fontWeight="600">{teamStats.away_record.losses}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography>Goals:</Typography>
            <Typography fontWeight="600">{teamStats.away_record.goals_for}-{teamStats.away_record.goals_against}</Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  </Box>
)}

            {/* Analysis */}
            {activeTab === 2 && (
              <Box sx={{ mt: 3 }}>
                <Card sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Team Analysis</Typography>
                    <Typography variant="body1">
                      {teamStats.analysis || "No analysis available for this team."}
                    </Typography>
                  </CardContent>
                </Card>
                
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mt: 3 }}>
                  <StatCard title="Average Goals For" value={teamStats.avg_goals_for * 20} color="#00ff88" />
                  <StatCard title="Average Goals Against" value={teamStats.avg_goals_against * 20} color="#ff4444" />
                </Box>
              </Box>
            )}
          </Paper>
        </>
      ) : (
        <Alert severity="warning">
          No statistics available for {selectedTeam.name}. This team may not be in the historical dataset.
        </Alert>
      )}
    </Box>
  );
};

export default TeamAnalysis;