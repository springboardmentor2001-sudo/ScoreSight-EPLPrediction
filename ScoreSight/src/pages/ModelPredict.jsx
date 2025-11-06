import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar, Target, Star, Loader, Trophy, Users, Zap, AlertCircle } from 'lucide-react';

const ModelPredict = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedMatch, setSelectedMatch] = useState(null);

  useEffect(() => {
    fetchModelPredictions();
  }, []);

  const fetchModelPredictions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/predict/model', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPredictions(data.predictions);
        if (data.predictions.length > 0) {
          setSelectedMatch(data.predictions[0]);
        }
      } else {
        setError('Failed to fetch predictions');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getOutcomeColor = (outcome) => {
    switch (outcome) {
      case 'Home Win': return '#10B981'; // green
      case 'Away Win': return '#EF4444'; // red
      case 'Draw': return '#F59E0B'; // yellow
      default: return '#6B7280'; // gray
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return '#10B981'; // green
    if (confidence >= 60) return '#F59E0B'; // yellow
    return '#EF4444'; // red
  };

  // Prepare data for charts
  const outcomeData = predictions.reduce((acc, prediction) => {
    const outcome = prediction.predicted_outcome;
    acc[outcome] = (acc[outcome] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(outcomeData).map(([outcome, count]) => ({
    name: outcome,
    value: count,
    color: getOutcomeColor(outcome)
  }));

  const confidenceData = predictions.map((prediction, index) => ({
    name: `${prediction.home_team} vs ${prediction.away_team}`,
    confidence: prediction.confidence,
    fill: getConfidenceColor(prediction.confidence)
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  // Calculate summary statistics
  const totalPredictions = predictions.length;
  const avgConfidence = predictions.length > 0 
    ? Math.round(predictions.reduce((acc, p) => acc + p.confidence, 0) / predictions.length)
    : 0;
  const homeWins = predictions.filter(p => p.predicted_outcome === 'Home Win').length;
  const awayWins = predictions.filter(p => p.predicted_outcome === 'Away Win').length;
  const draws = predictions.filter(p => p.predicted_outcome === 'Draw').length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-12 w-12 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-white text-xl">Loading AI predictions...</p>
          <p className="text-blue-200 text-sm mt-2">Analyzing historical data and team performance</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-400 text-xl mb-2">{error}</p>
          <button
            onClick={fetchModelPredictions}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-blue-900 to-purple-900 p-4 sm:p-6 w-full">
      <div className="w-full max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 flex items-center justify-center gap-3">
            <TrendingUp className="h-8 w-8 text-green-400" />
            AI Model Predictions
          </h1>
          <p className="text-xl text-blue-200 max-w-2xl mx-auto">
            Machine learning predictions for upcoming Premier League matches based on historical data analysis
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-500/20 rounded-2xl p-6 border border-blue-400/30 text-center">
            <Trophy className="h-8 w-8 text-blue-400 mx-auto mb-2" />
            <p className="text-blue-200 text-sm">Total Predictions</p>
            <p className="text-white text-2xl font-bold">{totalPredictions}</p>
          </div>
          <div className="bg-green-500/20 rounded-2xl p-6 border border-green-400/30 text-center">
            <Zap className="h-8 w-8 text-green-400 mx-auto mb-2" />
            <p className="text-green-200 text-sm">Avg Confidence</p>
            <p className="text-white text-2xl font-bold">{avgConfidence}%</p>
          </div>
          <div className="bg-purple-500/20 rounded-2xl p-6 border border-purple-400/30 text-center">
            <Users className="h-8 w-8 text-purple-400 mx-auto mb-2" />
            <p className="text-purple-200 text-sm">Home Wins</p>
            <p className="text-white text-2xl font-bold">{homeWins}</p>
          </div>
          <div className="bg-yellow-500/20 rounded-2xl p-6 border border-yellow-400/30 text-center">
            <Star className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
            <p className="text-yellow-200 text-sm">Draws</p>
            <p className="text-white text-2xl font-bold">{draws}</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Predictions List - Left Column */}
          <div className="xl:col-span-2 space-y-6">
            <h2 className="text-2xl font-bold text-white mb-4">Upcoming Match Predictions</h2>
            
            {predictions.map((prediction, index) => (
              <div
                key={prediction.match_id}
                onClick={() => setSelectedMatch(prediction)}
                className={`bg-white/10 backdrop-blur-lg rounded-2xl p-6 border-2 transition-all duration-300 cursor-pointer hover:scale-105 ${
                  selectedMatch?.match_id === prediction.match_id 
                    ? 'border-green-400 shadow-2xl' 
                    : 'border-white/20 hover:border-white/40'
                }`}
              >
                {/* Match Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-blue-400" />
                    <span className="text-blue-200 text-sm">{prediction.date}</span>
                    <span className="text-blue-200">•</span>
                    <span className="text-blue-200 text-sm">{prediction.venue}</span>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    prediction.predicted_outcome === 'Home Win' ? 'bg-green-500/20 text-green-300 border border-green-400' :
                    prediction.predicted_outcome === 'Away Win' ? 'bg-red-500/20 text-red-300 border border-red-400' :
                    'bg-yellow-500/20 text-yellow-300 border border-yellow-400'
                  }`}>
                    {prediction.predicted_outcome}
                  </div>
                </div>

                {/* Teams and Score Prediction */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-center flex-1">
                    <p className="text-white font-bold text-lg mb-1">{prediction.home_team}</p>
                    <div className="bg-green-500/20 rounded-lg px-3 py-1 inline-block">
                      <p className="text-green-300 text-sm font-medium">{prediction.home_points} pts</p>
                    </div>
                  </div>

                  <div className="text-center mx-4">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl px-6 py-3 shadow-2xl">
                      <p className="text-white font-bold text-2xl">
                        {prediction.predicted_goal_difference > 0 ? '+' : ''}{prediction.predicted_goal_difference}
                      </p>
                      <p className="text-blue-200 text-xs">Goal Diff</p>
                    </div>
                    <p className="text-blue-200 text-xs mt-1">Predicted</p>
                  </div>

                  <div className="text-center flex-1">
                    <p className="text-white font-bold text-lg mb-1">{prediction.away_team}</p>
                    <div className="bg-green-500/20 rounded-lg px-3 py-1 inline-block">
                      <p className="text-green-300 text-sm font-medium">{prediction.away_points} pts</p>
                    </div>
                  </div>
                </div>

                {/* Confidence Meter */}
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-200 text-sm flex items-center gap-2">
                      <Target className="h-4 w-4" />
                      Model Confidence
                    </span>
                    <span 
                      className="text-sm font-bold"
                      style={{ color: getConfidenceColor(prediction.confidence) }}
                    >
                      {prediction.confidence}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div
                      className="h-3 rounded-full transition-all duration-1000"
                      style={{
                        width: `${prediction.confidence}%`,
                        backgroundColor: getConfidenceColor(prediction.confidence)
                      }}
                    ></div>
                  </div>
                </div>

                {/* Quick Insights */}
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div className="bg-blue-500/20 rounded-lg p-2">
                    <p className="text-blue-200 text-xs">Home Advantage</p>
                    <p className="text-white text-sm font-medium">Strong</p>
                  </div>
                  <div className="bg-purple-500/20 rounded-lg p-2">
                    <p className="text-purple-200 text-xs">Recent Form</p>
                    <p className="text-white text-sm font-medium">Positive</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Analytics Sidebar - Right Column */}
          <div className="space-y-8">
            {/* Selected Match Details */}
            {selectedMatch && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-400" />
                  Match Analysis
                </h3>
                
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-white font-bold text-lg">{selectedMatch.home_team} vs {selectedMatch.away_team}</p>
                    <p className="text-blue-200 text-sm">{selectedMatch.date} • {selectedMatch.venue}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div className="bg-green-500/20 rounded-lg p-3">
                      <p className="text-green-200 text-xs">Predicted Outcome</p>
                      <p className="text-white font-bold text-lg">{selectedMatch.predicted_outcome}</p>
                    </div>
                    <div className="bg-blue-500/20 rounded-lg p-3">
                      <p className="text-blue-200 text-xs">Goal Difference</p>
                      <p className="text-white font-bold text-lg">
                        {selectedMatch.predicted_goal_difference > 0 ? '+' : ''}{selectedMatch.predicted_goal_difference}
                      </p>
                    </div>
                  </div>

                  <div className="bg-purple-500/20 rounded-lg p-4">
                    <p className="text-purple-200 text-sm mb-2">Key Factors</p>
                    <ul className="text-white text-sm space-y-1">
                      <li>• Historical performance analysis</li>
                      <li>• Head-to-head record</li>
                      <li>• Recent team form</li>
                      <li>• Home/away advantage</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Outcome Distribution Chart */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">Prediction Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value) => [`${value} matches`, 'Count']}
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Confidence Levels Chart */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">Confidence Levels</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={confidenceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="name" 
                      stroke="#9CA3AF"
                      fontSize={12}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      domain={[0, 100]}
                    />
                    <Tooltip 
                      formatter={(value) => [`${value}%`, 'Confidence']}
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                    />
                    <Bar 
                      dataKey="confidence" 
                      fill="#3B82F6"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Model Information */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-400" />
                About Our Model
              </h3>
              <div className="text-blue-200 text-sm space-y-2">
                <p>Our AI model analyzes:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>5 years of historical EPL data</li>
                  <li>Team form and performance metrics</li>
                  <li>Head-to-head records</li>
                  <li>Home/away advantage factors</li>
                  <li>Player statistics and injuries</li>
                </ul>
                <p className="text-green-300 font-medium mt-3">
                  Current Accuracy: 75% across all predictions
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Refresh Button */}
        <div className="text-center mt-8">
          <button
            onClick={fetchModelPredictions}
            disabled={loading}
            className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white px-8 py-3 rounded-full font-bold transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Refreshing...' : 'Refresh Predictions'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModelPredict;