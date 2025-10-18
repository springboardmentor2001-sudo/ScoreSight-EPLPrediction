import { footballAPI, transformAPIData } from './footballApi';

// Service with fallback to mock data if API fails
export const liveDataService = {
  // Get all teams with fallback
  async getTeams() {
    try {
      const data = await footballAPI.getTeams();
      return data.teams.map(transformAPIData.team);
    } catch (error) {
      console.warn('Using mock teams data due to API error');
      // Fallback to mock data
      const { mockTeams } = await import('./mockData');
      return mockTeams;
    }
  },

  // Get current fixtures with fallback
  async getFixtures() {
    try {
      const data = await footballAPI.getFixtures();
      console.log('Real API data:', data); // Debug
      return data.matches ? data.matches.map(transformAPIData.match) : [];
    } catch (error) {
      console.warn('Using mock fixtures data due to API error');
      // Fallback to mock data - return the actual mock data
      const { featuredMatches } = await import('./mockData');
      return featuredMatches;
    }
  },

  // Remove getStandings, getTeamWithMatches methods since they're not in the new API
};

export default liveDataService;