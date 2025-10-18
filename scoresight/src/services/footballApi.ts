const BACKEND_URL = 'http://localhost:8000';

// Generic API call function
const fetchFromAPI = async (endpoint: string) => {
  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Fetch Error:', error);
    throw error;
  }
};

// Specific API endpoints
export const footballAPI = {
  // Get current Premier League fixtures
  getFixtures: () => fetchFromAPI('/api/fixtures'),
  
  // Get all Premier League teams
  getTeams: () => fetchFromAPI('/api/teams'),
};

// Utility functions for data transformation
export const transformAPIData = {
  // Transform API team data to our format
  team: (apiTeam: any) => ({
    id: apiTeam.id,
    name: apiTeam.name,
    shortName: apiTeam.shortName,
    crest: apiTeam.crest,
  }),
  
  // Transform API match data to our format
  match: (apiMatch: any) => ({
    id: apiMatch.id,
    homeTeam: transformAPIData.team(apiMatch.homeTeam),
    awayTeam: transformAPIData.team(apiMatch.awayTeam),
    date: apiMatch.date,
    status: apiMatch.status,
    score: apiMatch.score,
    venue: apiMatch.venue,
    matchday: apiMatch.matchday,
  }),
};

export default footballAPI;