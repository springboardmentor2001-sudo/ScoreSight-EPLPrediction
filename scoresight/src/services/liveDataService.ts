import { footballAPI, transformAPIData } from './footballApi';

// Service with proper error handling
export const liveDataService = {
  // Get all teams
  async getTeams() {
    try {
      const data = await footballAPI.getTeams();
      return data.teams.map(transformAPIData.team);
    } catch (error) {
      console.error('Error fetching teams:', error);
      // Return empty array instead of mock data
      return [];
    }
  },

  // Get current fixtures
  async getFixtures() {
    try {
      const data = await footballAPI.getFixtures();
      console.log('Real API data:', data); // Debug
      return data.matches ? data.matches.map(transformAPIData.match) : [];
    } catch (error) {
      console.error('Error fetching fixtures:', error);
      // Return empty array instead of mock data
      return [];
    }
  },
};

export default liveDataService;