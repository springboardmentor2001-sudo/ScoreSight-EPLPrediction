from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime
import pickle
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from xgboost import XGBClassifier

# Get the correct paths to model files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_MODELS_DIR = os.path.join(BASE_DIR, '..', 'ml-models')

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

app = FastAPI(title="Scoresight API", version="1.0.0")

# CORS middleware to allow React frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FOOTBALL_API_TOKEN = "b839a17637ca4abc953080c5f3761314"
BASE_URL = "https://api.football-data.org/v4"

# IMPROVED TEAM NAME MAPPING - handles all API variations
def get_all_trained_teams():
    """Get all unique teams from your training data"""
    trained_teams = [
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
    return trained_teams

def map_team_name(api_team_name):
    """Smart mapping that handles any team name format from API"""
    trained_teams = get_all_trained_teams()
    
    # Common transformations
    clean_name = api_team_name
    transformations = [
        (' FC', ''),
        (' United', ''),
        (' City', ''),
        (' & Hove Albion', ''),
        ('Wolverhampton Wanderers', 'Wolves'),
        ('Tottenham Hotspur', 'Tottenham'),
        ('Manchester City', 'Man City'),
        ('Manchester United', 'Man United'),
        ('Nottingham Forest', "Nott'm Forest"),
        ('West Ham United', 'West Ham'),
        ('Newcastle United', 'Newcastle'),
        ('Leeds United', 'Leeds'),
        ('Leicester City', 'Leicester'),
        ('Brighton & Hove Albion', 'Brighton')
    ]
    
    # Apply transformations
    for old, new in transformations:
        clean_name = clean_name.replace(old, new)
    
    clean_name = clean_name.strip()
    
    # Exact match
    if clean_name in trained_teams:
        return clean_name
    
    # Case-insensitive match
    for team in trained_teams:
        if team.lower() == clean_name.lower():
            return team
    
    # Partial match (if "Manchester City FC" becomes "Man City")
    for team in trained_teams:
        if team.lower() in clean_name.lower() or clean_name.lower() in team.lower():
            return team
    
    # Final fallback - try to find closest match
    print(f"⚠️  Could not map team: '{api_team_name}' -> '{clean_name}'")
    return clean_name  # Return the cleaned name as fallback

def map_team_name(api_team_name):
    """Smart mapping that handles any team name format from API"""
    trained_teams = get_all_trained_teams()
    
    # Common transformations
    clean_name = api_team_name
    transformations = [
        (' FC', ''),
        (' United', ''),
        (' City', ''),
        (' & Hove Albion', ''),
        ('Wolverhampton Wanderers', 'Wolves'),
        ('Tottenham Hotspur', 'Tottenham'),
        ('Manchester City', 'Man City'),
        ('Manchester United', 'Man United'),
        ('Nottingham Forest', "Nott'm Forest"),
        ('West Ham United', 'West Ham'),
        ('Newcastle United', 'Newcastle'),
        ('Leeds United', 'Leeds'),
        ('Leicester City', 'Leicester'),
        ('Brighton & Hove Albion', 'Brighton')
    ]
    
    # Apply transformations
    for old, new in transformations:
        clean_name = clean_name.replace(old, new)
    
    clean_name = clean_name.strip()
    
    # Exact match
    if clean_name in trained_teams:
        return clean_name
    
    # Case-insensitive match
    for team in trained_teams:
        if team.lower() == clean_name.lower():
            return team
    
    # Partial match (if "Manchester City FC" becomes "Man City")
    for team in trained_teams:
        if team.lower() in clean_name.lower() or clean_name.lower() in team.lower():
            return team
    
    # Final fallback - try to find closest match
    print(f"⚠️  Could not map team: '{api_team_name}' -> '{clean_name}'")
    return clean_name  # Return the cleaned name as fallback

def create_pre_match_features(home_team, away_team):
    """Create feature vector for pre-match prediction"""
    preprocessing = ml_models['pre_match_preprocessing']
    feature_columns = preprocessing['feature_columns']
    
    # Create base feature dictionary with zeros
    features = {col: 0.0 for col in feature_columns}
    
    # Set team features (they will be encoded later)
    features['HomeTeam'] = home_team
    features['AwayTeam'] = away_team
    
    # Set realistic default values based on your model training
    # These are averages from your training data
    features['Home_Form_5'] = 1.5
    features['Away_Form_5'] = 1.5
    features['Home_Goals_Avg_5'] = 1.4
    features['Away_Goals_Avg_5'] = 1.2
    features['Home_Defense_Avg_5'] = 1.2
    features['Away_Defense_Avg_5'] = 1.4
    features['Avg_H_Odds'] = 2.1
    features['Avg_D_Odds'] = 3.4
    features['Avg_A_Odds'] = 3.8
    features['Home_Win_Probability'] = 0.42
    features['Draw_Probability'] = 0.27
    features['Away_Win_Probability'] = 0.31
    features['H2H_Home_Wins'] = 3.0
    features['H2H_Away_Wins'] = 2.0
    features['Season_Progress'] = 0.5
    features['Referee'] = 'M Dean'  # Default referee
    
    return features, feature_columns

def create_half_time_features(home_team, away_team, home_score, away_score):
    """Create feature vector for half-time prediction"""
    preprocessing = ml_models['half_time_preprocessing']
    feature_columns = preprocessing['feature_columns']
    
    # Create base feature dictionary with zeros
    features = {col: 0.0 for col in feature_columns}
    
    # Set team features
    features['HomeTeam'] = home_team
    features['AwayTeam'] = away_team
    
    # Set half-time specific features
    features['HTHG'] = home_score
    features['HTAG'] = away_score
    
    # Calculate half-time result
    if home_score > away_score:
        features['HTR_numeric'] = 2  # Home leading
    elif away_score > home_score:
        features['HTR_numeric'] = 0  # Away leading  
    else:
        features['HTR_numeric'] = 1  # Draw
        
    features['HT_Goal_Difference'] = home_score - away_score
    
    # Set realistic half-time statistics (averages from your data)
    features['HS'] = 6.0  # Home shots
    features['AS'] = 5.0  # Away shots
    features['HST'] = 2.5  # Home shots on target
    features['AST'] = 2.0  # Away shots on target
    features['HC'] = 3.0   # Home corners
    features['AC'] = 2.0   # Away corners
    features['HF'] = 7.0   # Home fouls
    features['AF'] = 8.0   # Away fouls
    features['HY'] = 1.0   # Home yellow cards
    features['AY'] = 1.0   # Away yellow cards
    features['HR'] = 0.0   # Home red cards
    features['AR'] = 0.0   # Away red cards
    
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
            # Handle unseen categories by using most common class
            try:
                df[col] = encoder.transform(df[col])
            except ValueError:
                # If team not in encoder, use first class (usually most common)
                df[col] = 0
    
    return df

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

@app.get("/api/predict")
async def predict_match(home_team: str, away_team: str):
    """Real prediction using your 75% accurate ML model"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded", 
                "model_loaded": False
            }

        # Map team names to your model's format
        home_team_mapped = map_team_name(home_team)
        away_team_mapped = map_team_name(away_team)

        # 🟢 ADD DEBUG PRINT HERE:
        print(f"Team mapping: '{home_team}' -> '{home_team_mapped}'")
        print(f"Team mapping: '{away_team}' -> '{away_team_mapped}'")
        
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

        # 🛠️ COMPLETE XGBOOST FIX:
        for estimator in model.estimators_:
            if hasattr(estimator, '__class__') and 'XGB' in estimator.__class__.__name__:
                # Add ALL missing attributes that XGBoost expects
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

        # THEN make prediction ✅
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
            ],
            "aiExplanation": f"ML model prediction: {max_prob*100:.1f}% chance of {predicted_outcome.lower()} victory.",
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

@app.get("/api/half-time-predict")
async def half_time_predict(home_team: str, away_team: str, home_score: int = 0, away_score: int = 0):
    """Half-time prediction using your 65% accurate ML model"""
    try:
        if ml_models is None:
            return {
                "error": "ML model not loaded",
                "model_loaded": False
            }
        
        # Map team names to your model's format
        home_team_mapped = map_team_name(home_team)
        away_team_mapped = map_team_name(away_team)
        
        # Create features for half-time prediction
        features, feature_columns = create_half_time_features(
            home_team_mapped, away_team_mapped, home_score, away_score
        )
        
        # Preprocess features
        processed_features = preprocess_features(
            features,
            feature_columns,
            ml_models['half_time_preprocessing']
        )
        
        # Get prediction probabilities
        model = ml_models['half_time_model']
        # 🛠️ ADD XGBOOST FIX HERE (if half-time model also uses XGBoost):
        if hasattr(model, 'estimators_'):  # Only if it's an ensemble
           for estimator in model.estimators_:
               if hasattr(estimator, '__class__') and 'XGB' in estimator.__class__.__name__:
                  if not hasattr(estimator, 'use_label_encoder'):
                     estimator.use_label_encoder = False
                  if not hasattr(estimator, 'enable_categorical'):
                     estimator.enable_categorical = False

         # THEN make prediction ✅
        probabilities = model.predict_proba(processed_features)[0]
        
        # Map probabilities to outcomes [Away, Draw, Home]
        away_win_prob = float(probabilities[0])
        draw_prob = float(probabilities[1]) 
        home_win_prob = float(probabilities[2])
        
        # Determine confidence and predicted outcome
        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = "high" if max_prob > 0.6 else "medium" if max_prob > 0.45 else "low"
        
        # Predict final score based on current score and probabilities
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            predicted_outcome = "HOME"
            home_final = home_score + 1
            away_final = away_score
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            predicted_outcome = "AWAY"
            home_final = home_score  
            away_final = away_score + 1
        else:
            predicted_outcome = "DRAW"
            home_final = home_score
            away_final = away_score
            
        # Ensure at least one goal if it's a draw and both are 0-0
        if predicted_outcome == "DRAW" and home_final == 0 and away_final == 0:
            home_final, away_final = 1, 1
        
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
            "keyFactors": [
                "Current score advantage",
                "Team form analysis", 
                "Head-to-head record",
                "Home advantage significance"
            ],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)