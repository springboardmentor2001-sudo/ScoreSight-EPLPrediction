from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime, timedelta
import pickle
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from xgboost import XGBClassifier
from typing import Dict, List, Any
import re
from dotenv import load_dotenv
from fastapi import APIRouter
from news_service import news_service


# Load environment variables from .env file
load_dotenv()

# Get the correct paths to model files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_MODELS_DIR = os.path.join(BASE_DIR, '..', 'ml-models')

# =============================================================================
# CORE FUNCTIONS THAT MUST COME FIRST
# =============================================================================

def get_all_trained_teams():
    """Return a canonical list of teams used for mapping and sample data."""
    return [
        'Arsenal', 'Aston Villa', 'Birmingham', 'Blackburn', 'Blackpool',
        'Bolton', 'Bournemouth', 'Bradford', 'Brentford', 'Brighton',
        'Burnley', 'Cardiff', 'Charlton', 'Chelsea', 'Coventry', 
        'Crystal Palace', 'Derby', 'Everton', 'Fulham', 'Huddersfield',
        'Hull', 'Ipswich', 'Leeds', 'Leicester', 'Liverpool',
        'Man City', 'Man United', 'Middlesbrough', 'Newcastle', 'Norwich',
        'Portsmouth', 'QPR', 'Reading', 'Sheffield United', 'Southampton',
        'Stoke', 'Sunderland', 'Swansea', 'Tottenham', 'Watford',
        'West Brom', 'West Ham', 'Wigan', 'Wolves', "Nott'm Forest"
    ]


def enhanced_map_team_name(api_team_name):
    """Comprehensive team mapping for all Premier League team variations"""
    
    # Complete mapping dictionary - covers all API variations
    team_mapping = {
        # Arsenal
        'Arsenal FC': 'Arsenal', 'Arsenal': 'Arsenal',
        
        # Aston Villa
        'Aston Villa FC': 'Aston Villa', 'Aston Villa': 'Aston Villa',
        
        # Bournemouth
        'AFC Bournemouth': 'Bournemouth', 'Bournemouth': 'Bournemouth',
        
        # Brentford
        'Brentford FC': 'Brentford', 'Brentford': 'Brentford',
        
        # Brighton
        'Brighton & Hove Albion FC': 'Brighton', 'Brighton and Hove Albion': 'Brighton', 
        'Brighton': 'Brighton',
        
        # Burnley
        'Burnley FC': 'Burnley', 'Burnley': 'Burnley',
        
        # Chelsea
        'Chelsea FC': 'Chelsea', 'Chelsea': 'Chelsea',
        
        # Crystal Palace
        'Crystal Palace FC': 'Crystal Palace', 'Crystal Palace': 'Crystal Palace',
        
        # Everton
        'Everton FC': 'Everton', 'Everton': 'Everton',
        
        # Fulham
        'Fulham FC': 'Fulham', 'Fulham': 'Fulham',
        
        # Liverpool
        'Liverpool FC': 'Liverpool', 'Liverpool': 'Liverpool',
        
        # Manchester City
        'Manchester City FC': 'Man City', 'Manchester City': 'Man City',
        
        # Manchester United
        'Manchester United FC': 'Man United', 'Manchester United': 'Man United',
        
        # Newcastle
        'Newcastle United FC': 'Newcastle', 'Newcastle United': 'Newcastle',
        'Newcastle': 'Newcastle',
        
        # Nottingham Forest
        'Nottingham Forest FC': "Nott'm Forest", 'Nottingham Forest': "Nott'm Forest",
        
        # Sheffield United
        'Sheffield United FC': 'Sheffield United', 'Sheffield United': 'Sheffield United',
        
        # Tottenham
        'Tottenham Hotspur FC': 'Tottenham', 'Tottenham Hotspur': 'Tottenham',
        'Tottenham': 'Tottenham',
        
        # West Ham
        'West Ham United FC': 'West Ham', 'West Ham United': 'West Ham',
        'West Ham': 'West Ham',
        
        # Wolves
        'Wolverhampton Wanderers FC': 'Wolves', 'Wolverhampton Wanderers': 'Wolves',
        'Wolves': 'Wolves',
        
        # Other teams
        'Leeds United': 'Leeds', 'Leeds United FC': 'Leeds',
        'Leicester City': 'Leicester', 'Leicester City FC': 'Leicester',
        'Southampton FC': 'Southampton', 'Southampton': 'Southampton',
        'Watford FC': 'Watford', 'Watford': 'Watford',
        'Norwich City': 'Norwich', 'Norwich City FC': 'Norwich',
        'Aston Villa FC': 'Aston Villa'
    }
    
    # Direct mapping lookup
    if api_team_name in team_mapping:
        mapped_name = team_mapping[api_team_name]
        print(f"✅ Team mapped: '{api_team_name}' -> '{mapped_name}'")
        return mapped_name
    
    # Try removing common suffixes
    clean_name = api_team_name
    suffixes = [' FC', ' United', ' City', ' & Hove Albion', ' and Hove Albion', ' Hotspur']
    for suffix in suffixes:
        if suffix in clean_name:
            clean_name = clean_name.replace(suffix, '')
    
    # Check if cleaned name exists in trained teams
    trained_teams = get_all_trained_teams()
    for team in trained_teams:
        if team.lower() == clean_name.lower():
            print(f"✅ Cleaned team mapped: '{api_team_name}' -> '{team}'")
            return team
    
    # Final fallback - return original name
    print(f"⚠️  Could not map team: '{api_team_name}'")
    return api_team_name

# =============================================================================
# LOAD ML MODELS
# =============================================================================

# Load your NEW ML models
try:
    # Load pre-match model and preprocessing
    pre_match_model_path = os.path.join(ML_MODELS_DIR, 'scoresight_ensemble_model.joblib')
    pre_match_preprocessing_path = os.path.join(ML_MODELS_DIR, 'scoresight_preprocessing.pkl')
    
    pre_match_model = joblib.load(pre_match_model_path)
    pre_match_preprocessing = joblib.load(pre_match_preprocessing_path)
    print("✅ Pre-match ML Model loaded successfully!")
    
    # Load half-time model and preprocessing  
    half_time_model_path = os.path.join(ML_MODELS_DIR, 'scoresight_halftime_model.joblib')
    half_time_preprocessing_path = os.path.join(ML_MODELS_DIR, 'scoresight_halftime_preprocessing.pkl')
    
    half_time_model = joblib.load(half_time_model_path)
    half_time_preprocessing = joblib.load(half_time_preprocessing_path)
    print("✅ Half-time ML Model loaded successfully!")
    
    # Store all models in one dictionary
    ml_models = {
        'pre_match_model': pre_match_model,
        'pre_match_preprocessing': pre_match_preprocessing,
        'half_time_model': half_time_model, 
        'half_time_preprocessing': half_time_preprocessing
    }
    
    print(f"✅ All models loaded from: {ML_MODELS_DIR}")
    
except Exception as e:
    print(f"❌ Error loading ML models: {e}")
    ml_models = None

# =============================================================================
# TEAM ANALYTICS ENGINE
# =============================================================================

class TeamAnalyzer:
    """Analyzes team performance using your historical EPL dataset"""
    
    def __init__(self):
        self.historical_data = None
        self.teams_stats = {}
        self.teams_form = {}
        self.load_historical_data()

    def get_all_trained_teams(self):
        """Get all unique teams from training data"""
        return [
            'Arsenal', 'Aston Villa', 'Birmingham', 'Blackburn', 'Blackpool',
            'Bolton', 'Bournemouth', 'Bradford', 'Brentford', 'Brighton',
            'Burnley', 'Cardiff', 'Charlton', 'Chelsea', 'Coventry', 
            'Crystal Palace', 'Derby', 'Everton', 'Fulham', 'Huddersfield',
            'Hull', 'Ipswich', 'Leeds', 'Leicester', 'Liverpool',
            'Man City', 'Man United', 'Middlesbrough', 'Newcastle', 'Norwich',
            'Portsmouth', 'QPR', 'Reading', 'Sheffield United', 'Southampton',
            'Stoke', 'Sunderland', 'Swansea', 'Tottenham', 'Watford',
            'West Brom', 'West Ham', 'Wigan', 'Wolves', "Nott'm Forest"
        ]
    
    def load_historical_data(self):
        """Load and process your historical EPL dataset from ml-models folder"""
        historical_data_path = os.path.join(ML_MODELS_DIR, 'epl_2010_2020_cleaned_dataset.csv')
        
        if os.path.exists(historical_data_path):
            try:
                self.historical_data = pd.read_csv(historical_data_path)
                print(f"✅ Loaded historical data from: {historical_data_path}")
                print(f"📊 Dataset shape: {self.historical_data.shape}")
                self.calculate_team_stats()
                self.calculate_team_form()
                return
            except Exception as e:
                print(f"❌ Error loading historical data: {e}")
        else:
            print(f"❌ Historical data file not found at: {historical_data_path}")
        
        # If no file found, create sample data
        print("🔄 Creating sample data for demonstration...")
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample historical data for demonstration"""
        sample_teams = get_all_trained_teams()
        
        for team in sample_teams:
            # Create realistic sample stats for each team
            self.teams_stats[team] = {
                'team_name': team,
                'total_matches': 380,
                'wins': np.random.randint(120, 200),
                'draws': np.random.randint(80, 120),
                'losses': np.random.randint(80, 140),
                'win_percentage': round(np.random.uniform(35, 55), 1),
                'goals_for': np.random.randint(400, 600),
                'goals_against': np.random.randint(350, 550),
                'goal_difference': np.random.randint(-50, 150),
                'avg_goals_for': round(np.random.uniform(1.2, 1.8), 2),
                'avg_goals_against': round(np.random.uniform(1.1, 1.7), 2),
                'clean_sheets': np.random.randint(40, 100),
                'total_points': np.random.randint(400, 600),
                'points_per_game': round(np.random.uniform(1.2, 1.6), 2),
                'recent_form': ['W', 'D', 'L', 'W', 'W'],
                'attack_strength': np.random.randint(60, 90),
                'defense_strength': np.random.randint(60, 90),
                'overall_strength': np.random.randint(65, 85),
                'home_record': {
                    'wins': np.random.randint(60, 100),
                    'draws': np.random.randint(30, 50),
                    'losses': np.random.randint(20, 40),
                    'goals_for': np.random.randint(200, 300),
                    'goals_against': np.random.randint(150, 250)
                },
                'away_record': {
                    'wins': np.random.randint(40, 80),
                    'draws': np.random.randint(30, 50),
                    'losses': np.random.randint(40, 80),
                    'goals_for': np.random.randint(150, 250),
                    'goals_against': np.random.randint(180, 280)
                }
            }
        
        print(f"✅ Created sample data for {len(self.teams_stats)} teams")
    
    def calculate_team_stats(self):
        """Calculate comprehensive statistics for all teams"""
        if self.historical_data is None:
            return
            
        all_teams = set(self.historical_data['HomeTeam'].unique()) | set(self.historical_data['AwayTeam'].unique())
        
        for team in all_teams:
            self.teams_stats[team] = self.calculate_single_team_stats(team)
        
        print(f"✅ Calculated stats for {len(self.teams_stats)} teams")
    
    def calculate_team_form(self):
        """Calculate recent form for all teams (last 5 matches)"""
        if self.historical_data is None:
            return
            
        all_teams = set(self.historical_data['HomeTeam'].unique()) | set(self.historical_data['AwayTeam'].unique())
        
        for team in all_teams:
            self.teams_form[team] = self.calculate_recent_form(team)
        
        print(f"✅ Calculated form for {len(self.teams_form)} teams")
    
    def calculate_recent_form(self, team_name: str, num_matches: int = 5) -> Dict[str, Any]:
        """Calculate recent form for a team"""
        recent_matches = self.get_recent_matches(team_name, num_matches)
        
        if not recent_matches:
            return {
                'form_points': 0,
                'avg_points': 0,
                'goals_for_avg': 0,
                'goals_against_avg': 0,
                'clean_sheets': 0
            }
        
        # Calculate form points
        form_points = 0
        goals_for = 0
        goals_against = 0
        clean_sheets = 0
        
        for match in recent_matches:
            if match['result'] == 'W':
                form_points += 3
            elif match['result'] == 'D':
                form_points += 1
            goals_for += match['goals_for']
            goals_against += match['goals_against']
            if match['goals_against'] == 0:
                clean_sheets += 1
        
        return {
            'form_points': form_points,
            'avg_points': form_points / len(recent_matches),
            'goals_for_avg': goals_for / len(recent_matches),
            'goals_against_avg': goals_against / len(recent_matches),
            'clean_sheets': clean_sheets
        }
    
    def calculate_single_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Calculate statistics for a single team"""
        # Get all matches for this team
        home_matches = self.historical_data[self.historical_data['HomeTeam'] == team_name]
        away_matches = self.historical_data[self.historical_data['AwayTeam'] == team_name]
        
        # Basic match counts
        total_matches = len(home_matches) + len(away_matches)
        if total_matches == 0:
            return {}
        
        # Results calculation
        home_wins = len(home_matches[home_matches['FTR'] == 'H'])
        home_draws = len(home_matches[home_matches['FTR'] == 'D'])
        home_losses = len(home_matches[home_matches['FTR'] == 'A'])
        
        away_wins = len(away_matches[away_matches['FTR'] == 'A'])
        away_draws = len(away_matches[away_matches['FTR'] == 'D'])
        away_losses = len(away_matches[away_matches['FTR'] == 'A'])
        
        total_wins = home_wins + away_wins
        total_draws = home_draws + away_draws
        total_losses = home_losses + away_losses
        
        # Goals calculation
        home_goals_for = home_matches['FTHG'].sum()
        home_goals_against = home_matches['FTAG'].sum()
        away_goals_for = away_matches['FTAG'].sum()
        away_goals_against = away_matches['FTHG'].sum()
        
        total_goals_for = home_goals_for + away_goals_for
        total_goals_against = home_goals_against + away_goals_against
        
        # Points calculation (3 for win, 1 for draw)
        total_points = (total_wins * 3) + total_draws
        points_per_game = total_points / total_matches
        
        # Win percentages
        win_percentage = (total_wins / total_matches) * 100
        home_win_percentage = (home_wins / len(home_matches)) * 100 if len(home_matches) > 0 else 0
        away_win_percentage = (away_wins / len(away_matches)) * 100 if len(away_matches) > 0 else 0
        
        # Average goals
        avg_goals_for = total_goals_for / total_matches
        avg_goals_against = total_goals_against / total_matches
        
        # Clean sheets
        home_clean_sheets = len(home_matches[home_matches['FTAG'] == 0])
        away_clean_sheets = len(away_matches[away_matches['FTHG'] == 0])
        total_clean_sheets = home_clean_sheets + away_clean_sheets
        
        # Recent form (last 5 matches)
        recent_matches = self.get_recent_matches(team_name, 5)
        recent_form = [match['result'] for match in recent_matches]
        
        # Strength ratings (based on performance metrics)
        attack_strength = min(100, (avg_goals_for / 2.5) * 100)  # Normalize to 100 scale
        defense_strength = max(0, 100 - (avg_goals_against / 2.5) * 100)
        overall_strength = (attack_strength + defense_strength) / 2
        
        return {
            'team_name': team_name,
            'total_matches': total_matches,
            'home_matches': len(home_matches),
            'away_matches': len(away_matches),
            'wins': total_wins,
            'draws': total_draws,
            'losses': total_losses,
            'win_percentage': round(win_percentage, 1),
            'home_win_percentage': round(home_win_percentage, 1),
            'away_win_percentage': round(away_win_percentage, 1),
            'goals_for': total_goals_for,
            'goals_against': total_goals_against,
            'goal_difference': total_goals_for - total_goals_against,
            'avg_goals_for': round(avg_goals_for, 2),
            'avg_goals_against': round(avg_goals_against, 2),
            'clean_sheets': total_clean_sheets,
            'clean_sheet_percentage': round((total_clean_sheets / total_matches) * 100, 1),
            'total_points': total_points,
            'points_per_game': round(points_per_game, 2),
            'recent_form': recent_form,
            'attack_strength': round(attack_strength),
            'defense_strength': round(defense_strength),
            'overall_strength': round(overall_strength),
            'home_record': {
                'wins': home_wins,
                'draws': home_draws,
                'losses': home_losses,
                'goals_for': home_goals_for,
                'goals_against': home_goals_against
            },
            'away_record': {
                'wins': away_wins,
                'draws': away_draws,
                'losses': away_losses,
                'goals_for': away_goals_for,
                'goals_against': away_goals_against
            }
        }
    
    def get_recent_matches(self, team_name: str, num_matches: int = 5) -> List[Dict]:
        """Get recent matches for a team"""
        if self.historical_data is None:
            return []
            
        # Get all matches for the team
        home_matches = self.historical_data[self.historical_data['HomeTeam'] == team_name].copy()
        away_matches = self.historical_data[self.historical_data['AwayTeam'] == team_name].copy()
        
        # Add match type and result
        home_matches['match_type'] = 'home'
        home_matches['opponent'] = home_matches['AwayTeam']
        home_matches['goals_for'] = home_matches['FTHG']
        home_matches['goals_against'] = home_matches['FTAG']
        home_matches['result'] = home_matches['FTR'].map({'H': 'W', 'D': 'D', 'A': 'L'})
        
        away_matches['match_type'] = 'away'
        away_matches['opponent'] = away_matches['HomeTeam']
        away_matches['goals_for'] = away_matches['FTAG']
        away_matches['goals_against'] = away_matches['FTHG']
        away_matches['result'] = away_matches['FTR'].map({'A': 'W', 'D': 'D', 'H': 'L'})
        
        # Combine and sort by date - FIXED DATE PARSING
        all_matches = pd.concat([home_matches, away_matches])
        
        # Fix date parsing with explicit format
        if 'Date' in all_matches.columns:
            # Try multiple common date formats
            date_formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
            
            for date_format in date_formats:
                try:
                    all_matches['Date'] = pd.to_datetime(all_matches['Date'], format=date_format, errors='coerce')
                    # Check if any dates were successfully parsed
                    if not all_matches['Date'].isna().all():
                        print(f"✅ Successfully parsed dates with format: {date_format}")
                        break
                except:
                    continue
            else:
                # If all formats fail, use flexible parsing as last resort
                all_matches['Date'] = pd.to_datetime(all_matches['Date'], errors='coerce', infer_datetime_format=True)
            
            all_matches = all_matches.dropna(subset=['Date'])
            all_matches = all_matches.sort_values('Date', ascending=False)
        
        # Get recent matches
        recent_matches = all_matches.head(num_matches)
        
        return recent_matches[['opponent', 'match_type', 'goals_for', 'goals_against', 'result']].to_dict('records')
    
    def get_head_to_head(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get head-to-head statistics between two teams"""
        if self.historical_data is None:
            return {'total_matches': 0, 'team1_wins': 0, 'team2_wins': 0, 'draws': 0}
            
        # Get all matches between these two teams
        matches = self.historical_data[
            ((self.historical_data['HomeTeam'] == team1) & (self.historical_data['AwayTeam'] == team2)) |
            ((self.historical_data['HomeTeam'] == team2) & (self.historical_data['AwayTeam'] == team1))
        ]
        
        if len(matches) == 0:
            return {'total_matches': 0, 'team1_wins': 0, 'team2_wins': 0, 'draws': 0}
        
        team1_wins = 0
        team2_wins = 0
        draws = 0
        
        for _, match in matches.iterrows():
            if match['HomeTeam'] == team1:
                if match['FTR'] == 'H':
                    team1_wins += 1
                elif match['FTR'] == 'A':
                    team2_wins += 1
                else:
                    draws += 1
            else:
                if match['FTR'] == 'A':
                    team1_wins += 1
                elif match['FTR'] == 'H':
                    team2_wins += 1
                else:
                    draws += 1
        
        total_matches = len(matches)
        
        return {
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_win_percentage': round((team1_wins / total_matches) * 100, 1) if total_matches > 0 else 0,
            'team2_win_percentage': round((team2_wins / total_matches) * 100, 1) if total_matches > 0 else 0,
            'draw_percentage': round((draws / total_matches) * 100, 1) if total_matches > 0 else 0,
            'recent_matches': self.get_recent_matches_between(team1, team2, 5)
        }
    
    def get_recent_matches_between(self, team1: str, team2: str, num_matches: int = 5) -> List[Dict]:
        """Get recent matches between two teams"""
        if self.historical_data is None:
            return []
            
        matches = self.historical_data[
            ((self.historical_data['HomeTeam'] == team1) & (self.historical_data['AwayTeam'] == team2)) |
            ((self.historical_data['HomeTeam'] == team2) & (self.historical_data['AwayTeam'] == team1))
        ].copy()
        
        # Fix date parsing with explicit format
        if 'Date' in matches.columns:
            # Try multiple common date formats
            date_formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
            
            for date_format in date_formats:
                try:
                    matches['Date'] = pd.to_datetime(matches['Date'], format=date_format, errors='coerce')
                    # Check if any dates were successfully parsed
                    if not matches['Date'].isna().all():
                        break
                except:
                    continue
            else:
                # If all formats fail, use flexible parsing as last resort
                matches['Date'] = pd.to_datetime(matches['Date'], errors='coerce', infer_datetime_format=True)
            
            matches = matches.dropna(subset=['Date'])
            matches = matches.sort_values('Date', ascending=False)
        
        recent_matches = matches.head(num_matches)
        
        results = []
        for _, match in recent_matches.iterrows():
            if match['HomeTeam'] == team1:
                result = {
                    'home_team': team1,
                    'away_team': team2,
                    'score': f"{match['FTHG']}-{match['FTAG']}",
                    'result': 'W' if match['FTR'] == 'H' else 'L' if match['FTR'] == 'A' else 'D'
                }
            else:
                result = {
                    'home_team': team2,
                    'away_team': team1,
                    'score': f"{match['FTHG']}-{match['FTAG']}",
                    'result': 'W' if match['FTR'] == 'A' else 'L' if match['FTR'] == 'H' else 'D'
                }
            results.append(result)
        
        return results
    
    def get_team_analysis(self, team_name: str) -> Dict[str, Any]:
        """Get comprehensive analysis for a team"""
        mapped_name = enhanced_map_team_name(team_name)
        
        if mapped_name not in self.teams_stats:
            return {'error': f'No data found for team: {team_name}', 'team_name': team_name}
        
        base_stats = self.teams_stats[mapped_name]
        recent_matches = self.get_recent_matches(mapped_name, 10)
        
        # Calculate form trends
        if len(recent_matches) >= 5:
            last_5_form = [match['result'] for match in recent_matches[:5]]
            form_trend = self.calculate_form_trend(last_5_form)
        else:
            form_trend = 'stable'
        
        return {
            **base_stats,
            'recent_matches': recent_matches,
            'form_trend': form_trend,
            'analysis': self.generate_team_analysis(base_stats, form_trend)
        }
    
    def calculate_form_trend(self, form: List[str]) -> str:
        """Calculate if team form is improving, declining, or stable"""
        if len(form) < 3:
            return 'stable'
        
        # Convert form to points (W=3, D=1, L=0)
        points = [3 if r == 'W' else 1 if r == 'D' else 0 for r in form]
        
        # Calculate trend
        first_half = sum(points[:2])
        second_half = sum(points[2:])
        
        if second_half > first_half:
            return 'improving'
        elif second_half < first_half:
            return 'declining'
        else:
            return 'stable'
    
    def generate_team_analysis(self, stats: Dict, form_trend: str) -> str:
        """Generate AI analysis of team performance"""
        analysis_parts = []
        
        # Overall strength
        if stats['overall_strength'] >= 80:
            analysis_parts.append("Elite team with consistent performance")
        elif stats['overall_strength'] >= 70:
            analysis_parts.append("Strong team with good fundamentals")
        elif stats['overall_strength'] >= 60:
            analysis_parts.append("Competitive team with room for improvement")
        else:
            analysis_parts.append("Developing team with potential")
        
        # Attack anagivelysis
        if stats['avg_goals_for'] >= 2.0:
            analysis_parts.append("Potent attacking force")
        elif stats['avg_goals_for'] >= 1.5:
            analysis_parts.append("Reliable goal-scoring capability")
        else:
            analysis_parts.append("Could improve offensive output")
        
        # Defense analysis
        if stats['avg_goals_against'] <= 1.0:
            analysis_parts.append("Excellent defensive organization")
        elif stats['avg_goals_against'] <= 1.5:
            analysis_parts.append("Solid defensive foundation")
        else:
            analysis_parts.append("Defense needs strengthening")
        
        # Form analysis
        if form_trend == 'improving':
            analysis_parts.append("Showing positive momentum recently")
        elif form_trend == 'declining':
            analysis_parts.append("Recent form has been concerning")
        else:
            analysis_parts.append("Maintaining consistent performance levels")
        
        # Home/Away analysis
        if stats['home_win_percentage'] - stats['away_win_percentage'] > 15:
            analysis_parts.append("Strong home advantage")
        elif stats['away_win_percentage'] - stats['home_win_percentage'] > 10:
            analysis_parts.append("Performs well on the road")
        
        return ". ".join(analysis_parts) + "."

# Initialize team analyzer
team_analyzer = TeamAnalyzer()

# =============================================================================
# IMPORT CHATBOT SERVICE
# =============================================================================

try:
    from chatbot_service import chatbot_service
    print("✅ Chatbot service imported successfully!")
except ImportError as e:
    print(f"❌ Could not import chatbot service: {e}")
    # Fallback placeholder
    class ChatbotService:
        def __init__(self):
            self.available = False
        
        async def process_question(self, question: str):
            return {
                "source": "error",
                "response": "Chatbot service is currently unavailable. Please try again later.",
                "confidence": "low"
            }
    
    chatbot_service = ChatbotService()

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(title="Scoresight API", version="1.0.0")

# CORS middleware to allow React frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router (file-based JSON user store)
try:
    from auth import router as auth_router
    app.include_router(auth_router)
    print("✅ Auth router included: /api/auth endpoints are available")
except ImportError as e:
    print(f"❌ Could not import auth router: {e}")
    # Create basic auth endpoints as fallback
    @app.post("/api/auth/login")
    async def login_fallback():
        raise HTTPException(status_code=501, detail="Authentication not configured")
    
    @app.post("/api/auth/signup") 
    async def signup_fallback():
        raise HTTPException(status_code=501, detail="Authentication not configured")
    
    print("⚠️ Auth endpoints not available - install pydantic[email]")
except Exception as e:
    print(f"⚠️ Could not include auth router: {e}")

FOOTBALL_API_TOKEN = "b839a17637ca4abc953080c5f3761314"
BASE_URL = "https://api.football-data.org/v4"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def create_pre_match_features(home_team, away_team):
    """Create feature vector for pre-match prediction using real historical data"""
    preprocessing = ml_models['pre_match_preprocessing']
    feature_columns = preprocessing['feature_columns']
    
    # Create base feature dictionary with zeros
    features = {col: 0.0 for col in feature_columns}
    
    # Set team features
    features['HomeTeam'] = home_team
    features['AwayTeam'] = away_team
    
    # Get real team statistics from historical data
    home_stats = team_analyzer.teams_stats.get(home_team, {})
    away_stats = team_analyzer.teams_stats.get(away_team, {})
    home_form = team_analyzer.teams_form.get(home_team, {})
    away_form = team_analyzer.teams_form.get(away_team, {})
    
    # Get head-to-head statistics
    h2h = team_analyzer.get_head_to_head(home_team, away_team)
    
    # Use real historical data instead of hardcoded values
    features['Home_Form_5'] = home_form.get('avg_points', 1.5)
    features['Away_Form_5'] = away_form.get('avg_points', 1.5)
    features['Home_Goals_Avg_5'] = home_form.get('goals_for_avg', 1.4)
    features['Away_Goals_Avg_5'] = away_form.get('goals_for_avg', 1.2)
    features['Home_Defense_Avg_5'] = home_form.get('goals_against_avg', 1.2)
    features['Away_Defense_Avg_5'] = away_form.get('goals_against_avg', 1.4)
    
    # Calculate betting odds based on team strength
    home_strength = home_stats.get('overall_strength', 70)
    away_strength = away_stats.get('overall_strength', 70)
    
    # Realistic odds calculation based on team strength
    strength_diff = home_strength - away_strength
    features['Avg_H_Odds'] = max(1.5, 3.0 - (strength_diff / 50))
    features['Avg_D_Odds'] = 3.4
    features['Avg_A_Odds'] = max(1.5, 3.0 + (strength_diff / 50))
    
    # Calculate probabilities from odds
    features['Home_Win_Probability'] = 1 / features['Avg_H_Odds']
    features['Draw_Probability'] = 1 / features['Avg_D_Odds']
    features['Away_Win_Probability'] = 1 / features['Avg_A_Odds']
    
    # Real head-to-head data
    features['H2H_Home_Wins'] = h2h.get('team1_wins', 3.0) if h2h.get('total_matches', 0) > 0 else 3.0
    features['H2H_Away_Wins'] = h2h.get('team2_wins', 2.0) if h2h.get('total_matches', 0) > 0 else 2.0
    
    # Season progress (default to mid-season)
    features['Season_Progress'] = 0.5
    features['Referee'] = 'M Dean'  # Default referee
    
    return features, feature_columns

def create_detailed_features(home_team, away_team, match_stats):
    """Create feature vector for detailed prediction using REAL user inputs WITHOUT DATA LEAKAGE"""
    preprocessing = ml_models['pre_match_preprocessing']
    feature_columns = preprocessing['feature_columns']
    
    # Create base feature dictionary with zeros
    features = {col: 0.0 for col in feature_columns}
    
    # Set team features
    features['HomeTeam'] = home_team
    features['AwayTeam'] = away_team
    
    # USE REAL USER INPUTS (NO FULL-TIME GOALS - THAT'S DATA LEAKAGE)
    features['HS'] = match_stats.get('hs', 0)
    features['AS'] = match_stats.get('as', 0)
    features['HST'] = match_stats.get('hst', 0)
    features['AST'] = match_stats.get('ast', 0)
    features['HC'] = match_stats.get('hc', 0)
    features['AC'] = match_stats.get('ac', 0)
    features['HF'] = match_stats.get('hf', 0)
    features['AF'] = match_stats.get('af', 0)
    features['HY'] = match_stats.get('hy', 0)
    features['AY'] = match_stats.get('ay', 0)
    features['HR'] = match_stats.get('hr', 0)
    features['AR'] = match_stats.get('ar', 0)
    
    # ⚠️ CRITICAL FIX: REMOVE FULL-TIME GOALS - THEY CAUSE DATA LEAKAGE
    # DO NOT USE fthg, ftag, or Goal_Difference for prediction
    # These are only known AFTER the match
    
    # Shot accuracy calculations (safe to use)
    features['Home_Shots_Accuracy'] = features['HST'] / features['HS'] if features['HS'] > 0 else 0
    features['Away_Shots_Accuracy'] = features['AST'] / features['AS'] if features['AS'] > 0 else 0
    
    # Get real team form and statistics
    home_stats = team_analyzer.teams_stats.get(home_team, {})
    away_stats = team_analyzer.teams_stats.get(away_team, {})
    home_form = team_analyzer.teams_form.get(home_team, {})
    away_form = team_analyzer.teams_form.get(away_team, {})
    h2h = team_analyzer.get_head_to_head(home_team, away_team)
    
    # Use real historical data combined with current match stats
    features['Home_Form_5'] = home_form.get('avg_points', 1.5)
    features['Away_Form_5'] = away_form.get('avg_points', 1.5)
    features['Home_Goals_Avg_5'] = home_form.get('goals_for_avg', 1.4)
    features['Away_Goals_Avg_5'] = away_form.get('goals_for_avg', 1.2)
    features['Home_Defense_Avg_5'] = home_form.get('goals_against_avg', 1.2)
    features['Away_Defense_Avg_5'] = away_form.get('goals_against_avg', 1.4)
    
    # Calculate betting odds based on current performance and historical strength
    home_strength = home_stats.get('overall_strength', 70)
    away_strength = away_stats.get('overall_strength', 70)
    
    # Adjust odds based on current match performance (using shots, not goals)
    current_home_advantage = 1.0
    home_shots_ratio = features['HS'] / (features['HS'] + features['AS'] + 1)
    if home_shots_ratio > 0.6:
        current_home_advantage = 0.8  # Home team dominating
    elif home_shots_ratio < 0.4:
        current_home_advantage = 1.2  # Away team dominating
    
    strength_diff = (home_strength - away_strength) * current_home_advantage
    features['Avg_H_Odds'] = max(1.5, 3.0 - (strength_diff / 50))
    features['Avg_D_Odds'] = 3.4
    features['Avg_A_Odds'] = max(1.5, 3.0 + (strength_diff / 50))
    
    features['Home_Win_Probability'] = 1 / features['Avg_H_Odds']
    features['Draw_Probability'] = 1 / features['Avg_D_Odds']
    features['Away_Win_Probability'] = 1 / features['Avg_A_Odds']
    
    # Real head-to-head data
    features['H2H_Home_Wins'] = h2h.get('team1_wins', 3.0) if h2h.get('total_matches', 0) > 0 else 3.0
    features['H2H_Away_Wins'] = h2h.get('team2_wins', 2.0) if h2h.get('total_matches', 0) > 0 else 2.0
    
    features['Season_Progress'] = 0.5
    features['Referee'] = 'M Dean'
    
    return features, feature_columns

def create_half_time_features(home_team, away_team, home_score, away_score, match_stats=None):
    """Create feature vector for half-time prediction using real-time data"""
    preprocessing = ml_models['half_time_preprocessing']
    feature_columns = preprocessing['feature_columns']
    
    # Create base feature dictionary with zeros
    features = {col: 0.0 for col in feature_columns}
    
    # Set team features
    features['HomeTeam'] = home_team
    features['AwayTeam'] = away_team
    
    # Set half-time specific features (this is OK for half-time prediction)
    features['HTHG'] = home_score
    features['HTAG'] = away_score
    
    # Calculate half-time result
    if home_score > away_score:
        features['HTR_numeric'] = 2
    elif away_score > home_score:
        features['HTR_numeric'] = 0
    else:
        features['HTR_numeric'] = 1
        
    features['HT_Goal_Difference'] = home_score - away_score
    
    # Use real-time statistics if provided, otherwise use realistic estimates
    if match_stats:
        # Use actual match statistics
        features['HS'] = match_stats.get('hs', 0)
        features['AS'] = match_stats.get('as', 0)
        features['HST'] = match_stats.get('hst', 0)
        features['AST'] = match_stats.get('ast', 0)
        features['HC'] = match_stats.get('hc', 0)
        features['AC'] = match_stats.get('ac', 0)
        features['HF'] = match_stats.get('hf', 0)
        features['AF'] = match_stats.get('af', 0)
        features['HY'] = match_stats.get('hy', 0)
        features['AY'] = match_stats.get('ay', 0)
        features['HR'] = match_stats.get('hr', 0)
        features['AR'] = match_stats.get('ar', 0)
    else:
        # Realistic estimates based on score and team strength
        home_stats = team_analyzer.teams_stats.get(home_team, {})
        away_stats = team_analyzer.teams_stats.get(away_team, {})
        
        base_shots = 5.0
        home_attack = home_stats.get('attack_strength', 70) / 100
        away_attack = away_stats.get('attack_strength', 70) / 100
        
        features['HS'] = base_shots + (home_attack * 3)
        features['AS'] = base_shots + (away_attack * 3)
        features['HST'] = max(1, home_score + (features['HS'] * 0.3))
        features['AST'] = max(1, away_score + (features['AS'] * 0.3))
        features['HC'] = max(1, features['HS'] * 0.5)
        features['AC'] = max(1, features['AS'] * 0.5)
        features['HF'] = 7.0
        features['AF'] = 8.0
        features['HY'] = 1.0
        features['AY'] = 1.0
        features['HR'] = 0.0
        features['AR'] = 0.0
    
    # Derived features
    features['Total_Shots_HT'] = features['HS'] + features['AS']
    features['Total_Shots_On_Target_HT'] = features['HST'] + features['AST']
    features['Total_Corners_HT'] = features['HC'] + features['AC']
    features['Total_Fouls_HT'] = features['HF'] + features['AF']
    
    # Shot accuracy
    features['Home_Shot_Accuracy_HT'] = features['HST'] / features['HS'] if features['HS'] > 0 else 0
    features['Away_Shot_Accuracy_HT'] = features['AST'] / features['AS'] if features['AS'] > 0 else 0
    
    return features, feature_columns

def preprocess_features(features, feature_columns, preprocessing_data):
    """Preprocess features using saved encoders and scalers"""
    # Create DataFrame
    df = pd.DataFrame([features])[feature_columns]
    
    # Encode categorical variables
    for col, encoder in preprocessing_data['label_encoders'].items():
        if col in df.columns:
            try:
                encoded_value = encoder.transform([features[col]])[0]
                df[col] = encoded_value
            except ValueError as e:
                fallback_value = hash(features[col]) % len(encoder.classes_)
                df[col] = fallback_value
    
    return df

def fix_xgboost_attributes(model):
    """Fix XGBoost missing attributes in ensemble models"""
    if hasattr(model, 'estimators_'):
        for estimator in model.estimators_:
            if hasattr(estimator, '__class__') and 'XGB' in estimator.__class__.__name__:
                missing_attrs = {
                    'use_label_encoder': False,
                    'enable_categorical': False,
                    'gpu_id': None,
                    'validate_parameters': None,
                    'predictor': None,
                    'n_jobs': None,
                    'monotone_constraints': None,
                    'interaction_constraints': None,
                    'feature_weights': None,
                    'max_cat_to_onehot': None,
                    'max_cat_threshold': None,
                    'eval_metric': None,
                    'early_stopping_rounds': None,
                    'callbacks': None,
                    'verbose': None
                }
                
                for attr, default_value in missing_attrs.items():
                    if not hasattr(estimator, attr):
                        setattr(estimator, attr, default_value)

# =============================================================================
# FIXED PREDICTION ENGINE
# =============================================================================

class FixedPredictionEngine:
    """Uses your actual trained ML models without hardcoded values"""
    
    def __init__(self, team_analyzer, ml_models):
        self.team_analyzer = team_analyzer
        self.ml_models = ml_models
    
    def create_features_using_model_knowledge(self, home_team: str, away_team: str, match_stats: Dict = None):
        """Create features using the same patterns your model was trained on"""
        # Map team names
        home_mapped = enhanced_map_team_name(home_team)
        away_mapped = enhanced_map_team_name(away_team)
        
        # Validate teams exist
        if home_mapped not in self.team_analyzer.teams_stats:
            raise ValueError(f"No historical data for home team: {home_team}")
        if away_mapped not in self.team_analyzer.teams_stats:
            raise ValueError(f"No historical data for away team: {away_team}")
        
        # Get preprocessing data
        preprocessing = self.ml_models['pre_match_preprocessing']
        feature_columns = preprocessing['feature_columns']
        features = {col: 0.0 for col in feature_columns}
        
        # Set team identity
        features['HomeTeam'] = home_mapped
        features['AwayTeam'] = away_mapped
        
        # Get historical data (NO SAFE DEFAULTS - use actual team data)
        home_stats = self.team_analyzer.teams_stats[home_mapped]
        away_stats = self.team_analyzer.teams_stats[away_mapped]
        home_form = self.team_analyzer.teams_form.get(home_mapped, {})
        away_form = self.team_analyzer.teams_form.get(away_mapped, {})
        h2h = self.team_analyzer.get_head_to_head(home_mapped, away_mapped)
        
        # USE THE EXACT FEATURES YOUR MODEL WAS TRAINED ON
        # Team form features (most important in your model)
        features['Home_Form_5'] = home_form.get('avg_points', home_stats.get('points_per_game', 1.0))
        features['Away_Form_5'] = away_form.get('avg_points', away_stats.get('points_per_game', 1.0))
        
        # Goal averages
        features['Home_Goals_Avg_5'] = home_form.get('goals_for_avg', home_stats.get('avg_goals_for', 1.2))
        features['Away_Goals_Avg_5'] = away_form.get('goals_for_avg', away_stats.get('avg_goals_for', 1.0))
        
        # Defense averages  
        features['Home_Defense_Avg_5'] = home_form.get('goals_against_avg', home_stats.get('avg_goals_against', 1.2))
        features['Away_Defense_Avg_5'] = away_form.get('goals_against_avg', away_stats.get('avg_goals_against', 1.4))
        
        # Head-to-head (important feature)
        total_h2h = h2h.get('total_matches', 0)
        if total_h2h > 0:
            features['H2H_Home_Wins'] = h2h['team1_wins']
            features['H2H_Away_Wins'] = h2h['team2_wins']
        else:
            # If no H2H, use team quality difference
            home_quality = home_stats.get('overall_strength', 70)
            away_quality = away_stats.get('overall_strength', 70)
            features['H2H_Home_Wins'] = max(1, home_quality / 25)
            features['H2H_Away_Wins'] = max(1, away_quality / 25)
        
        # Betting probabilities (key features from your model)
        home_strength = home_stats.get('overall_strength', 70)
        away_strength = away_stats.get('overall_strength', 70)
        
        # Calculate realistic odds based on team strength difference
        strength_diff = home_strength - away_strength
        features['Avg_H_Odds'] = max(1.5, 3.0 - (strength_diff / 40))
        features['Avg_D_Odds'] = 3.2
        features['Avg_A_Odds'] = max(1.5, 3.0 + (strength_diff / 40))
        
        features['Home_Win_Probability'] = 1 / features['Avg_H_Odds']
        features['Draw_Probability'] = 1 / features['Avg_D_Odds']
        features['Away_Win_Probability'] = 1 / features['Avg_A_Odds']
        
        # Current match stats (limited influence)
        if match_stats:
            features['HS'] = match_stats.get('hs', 0)
            features['AS'] = match_stats.get('as', 0)
            features['HST'] = match_stats.get('hst', 0)
            features['AST'] = match_stats.get('ast', 0)
            features['HC'] = match_stats.get('hc', 0)
            features['AC'] = match_stats.get('ac', 0)
            features['HF'] = match_stats.get('hf', 0)
            features['AF'] = match_stats.get('af', 0)
            features['HY'] = match_stats.get('hy', 0)
            features['AY'] = match_stats.get('ay', 0)
            features['HR'] = match_stats.get('hr', 0)
            features['AR'] = match_stats.get('ar', 0)
        else:
            # Realistic estimates based on team strength
            features['HS'] = 10 + (home_strength / 15)
            features['AS'] = 8 + (away_strength / 15)
            features['HST'] = max(1, features['HS'] * 0.4)
            features['AST'] = max(1, features['AS'] * 0.4)
            features['HC'] = max(1, features['HS'] * 0.3)
            features['AC'] = max(1, features['AS'] * 0.3)
            features['HF'] = 8.0
            features['AF'] = 10.0
            features['HY'] = 1.0
            features['AY'] = 1.0
            features['HR'] = 0.0
            features['AR'] = 0.0
        
        # Derived features
        features['Home_Shots_Accuracy'] = features['HST'] / features['HS'] if features['HS'] > 0 else 0.4
        features['Away_Shots_Accuracy'] = features['AST'] / features['AS'] if features['AS'] > 0 else 0.4
        
        # Season and referee (standard values)
        features['Season_Progress'] = 0.5
        features['Referee'] = 'M Dean'
        
        return features, feature_columns, home_strength, away_strength

# Initialize prediction engine
prediction_engine = FixedPredictionEngine(team_analyzer, ml_models)

# =============================================================================
# CHATBOT API ENDPOINTS (Will be connected to new chatbot service)
# =============================================================================

@app.post("/api/chat/message")
async def chat_message(message_data: dict):
    """Main chat endpoint that will use the new chatbot service"""
    try:
        question = message_data.get('message', '')
        
        if not question:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Process the question using the chatbot service
        bot_response = await chatbot_service.process_question(question)
        
        return {
            "success": True,
            "question": question,
            "response": bot_response["response"],
            "source": bot_response["source"],
            "confidence": bot_response["confidence"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/chat/suggestions")
async def get_chat_suggestions():
    """Get suggested questions for the chat"""
    suggestions = [
        "Predict Manchester City vs Liverpool",
        "Show me Arsenal's recent form",
        "Chelsea vs Tottenham head to head",
        "Who will win the Premier League?",
        "Explain the offside rule",
        "Best Premier League strikers 2024",
        "Manchester United team analysis",
        "Newcastle vs Brighton prediction"
    ]
    
    return {"suggestions": suggestions}

# =============================================================================
# TEAM ANALYTICS API ENDPOINTS
# =============================================================================

@app.get("/api/teams/{team_name}/analysis")
async def get_team_analysis(team_name: str):
    """Get comprehensive analysis for a specific team"""
    try:
        print(f"🔍 Team analysis requested for: '{team_name}'")
        mapped_name = enhanced_map_team_name(team_name)
        print(f"🔄 Mapped to: '{mapped_name}'")
        
        if mapped_name not in team_analyzer.teams_stats:
            print(f"❌ Team '{mapped_name}' not found in stats")
            raise HTTPException(status_code=404, detail=f"No data found for team: {team_name}")
        
        analysis = team_analyzer.get_team_analysis(team_name)
        
        # Ensure all required fields are present for the UI
        if 'error' not in analysis:
            # Add missing fields that UI expects
            analysis['team_name'] = analysis.get('team_name', team_name)
            analysis['recent_matches'] = analysis.get('recent_matches', [])
            analysis['analysis'] = analysis.get('analysis', "No analysis available.")
        
        # Convert numpy types to Python native types
        analysis = convert_numpy_types(analysis)
            
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error analyzing team {team_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing team: {str(e)}")

@app.get("/api/teams/{team_name}/stats")
async def get_team_stats(team_name: str):
    """Get basic statistics for a specific team"""
    try:
        print(f"🔍 Team stats requested for: '{team_name}'")
        mapped_name = enhanced_map_team_name(team_name)
        print(f"🔄 Mapped to: '{mapped_name}'")
        
        if mapped_name in team_analyzer.teams_stats:
            stats = team_analyzer.teams_stats[mapped_name]
            # Ensure team_name field is present
            stats['team_name'] = stats.get('team_name', team_name)
            
            # Convert numpy types to Python native types
            stats = convert_numpy_types(stats)
            
            return stats
        else:
            print(f"❌ Team '{mapped_name}' not found in stats")
            raise HTTPException(status_code=404, detail=f"No data found for team: {team_name}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting team stats for {team_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting team stats: {str(e)}")

@app.get("/api/teams/{team1}/vs/{team2}")
async def get_head_to_head(team1: str, team2: str):
    """Get head-to-head statistics between two teams"""
    try:
        print(f"🔍 Head-to-head requested: '{team1}' vs '{team2}'")
        mapped_team1 = enhanced_map_team_name(team1)
        mapped_team2 = enhanced_map_team_name(team2)
        print(f"🔄 Mapped to: '{mapped_team1}' vs '{mapped_team2}'")
        
        h2h = team_analyzer.get_head_to_head(mapped_team1, mapped_team2)
        
        if not h2h or h2h.get('total_matches', 0) == 0:
            print(f"❌ No head-to-head data found")
            raise HTTPException(status_code=404, detail=f"No head-to-head data found for {team1} vs {team2}")
        
        # Convert numpy types to Python native types
        h2h = convert_numpy_types(h2h)
        
        return h2h
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting head-to-head {team1} vs {team2}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting head-to-head data: {str(e)}")

@app.get("/api/teams/{team_name}/form")
async def get_team_form(team_name: str, matches: int = 5):
    """Get recent form for a team"""
    try:
        print(f"🔍 Team form requested for: '{team_name}'")
        mapped_name = enhanced_map_team_name(team_name)
        print(f"🔄 Mapped to: '{mapped_name}'")
        
        recent_matches = team_analyzer.get_recent_matches(mapped_name, matches)
        
        if not recent_matches:
            print(f"❌ No recent matches found")
            raise HTTPException(status_code=404, detail=f"No recent matches found for team: {team_name}")
        
        # Calculate form points
        form_points = []
        for match in recent_matches:
            if match['result'] == 'W':
                form_points.append(3)
            elif match['result'] == 'D':
                form_points.append(1)
            else:
                form_points.append(0)
        
        avg_points = sum(form_points) / len(form_points) if form_points else 0
        
        result = {
            'team': team_name,
            'recent_matches': recent_matches,
            'form_sequence': [match['result'] for match in recent_matches],
            'average_points': round(avg_points, 2),
            'total_points': sum(form_points),
            'form_rating': 'excellent' if avg_points >= 2.5 else 'good' if avg_points >= 1.5 else 'average' if avg_points >= 1.0 else 'poor'
        }
        
        # Convert numpy types to Python native types
        result = convert_numpy_types(result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting team form for {team_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting team form: {str(e)}")

@app.get("/api/teams-analysis/all")
async def get_all_teams_analysis():
    """Get analysis for all teams"""
    try:
        all_teams = list(team_analyzer.teams_stats.keys())
        teams_analysis = {}
        
        for team in all_teams[:20]:  # Limit to first 20 teams for performance
            teams_analysis[team] = team_analyzer.teams_stats[team]
        
        return {
            'total_teams': len(all_teams),
            'teams': teams_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all teams analysis: {str(e)}")

# =============================================================================
# EXISTING API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    return {"message": "Scoresight API is running!"}

@app.get("/api/fixtures")
async def get_fixtures():
    """Get Premier League fixtures"""
    try:
        headers = {
            "X-Auth-Token": FOOTBALL_API_TOKEN,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/competitions/PL/matches", headers=headers)
        
        if response.status_code != 200:
            print(f"Football API returned status: {response.status_code}")
            return {"matches": []}
            
        response.raise_for_status()
        
        data = response.json()
        
        # Transform to frontend format
        matches = []
        for match in data.get("matches", []):
            matches.append({
                "id": match["id"],
                "homeTeam": {
                    "id": match["homeTeam"]["id"],
                    "name": match["homeTeam"]["name"],
                    "shortName": match["homeTeam"]["shortName"] or match["homeTeam"]["name"][:3].upper(),
                    "crest": match["homeTeam"]["crest"] or "⚽"
                },
                "awayTeam": {
                    "id": match["awayTeam"]["id"],
                    "name": match["awayTeam"]["name"],
                    "shortName": match["awayTeam"]["shortName"] or match["awayTeam"]["name"][:3].upper(),
                    "crest": match["awayTeam"]["crest"] or "⚽"
                },
                "date": match.get("utcDate", ""),
                "status": match.get("status", "SCHEDULED"),
                "score": match.get("score", {}),
                "venue": match.get("venue", "Premier League"),
                "matchday": match.get("matchday", 0)
            })
        
        return {"matches": matches}
        
    except requests.RequestException as e:
        print(f"Football API error: {str(e)}")
        return {"matches": []}
 
@app.get("/api/teams")
async def get_teams():
    """Get Premier League teams"""
    try:
        headers = {
            "X-Auth-Token": FOOTBALL_API_TOKEN,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/competitions/PL/teams", headers=headers)
        
        if response.status_code != 200:
            print(f"Football API returned status: {response.status_code}")
            return {"teams": []}
            
        response.raise_for_status()
        
        data = response.json()
        
        # Transform to frontend format
        teams = []
        for team in data.get("teams", []):
            teams.append({
                "id": team["id"],
                "name": team["name"],
                "shortName": team["shortName"] or team["name"][:3].upper(),
                "crest": team["crest"] or "⚽",
                "founded": team.get("founded"),
                "venue": team.get("venue"),
                "clubColors": team.get("clubColors")
            })
        
        return {"teams": teams}
        
    except requests.RequestException as e:
        print(f"Football API error: {str(e)}")
        return {"teams": []}

async def predict_match_internal(home_team: str, away_team: str):
    """Internal prediction function for chatbot use"""
    if ml_models is None:
        return {"error": "ML model not loaded"}
    
    # Map team names to your model's format
    home_team_mapped = enhanced_map_team_name(home_team)
    away_team_mapped = enhanced_map_team_name(away_team)
    
    # Create features for pre-match prediction
    features, feature_columns = create_pre_match_features(home_team_mapped, away_team_mapped)
    
    # Preprocess features
    processed_features = preprocess_features(
        features, 
        feature_columns, 
        ml_models['pre_match_preprocessing']
    )

    # Get prediction probabilities
    model = ml_models['pre_match_model']
    fix_xgboost_attributes(model)

    # Make prediction
    probabilities = model.predict_proba(processed_features)[0]
    
    # Map probabilities to outcomes [Away, Draw, Home]
    away_win_prob = float(probabilities[0])
    draw_prob = float(probabilities[1]) 
    home_win_prob = float(probabilities[2])

    # Determine confidence and predicted outcome
    max_prob = max(home_win_prob, draw_prob, away_win_prob)
    confidence = "high" if max_prob > 0.6 else "medium" if max_prob > 0.45 else "low"
    
    if home_win_prob > away_win_prob and home_win_prob > draw_prob:
        predicted_outcome = "HOME"
        predicted_score = "2-1"
    elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
        predicted_outcome = "AWAY" 
        predicted_score = "1-2"
    else:
        predicted_outcome = "DRAW"
        predicted_score = "1-1"

    return {
        "home_team": home_team,
        "away_team": away_team, 
        "home_win_prob": home_win_prob,
        "draw_prob": draw_prob,
        "away_win_prob": away_win_prob,
        "predicted_outcome": predicted_outcome,
        "predicted_score": predicted_score,
        "confidence": confidence,
        "keyFactors": [
            "Team form analysis",
            "Head-to-head record", 
            "Home advantage",
            "Recent performance"
        ]
    }

@app.get("/api/predict")
async def predict_match(home_team: str, away_team: str):
    """Real prediction using your 75% accurate ML model"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded", 
                "model_loaded": False
            }

        prediction_result = await predict_match_internal(home_team, away_team)
        
        if 'error' in prediction_result:
            return prediction_result

        return {
            **prediction_result,
            "aiExplanation": f"ML model prediction: {max(prediction_result['home_win_prob'], prediction_result['draw_prob'], prediction_result['away_win_prob'])*100:.1f}% chance of {prediction_result['predicted_outcome'].lower()} victory.",
            "model_used": "Real ML Model (75% accuracy)",
            "model_loaded": True,
            "real_prediction": True
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "model_loaded": ml_models is not None
        }

@app.post("/api/predict-detailed")
async def predict_detailed_match(match_data: dict):
    """Detailed prediction using real match statistics from user input"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded", 
                "model_loaded": False
            }

        # Extract data from request
        home_team = match_data.get('home_team', '')
        away_team = match_data.get('away_team', '')
        
        if not home_team or not away_team:
            return {
                "error": "Both home_team and away_team are required",
                "model_loaded": True
            }

        # Map team names to your model's format
        home_team_mapped = enhanced_map_team_name(home_team)
        away_team_mapped = enhanced_map_team_name(away_team)

        print(f"📊 Detailed prediction: '{home_team}' vs '{away_team}'")
        
        # Create features for detailed prediction WITHOUT DATA LEAKAGE
        features, feature_columns = create_detailed_features(home_team_mapped, away_team_mapped, match_data)
        
        # Preprocess features
        processed_features = preprocess_features(
            features, 
            feature_columns, 
            ml_models['pre_match_preprocessing']
        )

        # Get prediction probabilities
        model = ml_models['pre_match_model']
        fix_xgboost_attributes(model)

        # Make prediction with real data
        probabilities = model.predict_proba(processed_features)[0]
        
        # Map probabilities to outcomes [Away, Draw, Home]
        away_win_prob = float(probabilities[0])
        draw_prob = float(probabilities[1]) 
        home_win_prob = float(probabilities[2])

        print(f"🎯 Raw probabilities: Away={away_win_prob:.3f}, Draw={draw_prob:.3f}, Home={home_win_prob:.3f}")

        # Determine confidence and predicted outcome
        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = "high" if max_prob > 0.6 else "medium" if max_prob > 0.45 else "low"
        
        # Generate score prediction based on actual shots (NOT full-time goals)
        home_shots = match_data.get('hs', 0)
        away_shots = match_data.get('as', 0)
        home_shots_on_target = match_data.get('hst', 0)
        away_shots_on_target = match_data.get('ast', 0)
        
        # Calculate expected goals based on shots and accuracy
        home_shot_accuracy = home_shots_on_target / home_shots if home_shots > 0 else 0.4
        away_shot_accuracy = away_shots_on_target / away_shots if away_shots > 0 else 0.4
        
        # Use probabilities to determine likely goals
        home_expected_goals = (home_win_prob * 2.5) + (home_shots_on_target * 0.1)
        away_expected_goals = (away_win_prob * 2.5) + (away_shots_on_target * 0.1)
        
        home_final = max(0, round(home_expected_goals))
        away_final = max(0, round(away_expected_goals))
        
        # Ensure at least one goal if someone is heavily favored
        if home_final == 0 and away_final == 0 and max_prob > 0.6:
            if home_win_prob > away_win_prob:
                home_final = 1
            else:
                away_final = 1
        
        predicted_score = f"{home_final}-{away_final}"
        
        # Determine outcome
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            predicted_outcome = "HOME"
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            predicted_outcome = "AWAY"
        else:
            predicted_outcome = "DRAW"

        # Generate dynamic key factors
        key_factors = []
        
        if home_shots > away_shots + 3:
            key_factors.append(f"Home team dominating shots ({home_shots} vs {away_shots})")
        elif away_shots > home_shots + 3:
            key_factors.append(f"Away team dominating shots ({away_shots} vs {home_shots})")
        
        if home_shot_accuracy > 0.5:
            key_factors.append("Excellent home shooting accuracy")
        if away_shot_accuracy > 0.5:
            key_factors.append("Excellent away shooting accuracy")
            
        home_corners = match_data.get('hc', 0)
        away_corners = match_data.get('ac', 0)
        if home_corners > away_corners + 2:
            key_factors.append("Home team creating more set-piece opportunities")
        elif away_corners > home_corners + 2:
            key_factors.append("Away team creating more set-piece opportunities")
            
        home_yellows = match_data.get('hy', 0)
        away_yellows = match_data.get('ay', 0)
        if home_yellows > 2:
            key_factors.append("Home team discipline concerns")
        if away_yellows > 2:
            key_factors.append("Away team discipline concerns")
            
        if 'Man City' in home_team or 'Liverpool' in home_team or 'Arsenal' in home_team:
            key_factors.append("Home team has superior squad quality")
        if 'Man City' in away_team or 'Liverpool' in away_team or 'Arsenal' in away_team:
            key_factors.append("Away team has superior squad quality")
            
        default_factors = [
            "Team form analysis",
            "Head-to-head record", 
            "Home advantage significance"
        ]
        
        while len(key_factors) < 3:
            key_factors.append(default_factors[len(key_factors)])
        
        # Generate AI explanation
        ai_explanation = f"Based on comprehensive match statistics analysis, {predicted_outcome.lower()} team has {max_prob*100:.1f}% chance to win. "
        ai_explanation += f"Home team: {home_shots} shots ({home_shots_on_target} on target), Away team: {away_shots} shots ({away_shots_on_target} on target)."

        return {
            "home_team": home_team,
            "away_team": away_team, 
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "predicted_outcome": predicted_outcome,
            "predicted_score": predicted_score,
            "confidence": confidence,
            "keyFactors": key_factors,
            "aiExplanation": ai_explanation,
            "model_used": "Real ML Model with Detailed Statistics",
            "model_loaded": True,
            "real_prediction": True,
            "statistics_used": {
                "home_shots": home_shots,
                "away_shots": away_shots,
                "home_shots_on_target": home_shots_on_target,
                "away_shots_on_target": away_shots_on_target,
                "home_corners": home_corners,
                "away_corners": away_corners
            }
        }
        
    except Exception as e:
        print(f"Detailed prediction error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "model_loaded": ml_models is not None
        }

@app.post("/api/half-time-predict")
async def half_time_predict(half_time_data: dict):
    """Half-time prediction using your 65% accurate ML model with real-time data"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded",
                "model_loaded": False
            }
        
        # Extract data from request
        home_team = half_time_data.get('home_team', '')
        away_team = half_time_data.get('away_team', '')
        home_score = half_time_data.get('home_score', 0)
        away_score = half_time_data.get('away_score', 0)
        match_stats = half_time_data.get('match_stats', {})
        
        if not home_team or not away_team:
            return {
                "error": "Both home_team and away_team are required",
                "model_loaded": True
            }

        # Map team names to your model's format
        home_team_mapped = enhanced_map_team_name(home_team)
        away_team_mapped = enhanced_map_team_name(away_team)
        
        # Create features for half-time prediction with real-time data
        features, feature_columns = create_half_time_features(
            home_team_mapped, away_team_mapped, home_score, away_score, match_stats
        )
        
        # Preprocess features
        processed_features = preprocess_features(
            features,
            feature_columns,
            ml_models['half_time_preprocessing']
        )
        
        # Get prediction probabilities
        model = ml_models['half_time_model']
        fix_xgboost_attributes(model)

        probabilities = model.predict_proba(processed_features)[0]
        
        # Map probabilities to outcomes [Away, Draw, Home]
        away_win_prob = float(probabilities[0])
        draw_prob = float(probabilities[1]) 
        home_win_prob = float(probabilities[2])
        
        # Determine confidence and predicted outcome
        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = "high" if max_prob > 0.6 else "medium" if max_prob > 0.45 else "low"
        
        # Predict final score based on current score, probabilities, and match statistics
        home_shots = match_stats.get('hs', features['HS'])
        away_shots = match_stats.get('as', features['AS'])
        home_shots_on_target = match_stats.get('hst', features['HST'])
        away_shots_on_target = match_stats.get('ast', features['AST'])
        
        # Calculate expected second half goals based on current performance
        home_expected_additional = (home_shots_on_target * 0.15) + (0.5 if home_win_prob > 0.5 else 0)
        away_expected_additional = (away_shots_on_target * 0.15) + (0.5 if away_win_prob > 0.5 else 0)
        
        home_final = home_score + max(0, round(home_expected_additional))
        away_final = away_score + max(0, round(away_expected_additional))
        
        # Ensure at least one goal if someone is heavily favored
        if home_final == home_score and away_final == away_score and max_prob > 0.6:
            if home_win_prob > away_win_prob:
                home_final += 1
            else:
                away_final += 1
        
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            predicted_outcome = "HOME"
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            predicted_outcome = "AWAY"
        else:
            predicted_outcome = "DRAW"

        # Generate dynamic key factors for half-time
        key_factors = []
        
        if home_score > away_score:
            key_factors.append(f"Home team leading {home_score}-{away_score}")
        elif away_score > home_score:
            key_factors.append(f"Away team leading {away_score}-{home_score}")
        else:
            key_factors.append("Match is currently level")
            
        if home_shots > away_shots + 2:
            key_factors.append(f"Home team dominating possession ({home_shots} shots)")
        elif away_shots > home_shots + 2:
            key_factors.append(f"Away team dominating possession ({away_shots} shots)")
            
        home_accuracy = home_shots_on_target / home_shots if home_shots > 0 else 0
        away_accuracy = away_shots_on_target / away_shots if away_shots > 0 else 0
        
        if home_accuracy > 0.5:
            key_factors.append("Home team shooting accurately")
        if away_accuracy > 0.5:
            key_factors.append("Away team shooting accurately")
            
        # Add historical factors
        h2h = team_analyzer.get_head_to_head(home_team, away_team)
        if h2h.get('total_matches', 0) > 0:
            if h2h['team1_win_percentage'] > 60:
                key_factors.append("Strong historical advantage for home team")
            elif h2h['team2_win_percentage'] > 60:
                key_factors.append("Strong historical advantage for away team")

        return {
            "home_team": home_team,
            "away_team": away_team,
            "homeWinProbability": home_win_prob,
            "drawProbability": draw_prob,
            "awayWinProbability": away_win_prob,
            "predicted_outcome": predicted_outcome,
            "finalScore": f"{home_final}-{away_final}",
            "confidence": confidence,
            "momentum": "home" if home_score > away_score else "away" if away_score > home_score else "equal",
            "comebackLikelihood": "high" if (away_score > home_score and home_win_prob > away_win_prob) or 
                                        (home_score > away_score and away_win_prob > home_win_prob) else "medium",
            "keyFactors": key_factors,
            "aiExplanation": f"Based on first-half performance and machine learning analysis, {predicted_outcome.lower()} team has {max_prob*100:.1f}% chance to win.",
            "model_used": "Real ML Model (65% accuracy)",
            "model_loaded": True,
            "real_prediction": True
        }
    except Exception as e:
        print(f"Half-time prediction error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "model_loaded": ml_models is not None,
            "real_prediction": False
        }

# =============================================================================
# FIXED PREDICTION ENDPOINTS USING YOUR ACTUAL MODELS
# =============================================================================

@app.post("/api/predict-detailed-fixed")
async def predict_detailed_match_fixed(match_data: dict):
    """Fixed detailed prediction using your actual ML model with proper team weighting"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded", 
                "model_loaded": False
            }

        home_team = match_data.get('home_team', '')
        away_team = match_data.get('away_team', '')
        
        if not home_team or not away_team:
            return {
                "error": "Both home_team and away_team are required",
                "model_loaded": True
            }

        print(f"🎯 FIXED prediction: '{home_team}' vs '{away_team}'")
        
        # USE FIXED PREDICTION ENGINE WITH YOUR ACTUAL MODEL
        features, feature_columns, home_quality, away_quality = prediction_engine.create_features_using_model_knowledge(
            home_team, away_team, match_data
        )
        
        # Preprocess features
        processed_features = preprocess_features(
            features, 
            feature_columns, 
            ml_models['pre_match_preprocessing']
        )

        # Get prediction probabilities from YOUR ACTUAL MODEL
        model = ml_models['pre_match_model']
        fix_xgboost_attributes(model)

        # Make prediction with your 75.7% accurate model
        probabilities = model.predict_proba(processed_features)[0]
        
        # Map probabilities to outcomes [Away, Draw, Home]
        away_win_prob = float(probabilities[0])
        draw_prob = float(probabilities[1]) 
        home_win_prob = float(probabilities[2])

        print(f"🎯 Model probabilities: Away={away_win_prob:.3f}, Draw={draw_prob:.3f}, Home={home_win_prob:.3f}")
        print(f"🏆 Team qualities: {home_team}={home_quality:.1f}, {away_team}={away_quality:.1f}")

        # Determine confidence and predicted outcome
        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = "high" if max_prob > 0.6 else "medium" if max_prob > 0.45 else "low"
        
        # Generate score prediction based on team quality
        home_expected = (home_quality / 45) + (features['HS'] * 0.03)
        away_expected = (away_quality / 45) + (features['AS'] * 0.03)
        
        home_final = max(0, round(home_expected))
        away_final = max(0, round(away_expected))
        
        # Ensure realistic scores
        if home_final == 0 and away_final == 0:
            if home_quality > away_quality:
                home_final = 1
            else:
                away_final = 1
        
        predicted_score = f"{home_final}-{away_final}"
        
        # Determine outcome
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            predicted_outcome = "HOME"
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            predicted_outcome = "AWAY"
        else:
            predicted_outcome = "DRAW"

        # Generate team-specific key factors
        key_factors = []
        
        # Team quality factors
        quality_diff = home_quality - away_quality
        if quality_diff > 25:
            key_factors.append(f"{home_team} have significant quality advantage")
        elif quality_diff > 10:
            key_factors.append(f"{home_team} have quality edge")
        elif quality_diff < -25:
            key_factors.append(f"{away_team} have significant quality advantage")
        elif quality_diff < -10:
            key_factors.append(f"{away_team} have quality edge")
        
        # Form factors
        if features['Home_Form_5'] > 2.0:
            key_factors.append(f"{home_team} in excellent recent form")
        if features['Away_Form_5'] > 2.0:
            key_factors.append(f"{away_team} in excellent recent form")
            
        # Current performance factors
        home_shots = match_data.get('hs', 0)
        away_shots = match_data.get('as', 0)
        
        if home_shots > away_shots + 5:
            key_factors.append(f"Home team dominating shots ({home_shots} vs {away_shots})")
        elif away_shots > home_shots + 5:
            key_factors.append(f"Away team dominating shots ({away_shots} vs {home_shots})")

        # Generate AI explanation
        ai_explanation = f"Based on comprehensive analysis: {home_team} (Quality: {home_quality:.0f}/100) vs {away_team} (Quality: {away_quality:.0f}/100). "
        ai_explanation += f"Team quality and recent form are the primary factors in this prediction."

        return {
            "home_team": home_team,
            "away_team": away_team, 
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "predicted_outcome": predicted_outcome,
            "predicted_score": predicted_score,
            "confidence": confidence,
            "keyFactors": key_factors,
            "aiExplanation": ai_explanation,
            "model_used": "Your Actual ML Model (75.7% accuracy)",
            "model_loaded": True,
            "real_prediction": True,
            "team_qualities": {
                "home_quality": home_quality,
                "away_quality": away_quality,
                "quality_difference": home_quality - away_quality
            }
        }
        
    except ValueError as e:
        # Team not found error
        return {
            "error": str(e),
            "model_loaded": True,
            "real_prediction": False
        }
    except Exception as e:
        print(f"Fixed prediction error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "model_loaded": ml_models is not None
        }

@app.get("/api/predict-fixed")
async def predict_match_fixed(home_team: str, away_team: str):
    """Fixed basic prediction using your actual ML model with proper team weighting"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded", 
                "model_loaded": False
            }

        # USE FIXED PREDICTION ENGINE
        features, feature_columns, home_quality, away_quality = prediction_engine.create_features_using_model_knowledge(
            home_team, away_team, None
        )
        
        # Preprocess features
        processed_features = preprocess_features(
            features, 
            feature_columns, 
            ml_models['pre_match_preprocessing']
        )

        # Get prediction probabilities from YOUR MODEL
        model = ml_models['pre_match_model']
        fix_xgboost_attributes(model)

        probabilities = model.predict_proba(processed_features)[0]
        
        away_win_prob = float(probabilities[0])
        draw_prob = float(probabilities[1]) 
        home_win_prob = float(probabilities[2])

        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = "high" if max_prob > 0.6 else "medium" if max_prob > 0.45 else "low"
        
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            predicted_outcome = "HOME"
            predicted_score = "2-1"
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            predicted_outcome = "AWAY" 
            predicted_score = "1-2"
        else:
            predicted_outcome = "DRAW"
            predicted_score = "1-1"

        # Generate team-specific factors
        key_factors = []
        quality_diff = home_quality - away_quality
        
        if quality_diff > 20:
            key_factors.append(f"{home_team} have strong quality advantage")
        elif quality_diff < -20:
            key_factors.append(f"{away_team} have strong quality advantage")
            
        if features['Home_Form_5'] > 2.0:
            key_factors.append(f"{home_team} in good recent form")
        if features['Away_Form_5'] > 2.0:
            key_factors.append(f"{away_team} in good recent form")

        return {
            "home_team": home_team,
            "away_team": away_team, 
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "predicted_outcome": predicted_outcome,
            "predicted_score": predicted_score,
            "confidence": confidence,
            "keyFactors": key_factors,
            "aiExplanation": f"Team quality analysis: {home_team} ({home_quality:.0f}/100) vs {away_team} ({away_quality:.0f}/100). Quality difference drives prediction.",
            "model_used": "Your Actual ML Model (75.7% accuracy)",
            "model_loaded": True,
            "real_prediction": True
        }
        
    except ValueError as e:
        return {"error": str(e), "model_loaded": True}
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return {
            "error": str(e),
            "model_loaded": ml_models is not None
        }

news_router = APIRouter(prefix="/api/news", tags=["news"])

@app.get("/api/news/epl")
async def get_epl_news(limit: int = 10):
    """Get latest EPL news"""
    try:
        news = news_service.get_all_news(limit=limit)
        return {
            "success": True,
            "data": news,
            "count": len(news)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }
    
app.include_router(news_router)
# =============================================================================
# IMPORT ACTUAL CHATBOT SERVICE (This will replace the placeholder)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)