import React, { useState, useEffect } from 'react';
import { Calendar, ArrowLeft, Search, Filter } from 'lucide-react';

const Matches = ({ onNavigate }) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

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
    'Newcastle United': 'https://upload.wikimedia.org/wikipedia/sco/5/56/Newcastle_United_Logo.svg',
    'Nottingham Forest': 'https://upload.wikimedia.org/wikipedia/en/e/e5/Nottingham_Forest_F.C._logo.svg',
    'Southampton': 'https://upload.wikimedia.org/wikipedia/en/c/c9/FC_Southampton.svg',
    'Tottenham': 'https://cdn.freebiesupply.com/logos/large/2x/tottenham-hotspur-logo-black-and-white.png',
    'West Ham': 'https://upload.wikimedia.org/wikipedia/en/c/c2/West_Ham_United_FC_logo.svg',
    'Wolverhampton': 'https://upload.wikimedia.org/wikipedia/en/f/fc/Wolverhampton_Wanderers.svg'
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
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
        setMatches(data.matches);
      } else {
        setMatches(getSampleMatches());
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
      setMatches(getSampleMatches());
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

  const filteredMatches = matches.filter(match => 
    match.home_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
    match.away_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
    match.venue.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => onNavigate('home')}
              className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors bg-blue-500/20 hover:bg-blue-500/30 px-4 py-2 rounded-lg border border-blue-500/30"
            >
              <ArrowLeft className="h-5 w-5" />
              Back to Home
            </button>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <Calendar className="h-8 w-8 text-blue-400" />
              All Upcoming Matches
            </h1>
          </div>
          <div className="text-blue-400 text-sm font-medium bg-blue-500/20 px-3 py-1 rounded-full">
            {matches.length} matches
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-8">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-blue-200" />
              <input
                type="text"
                placeholder="Search matches by team or venue..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
              />
            </div>
            <button className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors bg-blue-500/20 hover:bg-blue-500/30 px-4 py-3 rounded-lg border border-blue-500/30">
              <Filter className="h-5 w-5" />
              Filter
            </button>
          </div>
        </div>

        {/* Matches List */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          {loading ? (
            <div className="text-center py-12">
              <div className="text-blue-200 text-lg">Loading matches...</div>
            </div>
          ) : (
            <>
              {filteredMatches.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-blue-200 text-lg">No matches found</div>
                  <p className="text-blue-300 mt-2">Try adjusting your search terms</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredMatches.map((match, index) => (
                    <div
                      key={match.id}
                      className={`bg-gradient-to-r ${getMatchCardColor(index)} rounded-xl p-6 border border-white/20 hover:border-white/40 transition-all duration-300 w-full`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3 flex-1">
                              {premierLeagueTeams[match.home_team] && (
                                <img 
                                  src={premierLeagueTeams[match.home_team]} 
                                  alt={match.home_team}
                                  className="w-8 h-8 object-contain"
                                />
                              )}
                              <span className="text-white font-semibold text-lg">{match.home_team}</span>
                            </div>
                            
                            <div className="flex flex-col items-center mx-4">
                              <span className="text-blue-200 text-sm">VS</span>
                              <span className="text-blue-300 text-xs mt-1 bg-black/30 px-2 py-1 rounded">
                                {match.date}
                              </span>
                            </div>
                            
                            <div className="flex items-center gap-3 flex-1 justify-end">
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
                            <div className="flex items-center gap-4">
                              <span>{match.time}</span>
                              <span className="text-blue-300">•</span>
                              <span>{match.venue}</span>
                            </div>
                            <span className="text-blue-300 bg-black/30 px-2 py-1 rounded">
                              Match #{match.id}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Matches;