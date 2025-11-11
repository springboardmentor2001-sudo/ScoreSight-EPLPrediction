import React, { useState } from 'react';
import { 
  Trophy, 
  AlertCircle, 
  Loader, 
  Calendar, 
  Users, 
  Target, 
  Crosshair, 
  CornerDownRight, 
  Shield,
  Square
} from 'lucide-react';

const UserInputPredict = () => {
  const [matchData, setMatchData] = useState({
    Date: '',
    HomeTeam: '',
    AwayTeam: '',
    HTHG: '',
    HTAG: '',
    HS: '',
    AS: '',
    HST: '',
    AST: '',
    HC: '',
    AC: '',
    HF: '',
    AF: '',
    HY: '',
    AY: '',
    HR: '',
    AR: ''
  });

  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const teams = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brighton', 'Burnley',
    'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leicester',
    'Liverpool', 'Man City', 'Man United', 'Newcastle', 'Norwich',
    'Southampton', 'Tottenham', 'Watford', 'West Ham', 'Wolves'
  ];

  const handleChange = (e) => {
    setMatchData({ ...matchData, [e.target.name]: e.target.value });
  };

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    
    try {
      if (!matchData.HomeTeam || !matchData.AwayTeam) {
        throw new Error('Please select both Home and Away teams');
      }

      if (matchData.HomeTeam === matchData.AwayTeam) {
        throw new Error('Home and Away teams must be different');
      }

      // Use the correct endpoint and include credentials
      const response = await fetch('http://localhost:5000/predict-ai-fixed', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for session cookies
        body: JSON.stringify({
          HomeTeam: matchData.HomeTeam,
          AwayTeam: matchData.AwayTeam,
          Date: matchData.Date || new Date().toISOString().split('T')[0]
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        let errorMessage = 'Prediction failed. Please check your input and try again.';
        
        if (response.status === 401) {
          errorMessage = 'Please login first to use the prediction feature.';
        } else {
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch (e) {
            // If we can't parse JSON error, use status text
            errorMessage = response.statusText || errorMessage;
          }
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Prediction result:', result);
      setPredictions(result);
      
    } catch (err) {
      console.error('Prediction error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4 sm:p-6 w-full">
      <div className="w-full max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <Trophy className="text-yellow-400" size={48} />
            EPL Match Predictor
          </h1>
          <p className="text-blue-200 text-lg">Input match statistics for accurate predictions</p>
        </div>

        {/* Match Details Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 sm:p-8 shadow-2xl border border-white/20 mb-6 w-full">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <Calendar className="text-blue-400" size={28} />
            Match Details
          </h2>
          
          <div className="space-y-8">
            {/* Basic Match Info */}
            <div className="bg-blue-500/20 p-6 rounded-xl border border-blue-400/30">
              <h3 className="text-blue-200 font-semibold mb-4 text-lg flex items-center gap-2">
                <Users className="text-blue-300" size={20} />
                Basic Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-blue-200 mb-2 font-medium">Match Date</label>
                  <input
                    type="date"
                    name="Date"
                    value={matchData.Date}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  />
                </div>

                <div>
                  <label className="block text-blue-200 mb-2 font-medium">Home Team</label>
                  <select
                    name="HomeTeam"
                    value={matchData.HomeTeam}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
                  >
                    <option value="" className="bg-gray-800">Select Home Team</option>
                    {teams.map(team => (
                      <option key={`home-${team}`} value={team} className="bg-gray-800">{team}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-blue-200 mb-2 font-medium">Away Team</label>
                  <select
                    name="AwayTeam"
                    value={matchData.AwayTeam}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
                  >
                    <option value="" className="bg-gray-800">Select Away Team</option>
                    {teams.map(team => (
                      <option key={`away-${team}`} value={team} className="bg-gray-800">{team}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Half-Time Statistics */}
            <div className="bg-green-500/20 p-6 rounded-xl border border-green-400/30">
              <h3 className="text-green-200 font-semibold mb-4 text-lg flex items-center gap-2">
                <Target className="text-green-300" size={20} />
                Half-Time Statistics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-blue-200 mb-2">Home Goals (Half-Time)</label>
                  <input
                    type="number"
                    name="HTHG"
                    value={matchData.HTHG}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                    placeholder="0"
                    min="0"
                    max="10"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Away Goals (Half-Time)</label>
                  <input
                    type="number"
                    name="HTAG"
                    value={matchData.HTAG}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                    placeholder="0"
                    min="0"
                    max="10"
                  />
                </div>
              </div>
            </div>

            {/* Shots Statistics */}
            <div className="bg-purple-500/20 p-6 rounded-xl border border-purple-400/30">
              <h3 className="text-purple-200 font-semibold mb-4 text-lg flex items-center gap-2">
                <Crosshair className="text-purple-300" size={20} />
                Shots Statistics
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-blue-200 mb-2">Home Shots</label>
                  <input
                    type="number"
                    name="HS"
                    value={matchData.HS}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                    placeholder="0"
                    min="0"
                    max="50"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Away Shots</label>
                  <input
                    type="number"
                    name="AS"
                    value={matchData.AS}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                    placeholder="0"
                    min="0"
                    max="50"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Home Shots on Target</label>
                  <input
                    type="number"
                    name="HST"
                    value={matchData.HST}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                    placeholder="0"
                    min="0"
                    max="50"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Away Shots on Target</label>
                  <input
                    type="number"
                    name="AST"
                    value={matchData.AST}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                    placeholder="0"
                    min="0"
                    max="50"
                  />
                </div>
              </div>
            </div>

            {/* Corners and Fouls */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Corners */}
              <div className="bg-yellow-500/20 p-6 rounded-xl border border-yellow-400/30">
                <h3 className="text-yellow-200 font-semibold mb-4 text-lg flex items-center gap-2">
                  <CornerDownRight className="text-yellow-300" size={20} />
                  Corners
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-blue-200 mb-2">Home Corners</label>
                    <input
                      type="number"
                      name="HC"
                      value={matchData.HC}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                      placeholder="0"
                      min="0"
                      max="20"
                    />
                  </div>
                  <div>
                    <label className="block text-blue-200 mb-2">Away Corners</label>
                    <input
                      type="number"
                      name="AC"
                      value={matchData.AC}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                      placeholder="0"
                      min="0"
                      max="20"
                    />
                  </div>
                </div>
              </div>

              {/* Fouls */}
              <div className="bg-orange-500/20 p-6 rounded-xl border border-orange-400/30">
                <h3 className="text-orange-200 font-semibold mb-4 text-lg flex items-center gap-2">
                  <Shield className="text-orange-300" size={20} />
                  Fouls
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-blue-200 mb-2">Home Fouls</label>
                    <input
                      type="number"
                      name="HF"
                      value={matchData.HF}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-orange-400"
                      placeholder="0"
                      min="0"
                      max="30"
                    />
                  </div>
                  <div>
                    <label className="block text-blue-200 mb-2">Away Fouls</label>
                    <input
                      type="number"
                      name="AF"
                      value={matchData.AF}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-orange-400"
                      placeholder="0"
                      min="0"
                      max="30"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Cards */}
            <div className="bg-red-500/20 p-6 rounded-xl border border-red-400/30">
              <h3 className="text-red-200 font-semibold mb-4 text-lg flex items-center gap-2">
                <Square className="text-red-300" size={20} />
                Cards
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-blue-200 mb-2">Home Yellow Cards</label>
                  <input
                    type="number"
                    name="HY"
                    value={matchData.HY}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                    placeholder="0"
                    min="0"
                    max="10"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Away Yellow Cards</label>
                  <input
                    type="number"
                    name="AY"
                    value={matchData.AY}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                    placeholder="0"
                    min="0"
                    max="10"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Home Red Cards</label>
                  <input
                    type="number"
                    name="HR"
                    value={matchData.HR}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                    placeholder="0"
                    min="0"
                    max="5"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-2">Away Red Cards</label>
                  <input
                    type="number"
                    name="AR"
                    value={matchData.AR}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                    placeholder="0"
                    min="0"
                    max="5"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Predict Button */}
        <div className="text-center mb-6">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="px-8 sm:px-12 py-4 bg-gradient-to-r from-green-500 to-blue-500 text-white font-bold text-lg sm:text-xl rounded-full shadow-2xl hover:from-green-600 hover:to-blue-600 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 mx-auto"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={24} />
                Analyzing Match Data...
              </>
            ) : (
              'Predict Match Outcome'
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/20 border-2 border-red-500 rounded-2xl p-4 mb-6 flex items-center gap-3 animate-pulse w-full">
            <AlertCircle className="text-red-300" size={24} />
            <div>
              <p className="text-red-200 font-medium">{error}</p>
              {error.includes('login') && (
                <p className="text-red-300 text-sm mt-1">Please make sure you are logged in.</p>
              )}
            </div>
          </div>
        )}

        {/* Predictions Display */}
        {predictions && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 sm:p-8 shadow-2xl border border-white/20 w-full">
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Match Predictions</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gradient-to-br from-green-500/30 to-blue-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium">Match Outcome</p>
                <p className="text-4xl font-bold text-white">{predictions.outcome}</p>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium">Goal Difference</p>
                <p className="text-4xl font-bold text-white">
                  {predictions.goalDifference > 0 ? '+' : ''}{predictions.goalDifference}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-yellow-500/30 to-orange-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium">Home Team Points</p>
                <p className="text-4xl font-bold text-white">{predictions.homePoints}</p>
              </div>
              
              <div className="bg-gradient-to-br from-red-500/30 to-pink-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium">Away Team Points</p>
                <p className="text-4xl font-bold text-white">{predictions.awayPoints}</p>
              </div>
            </div>

            {/* Score Prediction */}
            <div className="mt-6 text-center bg-indigo-500/20 rounded-xl p-6 border border-indigo-400/30">
              <p className="text-blue-200 text-lg mb-2">Predicted Score</p>
              <p className="text-5xl font-bold text-white">
                {predictions.homeGoals} - {predictions.awayGoals}
              </p>
            </div>

            {predictions.confidence && (
              <div className="mt-6 text-center bg-green-500/20 rounded-xl p-4 border border-green-400/30">
                <p className="text-blue-200">Model Confidence: <span className="text-white font-bold text-2xl">{predictions.confidence}%</span></p>
              </div>
            )}

            {predictions.insights && (
              <div className="mt-6 bg-slate-700/30 rounded-xl p-6 border border-slate-600/30">
                <h3 className="text-white font-bold text-xl mb-4">Match Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="text-cyan-300">Home Form: {predictions.insights.homeForm}</div>
                  <div className="text-cyan-300">Away Form: {predictions.insights.awayForm}</div>
                  <div className="text-cyan-300">H2H Record: {predictions.insights.h2hRecord}</div>
                  <div className="text-cyan-300">Form Difference: {predictions.insights.formDifference}</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserInputPredict;