import React, { useState, useEffect } from 'react';
import { Trophy, Calendar, Users, TrendingUp, ArrowRight, Brain } from 'lucide-react';

const Home = ({ user, onNavigate }) => { // Add onNavigate prop
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchUpcomingMatches();
    fetchDashboardStats();
  }, []);

  const fetchUpcomingMatches = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/matches', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUpcomingMatches(data.matches.slice(0, 5));
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardStats = async () => {
    setStats({
      totalPredictions: 47,
      accuracy: 75,
      favoriteTeam: 'Manchester City'
    });
  };

  const getMatchCardColor = (index) => {
    const colors = [
      'from-blue-500/20 to-purple-500/20',
      'from-green-500/20 to-blue-500/20',
      'from-purple-500/20 to-pink-500/20',
      'from-orange-500/20 to-red-500/20',
      'from-teal-500/20 to-cyan-500/20'
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
          Welcome back, {user.username}! 👋
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

        <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Favorite Team</p>
              <p className="text-3xl font-bold text-white">{stats?.favoriteTeam || 'N/A'}</p>
            </div>
            <Users className="h-8 w-8 text-purple-400" />
          </div>
        </div>
      </div>

      {/* Action Cards - FIXED NAVIGATION */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12 max-w-7xl mx-auto">
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

        {/* <button
          onClick={() => onNavigate('model-predict')}
          className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl p-8 border border-white/20 hover:border-white/40 transition-all duration-300 hover:scale-105 group text-left w-full"
        >
          <div className="flex items-center justify-between">
            <div>
              {/* <h3 className="text-2xl font-bold text-white mb-2">Model Predictions</h3> */}
              {/* <p className="text-blue-200 mb-4">
                View AI-generated predictions for upcoming matches
              </p>
              <div className="flex items-center text-purple-400 group-hover:text-purple-300">
                <span className="font-medium">View Predictions</span>
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
            <TrendingUp className="h-12 w-12 text-purple-400" />
          </div>
        </button> */} 

        {/* AI Predictor Card - ADDED */}
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

      {/* Upcoming Matches - FIXED NAVIGATION */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Calendar className="h-6 w-6 text-blue-400" />
            Upcoming Matches
          </h2>
          <button
            onClick={() => onNavigate('model-predict')}
            className="text-blue-400 hover:text-blue-300 text-sm font-medium flex items-center gap-1"
          >
            View All
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="text-blue-200">Loading matches...</div>
          </div>
        ) : (
          <div className="space-y-4">
            {upcomingMatches.map((match, index) => (
              <div
                key={match.id}
                className={`bg-gradient-to-r ${getMatchCardColor(index)} rounded-xl p-6 border border-white/20 hover:border-white/40 transition-all duration-300 w-full`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-semibold text-lg">{match.home_team}</span>
                      <span className="text-blue-200 text-sm">VS</span>
                      <span className="text-white font-semibold text-lg">{match.away_team}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-blue-200">
                      <span>{match.date} • {match.time}</span>
                      <span>{match.venue}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;