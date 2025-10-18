export interface Team {
  id: number;
  name: string;
  shortName: string;
  crest: string;
}

export interface MatchPrediction {
  id: number;
  homeTeam: Team;
  awayTeam: Team;
  date: string;
  homeWinProbability: number;
  drawProbability: number;
  awayWinProbability: number;
  predictedScore: string;
  confidence: 'high' | 'medium' | 'low';
  keyFactors: string[];
}

export interface FormIndicator {
  teamId: number;
  form: string[]; // ['W', 'L', 'D', 'W', 'W']
  goalsFor: number;
  goalsAgainst: number;
}