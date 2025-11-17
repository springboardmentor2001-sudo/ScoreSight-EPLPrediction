import pandas as pd
import numpy as np
import joblib
import os
import sys

# Add the project root to sys.path to handle relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Config to get the correct model directory
from app.config import Config

# Load our trained models and encoders
# These were created during the model training process
try:
    model_dir = Config.MODEL_DIR
    match_winner_model = joblib.load(os.path.join(model_dir, 'match_winner_model.pkl'))
    fthg_model = joblib.load(os.path.join(model_dir, 'fthg_model.pkl'))
    ftag_model = joblib.load(os.path.join(model_dir, 'ftag_model.pkl'))
    home_team_encoder = joblib.load(os.path.join(model_dir, 'home_team_encoder.pkl'))
    away_team_encoder = joblib.load(os.path.join(model_dir, 'away_team_encoder.pkl'))
    print("Models and encoders loaded successfully!")
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    # Continue with the app even if models fail to load
    match_winner_model = None
    fthg_model = None
    ftag_model = None
    home_team_encoder = None
    away_team_encoder = None
    models_loaded = False

def predict_match_result(home_team, away_team, hthg=0, htag=0, hs=5, as_=5, hst=2, ast=2, 
                        hc=3, ac=3, hf=10, af=10, hy=1, ay=1, hr=0, ar=0):
    """
    Predict the outcome of a match between two teams
    
    Parameters are match statistics that affect the prediction:
    - hthg/htag: Half-time goals
    - hs/as_: Shots by each team
    - hst/ast: Shots on target
    - hc/ac: Corner kicks
    - hf/af: Fouls committed
    - hy/ay: Yellow cards
    - hr/ar: Red cards
    
    Returns prediction results including winner and expected score
    """
    
    # Normalize team names to handle variations
    def normalize_team_name(team_name):
        if not team_name:
            return team_name
        # Remove common suffixes
        normalized = team_name.replace(' FC', '').replace(' AFC', '').replace(' FC', '')
        return normalized.strip()
    
    # Normalize team names
    home_team_normalized = normalize_team_name(home_team)
    away_team_normalized = normalize_team_name(away_team)
    
    print(f"Original home team: '{home_team}' -> Normalized: '{home_team_normalized}'")
    print(f"Original away team: '{away_team}' -> Normalized: '{away_team_normalized}'")
    
    # Check if models are loaded
    if not models_loaded or match_winner_model is None:
        return {
            "error": "Prediction models are not available"
        }
    
    try:
        # Convert team names to numbers using our encoders
        if home_team_encoder is not None and away_team_encoder is not None:
            # Try exact match first
            try:
                home_team_encoded = home_team_encoder.transform([home_team])[0]
                away_team_encoded = away_team_encoder.transform([away_team])[0]
            except ValueError:
                # If exact match fails, try normalized names
                try:
                    home_team_encoded = home_team_encoder.transform([home_team_normalized])[0]
                    away_team_encoded = away_team_encoder.transform([away_team_normalized])[0]
                except ValueError:
                    # If normalized names also fail, raise the original error
                    available_home_teams = home_team_encoder.classes_ if home_team_encoder is not None else []
                    available_away_teams = away_team_encoder.classes_ if away_team_encoder is not None else []
                    return {
                        "error": f"Team not found. Available home teams: {list(available_home_teams)[:10]}... Available away teams: {list(available_away_teams)[:10]}..."
                    }
        else:
            return {
                "error": "Team encoders are not available"
            }
    except ValueError as e:
        # Team name not found in our data
        available_home_teams = home_team_encoder.classes_ if home_team_encoder is not None else []
        available_away_teams = away_team_encoder.classes_ if away_team_encoder is not None else []
        return {
            "error": f"Team not found. Available home teams: {list(available_home_teams)[:10]}... Available away teams: {list(available_away_teams)[:10]}..."
        }
    
    # Put all features into an array for our models
    features = np.array([[home_team_encoded, away_team_encoded, hthg, htag, hs, as_, hst, ast, 
                         hc, ac, hf, af, hy, ay, hr, ar]])
    
    # Predict match result (winner)
    if match_winner_model is not None:
        match_result = match_winner_model.predict(features)[0]
    else:
        return {
            "error": "Match winner model is not available"
        }
    
    # Predict exact scores
    if fthg_model is not None and ftag_model is not None:
        fthg_pred = fthg_model.predict(features)[0]
        ftag_pred = ftag_model.predict(features)[0]
    else:
        return {
            "error": "Score prediction models are not available"
        }
    
    # Round to whole numbers since you can't score partial goals
    fthg_pred = round(fthg_pred)
    fthg_pred = max(0, fthg_pred)
    
    ftag_pred = round(ftag_pred)
    ftag_pred = max(0, ftag_pred)
    
    # Prepare the final result - respect the model's original prediction
    # Only override if there's a clear contradiction between the model prediction and scores
    original_match_result = match_result
    
    # Calculate score-based result
    if fthg_pred > ftag_pred:
        score_based_result = 'H'  # Home Win
    elif ftag_pred > fthg_pred:
        score_based_result = 'A'  # Away Win
    else:
        score_based_result = 'D'  # Draw
    
    # Override the model's prediction when there's a clear contradiction with scores
    # Even a 1-goal difference is significant in football
    goal_difference = abs(fthg_pred - ftag_pred)
    
    if original_match_result == 'H' and score_based_result == 'A':
        # Strong contradiction - override
        match_result = 'A'
    elif original_match_result == 'A' and score_based_result == 'H':
        # Strong contradiction - override
        match_result = 'H'
    elif original_match_result == 'D' and score_based_result != 'D':
        # Model predicts draw but scores show a winner - override for any goal difference
        match_result = score_based_result
    elif original_match_result != 'D' and score_based_result == 'D':
        # Model predicts winner but scores show draw - only override if very close
        if goal_difference < 1.5:
            match_result = 'D'
        else:
            # Keep model's prediction if there's a clear goal difference
            match_result = original_match_result
    else:
        # No strong contradiction, keep the model's original prediction
        match_result = original_match_result
    
    return {
        "match_result": match_result,
        "predicted_FTHG": fthg_pred,
        "predicted_FTAG": ftag_pred,
        "predicted_score": f"{fthg_pred} - {ftag_pred}"
    }

def get_available_teams():
    """
    Get lists of team names we can make predictions for
    """
    if home_team_encoder is not None and away_team_encoder is not None:
        home_teams = list(home_team_encoder.classes_)
        away_teams = list(away_team_encoder.classes_)
    else:
        # Return sample teams if encoders are not available
        home_teams = ["Manchester City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham"]
        away_teams = ["Manchester United", "Chelsea", "Newcastle United", "Brighton", "Fulham"]
    
    return {
        "home_teams": home_teams,
        "away_teams": away_teams
    }

# Example usage when running the script directly
if __name__ == "__main__":
    print("ScoreSight Predictor - Example Usage")
    print("=" * 40)
    
    # Show available teams
    teams = get_available_teams()
    print(f"Available home teams: {len(teams['home_teams'])}")
    print(f"Available away teams: {len(teams['away_teams'])}")
    
    # Make a sample prediction
    print("\nExample Prediction:")
    # Use the first available teams for our example
    home_team = teams['home_teams'][0]
    away_team = teams['away_teams'][1]
    
    print(f"Predicting match: {home_team} vs {away_team}")
    result = predict_match_result(home_team, away_team)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        # Convert result codes to readable text
        result_mapping = {
            'H': 'Home Win',
            'A': 'Away Win',
            'D': 'Draw'
        }
        
        print(f"Match Result Prediction: {result_mapping[result['match_result']]}")
        print(f"Exact Score Prediction: {result['predicted_score']}")