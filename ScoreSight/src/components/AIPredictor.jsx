import React, { useState } from 'react';
import { AlertCircle, TrendingUp } from 'lucide-react';

const AIPredictor = () => {
  const [formData, setFormData] = useState({
    homeTeam: '',
    awayTeam: '',
    matchDate: ''
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const teams = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brighton', 'Burnley',
    'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leicester',
    'Liverpool', 'Man City', 'Man United', 'Newcastle', 'Norwich',
    'Southampton', 'Tottenham', 'Watford', 'West Ham', 'Wolves'
  ];

  // API URL - change if your Flask server runs on different port
  const API_URL = 'http://localhost:5000';

  const testConnection = async () => {
    try {
      const response = await fetch(`${API_URL}/test`, {
        credentials: 'include' // Add this for session cookies
      });
      if (response.ok) {
        const data = await response.json();
        console.log('Server connection successful:', data);
        alert('Server connection successful!');
        return true;
      }
    } catch (err) {
      console.error('Server connection failed:', err);
      alert('Server connection failed. Make sure Flask is running on port 5000.');
    }
    return false;
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handlePredict = async () => {
    if (!formData.homeTeam || !formData.awayTeam) {
      setError('Please select both teams');
      return;
    }

    if (formData.homeTeam === formData.awayTeam) {
      setError('Home and Away teams must be different');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('Sending prediction request...');
      
      const response = await fetch(`${API_URL}/predict-ai-fixed`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        credentials: 'include', // CRITICAL: This sends session cookies
        body: JSON.stringify({
          HomeTeam: formData.homeTeam,
          AwayTeam: formData.awayTeam,
          Date: formData.matchDate || new Date().toISOString().split('T')[0]
        })
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        let errorMessage = `Server error: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorMessage;
        } catch (e) {
          errorMessage = response.statusText || errorMessage;
        }
        
        // Handle authentication error specifically
        if (response.status === 401) {
          errorMessage = 'Please login first to use the AI Predictor';
          // You could redirect to login page here
          // window.location.href = '/?login=true';
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Prediction result:', result);
      setPrediction(result);
      
    } catch (err) {
      console.error('Prediction error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getOutcomeColor = (outcome) => {
    if (outcome === 'Home Win') return 'text-green-400';
    if (outcome === 'Away Win') return 'text-red-400';
    return 'text-yellow-400';
  };

  const getConfidenceWidth = (confidence) => {
    return `${Math.min(100, Math.max(0, confidence))}%`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-cyan-400 mb-2">EPL Match Predictor</h1>
          <p className="text-slate-300">AI-Powered Match Outcome Prediction</p>
          
          {/* Test Connection Button */}
          <button
            onClick={testConnection}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
          >
            Test Server Connection
          </button>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Prediction Form */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl p-8 border border-slate-700 shadow-2xl">
            <h2 className="text-2xl font-bold text-cyan-400 mb-6 border-b-2 border-cyan-400 pb-2 inline-block">
              Predict Your Match
            </h2>

            <div className="space-y-6 mt-6">
              {/* Home Team */}
              <div>
                <label className="block text-slate-300 mb-2 font-medium">Home Team:</label>
                <select
                  name="homeTeam"
                  value={formData.homeTeam}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                >
                  <option value="">Select Home Team</option>
                  {teams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              {/* Away Team */}
              <div>
                <label className="block text-slate-300 mb-2 font-medium">Away Team:</label>
                <select
                  name="awayTeam"
                  value={formData.awayTeam}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                >
                  <option value="">Select Away Team</option>
                  {teams.map(team => (
                    <option key={team} value={team}>{team}</option>
                  ))}
                </select>
              </div>

              {/* Match Date */}
              <div>
                <label className="block text-slate-300 mb-2 font-medium">Match Date:</label>
                <input
                  type="date"
                  name="matchDate"
                  value={formData.matchDate}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                />
              </div>

              {/* Predict Button */}
              <button
                onClick={handlePredict}
                disabled={loading}
                className="w-full px-6 py-4 bg-cyan-500 hover:bg-cyan-600 text-white font-bold text-lg rounded-lg shadow-lg transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Analyzing...
                  </span>
                ) : (
                  'Predict Match Result'
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 flex items-center gap-3">
                  <AlertCircle className="text-red-400 flex-shrink-0" size={20} />
                  <div>
                    <p className="text-red-300 text-sm font-medium">Error</p>
                    <p className="text-red-300 text-sm">{error}</p>
                    <p className="text-red-300 text-xs mt-1">
                      {error.includes('login') ? (
                        'Please go back to the home page and login first.'
                      ) : (
                        'Make sure your Flask server is running: python app.py'
                      )}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Prediction Results */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl p-8 border border-slate-700 shadow-2xl">
            <h2 className="text-2xl font-bold text-cyan-400 mb-6 border-b-2 border-cyan-400 pb-2 inline-block">
              Prediction Result
            </h2>

            {prediction ? (
              <div className="space-y-6 mt-6">
                {/* Match Info */}
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <p className="text-slate-400 text-sm mb-1">Match:</p>
                  <p className="text-white font-bold text-lg">
                    {formData.homeTeam} vs {formData.awayTeam}
                  </p>
                  {formData.matchDate && (
                    <p className="text-cyan-400 text-sm mt-1">
                      Date: {new Date(formData.matchDate).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </p>
                  )}
                </div>

                {/* Predicted Outcome */}
                <div className="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 rounded-lg p-6 border border-cyan-500/30">
                  <p className="text-slate-400 text-sm mb-2">Predicted Outcome:</p>
                  <p className={`text-3xl font-bold ${getOutcomeColor(prediction.outcome)}`}>
                    {prediction.outcome}
                  </p>
                </div>

                {/* Prediction Confidence */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-slate-400 text-sm font-medium">Prediction Confidence:</p>
                    <p className="text-cyan-400 font-bold">{prediction.confidence}%</p>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-cyan-500 to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: getConfidenceWidth(prediction.confidence) }}
                    />
                  </div>
                </div>

                {/* Score Predictions */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Home Team Goals</p>
                    <p className="text-green-400 text-3xl font-bold">{prediction.homeGoals}</p>
                  </div>
                  <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Away Team Goals</p>
                    <p className="text-red-400 text-3xl font-bold">{prediction.awayGoals}</p>
                  </div>
                </div>

                {/* Points Prediction */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Home Points</p>
                    <p className="text-yellow-400 text-2xl font-bold">{prediction.homePoints}</p>
                  </div>
                  <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
                    <p className="text-slate-400 text-xs mb-1">Away Points</p>
                    <p className="text-purple-400 text-2xl font-bold">{prediction.awayPoints}</p>
                  </div>
                </div>

                {/* Goal Difference */}
                <div className="bg-slate-700/50 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="text-cyan-400" size={20} />
                    <span className="text-slate-300 font-medium">Goal Difference:</span>
                  </div>
                  <span className={`text-xl font-bold ${
                    prediction.goalDifference > 0 ? 'text-green-400' : 
                    prediction.goalDifference < 0 ? 'text-red-400' : 'text-yellow-400'
                  }`}>
                    {prediction.goalDifference > 0 ? '+' : ''}{prediction.goalDifference}
                  </span>
                </div>

                {/* Insights */}
                {prediction.insights && (
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <p className="text-slate-400 text-sm mb-2">Match Insights:</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="text-cyan-300">Home Form: {prediction.insights.homeForm}</div>
                      <div className="text-cyan-300">Away Form: {prediction.insights.awayForm}</div>
                      <div className="text-cyan-300">H2H Record: {prediction.insights.h2hRecord}</div>
                      <div className="text-cyan-300">Form Diff: {prediction.insights.formDifference}</div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-96 text-slate-500">
                <svg className="w-24 h-24 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-lg font-medium">No prediction yet</p>
                <p className="text-sm mt-2 text-center">Select teams and click predict to see results</p>
                <p className="text-xs mt-1 text-slate-600 text-center">Make sure you are logged in and Flask server is running</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          <p>© 2025 EPL Match Predictor. All rights reserved.</p>
          <p className="mt-1">Predictions based on historical data and team form analysis</p>
        </div>
      </div>
    </div>
  );
};

export default AIPredictor;