import React, { useState, useEffect } from 'react';
import { Trophy, Calendar, TrendingUp, ArrowRight, Brain, ChevronDown, ExternalLink } from 'lucide-react';

const Home = ({ user, onNavigate }) => {
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [showTeamDropdown, setShowTeamDropdown] = useState(false);

  // Premier League teams with logos
  const premierLeagueTeams = {
    'Arsenal': 'https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg',
    'Aston Villa': 'https://upload.wikimedia.org/wikipedia/de/9/9f/Aston_Villa_logo.svg',
    'Bournemouth': 'https://upload.wikimedia.org/wikipedia/en/e/e5/AFC_Bournemouth_%282013%29.svg',
    'Brentford': 'https://upload.wikimedia.org/wikipedia/en/2/2a/Brentford_FC_crest.svg',
    'Brighton': 'https://upload.wikimedia.org/wikipedia/en/f/fd/Brighton_%26_Hove_Albion_logo.svg',
    'Chelsea': 'https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg',
    'Crystal Palace': 'https://upload.wikimedia.org/wikipedia/sco/thumb/0/0c/Crystal_Palace_FC_logo.svg/1643px-Crystal_Palace_FC_logo.svg.png',
    'Everton': 'https://upload.wikimedia.org/wikipedia/en/7/7c/Everton_FC_logo.svg',
    'Fulham': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Fulham_FC_%28shield%29.svg',
    'Leeds United': 'https://upload.wikimedia.org/wikipedia/en/5/54/Leeds_United_F.C._logo.svg',
    'Leicester City': 'https://upload.wikimedia.org/wikipedia/en/2/2d/Leicester_City_crest.svg',
    'Liverpool': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg',
    'Man City': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg',
    'Man United': 'https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg',
    'Newcastle United': 'https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg',
    'Nottingham Forest': 'https://upload.wikimedia.org/wikipedia/en/e/e5/Nottingham_Forest_F.C._logo.svg',
    'Southampton': 'https://upload.wikimedia.org/wikipedia/en/c/c9/FC_Southampton.svg',
    'Tottenham': 'https://cdn.freebiesupply.com/logos/large/2x/tottenham-hotspur-logo-black-and-white.png',
    'West Ham': 'https://upload.wikimedia.org/wikipedia/en/c/c2/West_Ham_United_FC_logo.svg',
    'Wolverhampton': 'https://upload.wikimedia.org/wikipedia/en/f/fc/Wolverhampton_Wanderers.svg'
  };

  useEffect(() => {
    fetchUpcomingMatches();
    loadUserStats();
  }, []);

  // Load user stats from localStorage
  const loadUserStats = () => {
    const savedStats = localStorage.getItem(`userStats_${user?.username}`);
    if (savedStats) {
      setStats(JSON.parse(savedStats));
    } else {
      // Default stats
      const defaultStats = {
        totalPredictions: 47,
        accuracy: 75,
        favoriteTeam: null
      };
      setStats(defaultStats);
      saveUserStats(defaultStats);
    }
  };

  // Save user stats to localStorage
  const saveUserStats = (newStats) => {
    localStorage.setItem(`userStats_${user?.username}`, JSON.stringify(newStats));
  };

  const handleTeamSelect = (team) => {
    const updatedStats = {
      ...stats,
      favoriteTeam: team
    };
    setStats(updatedStats);
    saveUserStats(updatedStats);
    setShowTeamDropdown(false);
  };

  const fetchUpcomingMatches = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/matches', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUpcomingMatches(data.matches);
      } else {
        setUpcomingMatches(getSampleMatches());
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
      setUpcomingMatches(getSampleMatches());
    } finally {
      setLoading(false);
    }
  };

  const getSampleMatches = () => [
    {
      id: 1,
      home_team: 'Man City',
      away_team: 'Liverpool',
      date: '2024-12-15',
      time: '15:00',
      venue: 'Etihad Stadium'
    },
    {
      id: 2,
      home_team: 'Arsenal',
      away_team: 'Chelsea',
      date: '2024-12-16',
      time: '17:30',
      venue: 'Emirates Stadium'
    },
    {
      id: 3,
      home_team: 'Man United',
      away_team: 'Tottenham',
      date: '2024-12-17',
      time: '15:00',
      venue: 'Old Trafford'
    },
    {
      id: 4,
      home_team: 'Newcastle',
      away_team: 'Aston Villa',
      date: '2024-12-18',
      time: '15:00',
      venue: 'St James Park'
    },
    {
      id: 5,
      home_team: 'West Ham',
      away_team: 'Brighton',
      date: '2024-12-19',
      time: '19:45',
      venue: 'London Stadium'
    },
    {
      id: 6,
      home_team: 'Everton',
      away_team: 'Fulham',
      date: '2024-12-20',
      time: '15:00',
      venue: 'Goodison Park'
    },
    {
      id: 7,
      home_team: 'Brentford',
      away_team: 'Wolverhampton',
      date: '2024-12-21',
      time: '15:00',
      venue: 'Gtech Community Stadium'
    },
    {
      id: 8,
      home_team: 'Crystal Palace',
      away_team: 'Nottingham Forest',
      date: '2024-12-22',
      time: '15:00',
      venue: 'Selhurst Park'
    }
  ];

  const getMatchCardColor = (index) => {
    const colors = [
      'from-blue-500/20 to-purple-500/20',
      'from-green-500/20 to-blue-500/20',
      'from-purple-500/20 to-pink-500/20',
      'from-orange-500/20 to-red-500/20',
      'from-teal-500/20 to-cyan-500/20',
      'from-yellow-500/20 to-orange-500/20',
      'from-indigo-500/20 to-purple-500/20',
      'from-emerald-500/20 to-teal-500/20'
    ];
    return colors[index % colors.length];
  };

  // Show only first 3 matches on home page
  const displayedMatches = upcomingMatches.slice(0, 3);
  const hasMoreMatches = upcomingMatches.length > 3;

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
          Welcome back, {user?.username || 'User'}! 👋
        </h1>
        <p className="text-xl text-blue-200 max-w-4xl mx-auto">
          Ready to explore today's Premier League predictions and insights?
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Total Predictions</p>
              <p className="text-3xl font-bold text-white">{stats?.totalPredictions || 0}</p>
            </div>
            <Trophy className="h-8 w-8 text-yellow-400" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-2xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Prediction Accuracy</p>
              <p className="text-3xl font-bold text-white">{stats?.accuracy || 0}%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-400" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl p-6 border border-white/20 relative">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-blue-200 text-sm">Favorite Team</p>
              <div className="relative">
                <button
                  onClick={() => setShowTeamDropdown(!showTeamDropdown)}
                  className="flex items-center justify-between w-full text-left group"
                >
                  <div className="flex items-center gap-3">
                    {stats?.favoriteTeam && premierLeagueTeams[stats.favoriteTeam] ? (
                      <>
                        <img 
                          src={premierLeagueTeams[stats.favoriteTeam]} 
                          alt={stats.favoriteTeam}
                          className="w-8 h-8 object-contain"
                        />
                        <p className="text-xl font-bold text-white truncate">
                          {stats.favoriteTeam}
                        </p>
                      </>
                    ) : (
                      <p className="text-xl font-bold text-white/70">Select Team</p>
                    )}
                  </div>
                  <ChevronDown 
                    className={`h-5 w-5 text-purple-400 transition-transform group-hover:text-purple-300 ${
                      showTeamDropdown ? 'rotate-180' : ''
                    }`} 
                  />
                </button>
                
                {/* Dropdown Menu */}
                {showTeamDropdown && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-slate-600 rounded-lg shadow-2xl z-10 max-h-60 overflow-y-auto">
                    {Object.entries(premierLeagueTeams).map(([team, logo]) => (
                      <button
                        key={team}
                        onClick={() => handleTeamSelect(team)}
                        className={`w-full text-left px-4 py-3 hover:bg-slate-700 transition-colors flex items-center gap-3 ${
                          stats?.favoriteTeam === team 
                            ? 'bg-purple-600 text-white' 
                            : 'text-slate-200'
                        }`}
                      >
                        <img 
                          src={logo} 
                          alt={team}
                          className="w-6 h-6 object-contain"
                        />
                        <span className="font-medium">{team}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Close dropdown when clicking outside */}
      {showTeamDropdown && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setShowTeamDropdown(false)}
        />
      )}

      {/* Action Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12 max-w-7xl mx-auto">
        <button
          onClick={() => onNavigate('user-input')}
          className="bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-2xl p-8 border border-white/20 hover:border-white/40 transition-all duration-300 hover:scale-105 group text-left w-full"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-white mb-2">Predict Match</h3>
              <p className="text-blue-200 mb-4">
                Input match statistics and get real-time predictions
              </p>
              <div className="flex items-center text-green-400 group-hover:text-green-300">
                <span className="font-medium">Start Predicting</span>
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
            <Trophy className="h-12 w-12 text-green-400" />
          </div>
        </button>

        <button
          onClick={() => onNavigate('ai-predictor')}
          className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 rounded-2xl p-8 hover:border-cyan-400/50 transition-all duration-300 hover:scale-105 group text-left w-full"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-white mb-2">AI Predictor</h3>
              <p className="text-blue-200 mb-4">
                Advanced AI-powered predictions using team form, head-to-head records, and historical data analysis.
              </p>
              <div className="flex items-center text-cyan-400 group-hover:text-cyan-300">
                <span className="font-medium">Try AI Prediction</span>
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
            <Brain className="h-12 w-12 text-cyan-400" />
          </div>
        </button>
      </div>

      {/* Upcoming Matches Preview */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Calendar className="h-6 w-6 text-blue-400" />
              Upcoming Matches
            </h2>
            <span className="text-blue-400 text-sm font-medium bg-blue-500/20 px-3 py-1 rounded-full">
              {upcomingMatches.length} total matches
            </span>
          </div>
          {hasMoreMatches && (
            <button
              onClick={() => onNavigate('matches')}
              className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors duration-200 bg-blue-500/20 hover:bg-blue-500/30 px-4 py-2 rounded-lg border border-blue-500/30"
            >
              <span className="font-medium">View All</span>
              <ExternalLink className="h-4 w-4" />
            </button>
          )}
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="text-blue-200">Loading matches...</div>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-6">
              {displayedMatches.map((match, index) => (
                <div
                  key={match.id}
                  className={`bg-gradient-to-r ${getMatchCardColor(index)} rounded-xl p-6 border border-white/20 hover:border-white/40 transition-all duration-300 w-full`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          {premierLeagueTeams[match.home_team] && (
                            <img 
                              src={premierLeagueTeams[match.home_team]} 
                              alt={match.home_team}
                              className="w-8 h-8 object-contain"
                            />
                          )}
                          <span className="text-white font-semibold text-lg">{match.home_team}</span>
                        </div>
                        <div className="flex flex-col items-center">
                          <span className="text-blue-200 text-sm mx-4">VS</span>
                          <span className="text-blue-300 text-xs mt-1">{match.date}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-white font-semibold text-lg">{match.away_team}</span>
                          {premierLeagueTeams[match.away_team] && (
                            <img 
                              src={premierLeagueTeams[match.away_team]} 
                              alt={match.away_team}
                              className="w-8 h-8 object-contain"
                            />
                          )}
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm text-blue-200">
                        <span>{match.time} • {match.venue}</span>
                        <span className="text-blue-300">Match #{match.id}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Show more matches indicator */}
            {hasMoreMatches && (
              <div className="text-center pt-4 border-t border-white/20">
                <p className="text-blue-300 text-sm">
                  Showing 3 of {upcomingMatches.length} matches •{' '}
                  <button
                    onClick={() => onNavigate('matches')}
                    className="text-green-400 hover:text-green-300 font-medium underline transition-colors"
                  >
                    View all matches
                  </button>
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Home;