import { MatchPrediction, Team } from '../types';

export const mockTeams: Team[] = [
  { id: 1, name: 'Manchester United', shortName: 'MUN', crest: '🔴' },
  { id: 2, name: 'Manchester City', shortName: 'MCI', crest: '🔵' },
  { id: 3, name: 'Liverpool', shortName: 'LIV', crest: '🔴' },
  { id: 4, name: 'Chelsea', shortName: 'CHE', crest: '🔵' },
  { id: 5, name: 'Arsenal', shortName: 'ARS', crest: '🔴' },
  { id: 6, name: 'Tottenham Hotspur', shortName: 'TOT', crest: '⚪' },
  { id: 7, name: 'Newcastle United', shortName: 'NEW', crest: '⚫' },
  { id: 8, name: 'Brighton', shortName: 'BHA', crest: '🔵' },
];

export const featuredMatches = [
  {
    id: 1,
    homeTeam: mockTeams[0], // MUN
    awayTeam: mockTeams[1], // MCI
    date: '2024-01-15T15:00:00',
    homeWinProbability: 0.35,
    drawProbability: 0.25,
    awayWinProbability: 0.40,
    predictedScore: '1-1',
    confidence: 'high',
    keyFactors: [
      'City unbeaten in last 5 away matches',
      'United strong home record (W4 D1 L0)',
      'Historical: 4 draws in last 6 meetings'
    ],
    venue: 'Old Trafford',
    betRecommendation: 'BOTH TEAMS TO SCORE'
  },
  {
    id: 2,
    homeTeam: mockTeams[2], // LIV
    awayTeam: mockTeams[3], // CHE
    date: '2024-01-16T17:30:00',
    homeWinProbability: 0.65,
    drawProbability: 0.20,
    awayWinProbability: 0.15,
    predictedScore: '2-0',
    confidence: 'high',
    keyFactors: [
      'Liverpool unbeaten at Anfield this season',
      'Chelsea 1 win in last 5 away matches',
      'Anfield crowd advantage significant'
    ],
    venue: 'Anfield',
    betRecommendation: 'HOME WIN'
  },
  {
    id: 3,
    homeTeam: mockTeams[4], // ARS
    awayTeam: mockTeams[5], // TOT
    date: '2024-01-17T12:30:00',
    homeWinProbability: 0.55,
    drawProbability: 0.30,
    awayWinProbability: 0.15,
    predictedScore: '2-1',
    confidence: 'medium',
    keyFactors: [
      'Arsenal home dominance (W5 D0 L1)',
      'North London derby - high intensity expected',
      'Spurs defensive issues in away matches'
    ],
    venue: 'Emirates Stadium',
    betRecommendation: 'OVER 2.5 GOALS'
  },
  {
    id: 4,
    homeTeam: mockTeams[6], // NEW
    awayTeam: mockTeams[7], // BHA
    date: '2024-01-15T14:00:00',
    homeWinProbability: 0.48,
    drawProbability: 0.28,
    awayWinProbability: 0.24,
    predictedScore: '2-1',
    confidence: 'medium',
    keyFactors: [
      'Newcastle strong home form',
      'Brighton struggling away',
      'Both teams scoring in last 3 meetings'
    ],
    venue: 'St. James Park',
    betRecommendation: 'HOME WIN & BTTS'
  }
];

export const mockPredictions = featuredMatches;