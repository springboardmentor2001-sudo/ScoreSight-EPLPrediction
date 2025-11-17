import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def create_placeholder_models():
    """
    Create placeholder models to prevent the application from crashing
    """
    print("Creating placeholder models...")
    
    # Create sample data for training
    teams = ['Arsenal', 'Man City', 'Liverpool', 'Chelsea', 'Man United', 
             'Tottenham', 'Newcastle', 'Aston Villa', 'Brighton', 'West Ham',
             'Crystal Palace', 'Leicester', 'Wolves', 'Everton', 'Leeds United',
             'Southampton', 'Brentford', 'Bournemouth', 'Nottingham Forest', 'Fulham']
    
    # Create a sample dataset
    sample_data = []
    for i in range(1000):
        match = {
            'HomeTeam': np.random.choice(teams),
            'AwayTeam': np.random.choice([t for t in teams if t != np.random.choice(teams)]),
            'HTHG': np.random.randint(0, 3),
            'HTAG': np.random.randint(0, 3),
            'HTR': np.random.choice(['H', 'A', 'D']),
            'FTHG': np.random.randint(0, 5),
            'FTAG': np.random.randint(0, 5),
            'FTR': np.random.choice(['H', 'A', 'D']),
            'HS': np.random.randint(5, 20),
            'AS': np.random.randint(5, 20),
            'HST': np.random.randint(2, 10),
            'AST': np.random.randint(2, 10),
            'HC': np.random.randint(1, 8),
            'AC': np.random.randint(1, 8),
            'HF': np.random.randint(5, 20),
            'AF': np.random.randint(5, 20),
            'HY': np.random.randint(0, 5),
            'AY': np.random.randint(0, 5),
            'HR': np.random.randint(0, 2),
            'AR': np.random.randint(0, 2)
        }
        sample_data.append(match)
    
    df = pd.DataFrame(sample_data)
    
    # Create encoders
    le_home = LabelEncoder()
    le_away = LabelEncoder()
    
    df['HomeTeam_encoded'] = le_home.fit_transform(df['HomeTeam'])
    df['AwayTeam_encoded'] = le_away.fit_transform(df['AwayTeam'])
    
    # Feature columns
    feature_columns = [
        'HomeTeam_encoded', 'AwayTeam_encoded', 
        'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 
        'HC', 'AC', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR'
    ]
    
    X = df[feature_columns]
    
    # Create and train placeholder models
    # Match winner model
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, df['FTR'])
    joblib.dump(clf, 'match_winner_model.pkl')
    
    # Home team goals model
    reg_fthg = RandomForestRegressor(n_estimators=10, random_state=42)
    reg_fthg.fit(X, df['FTHG'])
    joblib.dump(reg_fthg, 'fthg_model.pkl')
    
    # Away team goals model
    reg_ftag = RandomForestRegressor(n_estimators=10, random_state=42)
    reg_ftag.fit(X, df['FTAG'])
    joblib.dump(reg_ftag, 'ftag_model.pkl')
    
    # Save encoders
    joblib.dump(le_home, 'home_team_encoder.pkl')
    joblib.dump(le_away, 'away_team_encoder.pkl')
    
    print("Placeholder models created successfully!")

if __name__ == "__main__":
    create_placeholder_models()