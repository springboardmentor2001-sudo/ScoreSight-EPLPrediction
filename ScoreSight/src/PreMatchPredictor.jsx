import React, { useState } from 'react';
import { Trophy, TrendingUp, Users, Calendar, Target, Loader, Star } from 'lucide-react';

const PreMatchPredictor = () => {
  const [predictionData, setPredictionData] = useState({
    HomeTeam: '',
    AwayTeam: '',
    Date: new Date().toISOString().split('T')[0]
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
    setPredictionData({ ...predictionData, [e.target.name]: e.target.value });
  };

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Validate required fields
      if (!predictionData.HomeTeam || !predictionData.AwayTeam) {
        throw new Error('Please select both Home and Away teams');
      }

      if (predictionData.HomeTeam === predictionData.AwayTeam) {
        throw new Error('Home and Away teams must be different');
      }

      // Send data to backend API
      const response = await fetch('http://localhost:5000/predict-prematch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(predictionData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed. Please try again.');
      }

      const result = await response.json();
      setPredictions(result);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getWinProbability = (outcome, homePoints, awayPoints) => {
    if (outcome === 'Home Win') return Math.round((homePoints / 3) * 100);
    if (outcome === 'Away Win') return Math.round((awayPoints / 3) * 100);
    return Math.round(((homePoints + awayPoints) / 6) * 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-blue-900 to-purple-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <Target className="text-yellow-400" size={48} />
            Pre-Match Predictor
          </h1>
          <p className="text-blue-200 text-lg">
            Predict match outcomes before kickoff using 5 years of historical data
          </p>
        </div>

        {/* Prediction Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20 mb-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <Calendar className="text-green-400" size={28} />
            Match Setup
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <label className="block text-green-200 mb-3 font-medium text-lg">Match Date</label>
              <input
                type="date"
                name="Date"
                value={predictionData.Date}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-green-200 focus:outline-none focus:ring-2 focus:ring-green-400 text-lg"
              />
            </div>

            <div>
              <label className="block text-green-200 mb-3 font-medium text-lg">Home Team</label>
              <select
                name="HomeTeam"
                value={predictionData.HomeTeam}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-green-400 text-lg"
              >
                <option value="" className="bg-gray-800">Select Home Team</option>
                {teams.map(team => (
                  <option key={`home-${team}`} value={team} className="bg-gray-800">{team}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-green-200 mb-3 font-medium text-lg">Away Team</label>
              <select
                name="AwayTeam"
                value={predictionData.AwayTeam}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-green-400 text-lg"
              >
                <option value="" className="bg-gray-800">Select Away Team</option>
                {teams.map(team => (
                  <option key={`away-${team}`} value={team} className="bg-gray-800">{team}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-8 bg-green-500/20 p-5 rounded-xl border border-green-400/30">
            <h3 className="text-green-200 font-semibold mb-3 text-lg flex items-center gap-2">
              <Users className="text-green-300" size={20} />
              How it works
            </h3>
            <p className="text-blue-200 text-sm">
              This predictor analyzes 5 years of historical EPL data including team form, head-to-head records, 
              home/away performance, and seasonal trends to forecast match outcomes before they begin.
            </p>
          </div>
        </div>

        {/* Predict Button */}
        <div className="text-center mb-6">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="px-12 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold text-xl rounded-full shadow-2xl hover:from-yellow-600 hover:to-orange-600 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 mx-auto"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={24} />
                Analyzing Historical Data...
              </>
            ) : (
              <>
                <TrendingUp size={24} />
                Predict Match Outcome
              </>
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/20 border-2 border-red-500 rounded-2xl p-4 mb-6 flex items-center gap-3 animate-pulse">
            <Target className="text-red-300" size={24} />
            <p className="text-red-200 font-medium">{error}</p>
          </div>
        )}

        {/* Predictions Display */}
        {predictions && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
            <h2 className="text-3xl font-bold text-white mb-6 text-center flex items-center justify-center gap-3">
              <Trophy className="text-yellow-400" size={32} />
              Prediction Results
            </h2>
            
            {/* Match Info */}
            <div className="text-center mb-8 bg-blue-500/20 rounded-xl p-4 border border-blue-400/30">
              <h3 className="text-2xl font-bold text-white">
                {predictionData.HomeTeam} vs {predictionData.AwayTeam}
              </h3>
              <p className="text-blue-200">Based on historical data analysis</p>
            </div>

            {/* Main Prediction Cards */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gradient-to-br from-green-500/30 to-blue-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium flex items-center gap-2">
                  <Target className="text-green-300" size={16} />
                  Predicted Outcome
                </p>
                <p className="text-4xl font-bold text-white">{predictions.outcome}</p>
                <div className="mt-3 bg-black/30 rounded-lg p-2">
                  <p className="text-green-200 text-sm">
                    Win Probability: <span className="text-white font-bold">{getWinProbability(predictions.outcome, predictions.homePoints, predictions.awayPoints)}%</span>
                  </p>
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium flex items-center gap-2">
                  <TrendingUp className="text-purple-300" size={16} />
                  Expected Goal Difference
                </p>
                <p className="text-4xl font-bold text-white">
                  {predictions.goalDifference > 0 ? '+' : ''}{predictions.goalDifference}
                </p>
                <p className="text-blue-200 text-sm mt-2">
                  {predictions.goalDifference > 0 ? 'Home team advantage' : 
                   predictions.goalDifference < 0 ? 'Away team advantage' : 'Evenly matched'}
                </p>
              </div>
            </div>

            {/* Points Prediction */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gradient-to-br from-yellow-500/30 to-orange-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium flex items-center gap-2">
                  <Star className="text-yellow-300" size={16} />
                  {predictionData.HomeTeam} Expected Points
                </p>
                <p className="text-4xl font-bold text-white">{predictions.homePoints}</p>
                <p className="text-blue-200 text-sm mt-2">
                  {predictions.homePoints === 3 ? 'Strong favorite to win' :
                   predictions.homePoints === 1 ? 'Likely to draw' : 'Underdog in this match'}
                </p>
              </div>
              
              <div className="bg-gradient-to-br from-red-500/30 to-pink-500/30 rounded-xl p-6 border border-white/30 transform hover:scale-105 transition-transform">
                <p className="text-blue-200 text-sm mb-2 font-medium flex items-center gap-2">
                  <Star className="text-red-300" size={16} />
                  {predictionData.AwayTeam} Expected Points
                </p>
                <p className="text-4xl font-bold text-white">{predictions.awayPoints}</p>
                <p className="text-blue-200 text-sm mt-2">
                  {predictions.awayPoints === 3 ? 'Strong favorite to win' :
                   predictions.awayPoints === 1 ? 'Likely to draw' : 'Underdog in this match'}
                </p>
              </div>
            </div>

            {/* Additional Insights */}
            {predictions.insights && (
              <div className="mt-6 grid md:grid-cols-2 gap-4">
                {predictions.insights.homeAdvantage && (
                  <div className="bg-indigo-500/20 rounded-xl p-4 border border-indigo-400/30">
                    <h4 className="text-green-200 font-semibold mb-2">🏠 Home Advantage</h4>
                    <p className="text-white text-sm">{predictions.insights.homeAdvantage}</p>
                  </div>
                )}
                {predictions.insights.h2hRecord && (
                  <div className="bg-teal-500/20 rounded-xl p-4 border border-teal-400/30">
                    <h4 className="text-green-200 font-semibold mb-2">📊 Head-to-Head</h4>
                    <p className="text-white text-sm">{predictions.insights.h2hRecord}</p>
                  </div>
                )}
              </div>
            )}

            {/* Confidence and Method */}
            <div className="mt-6 text-center bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-xl p-4 border border-indigo-400/30">
              <p className="text-blue-200">
                Model Confidence: <span className="text-white font-bold text-2xl">{predictions.confidence}%</span>
              </p>
              <p className="text-green-200 text-sm mt-2">
                {predictions.predictionMethod} • Based on 5 years of EPL historical data
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PreMatchPredictor;