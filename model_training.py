import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error
import joblib
import warnings
import traceback
warnings.filterwarnings('ignore')

def prepare_features(df):
    """
    Prepare our data for machine learning by cleaning it up and creating useful features
    """
    # Make a copy so we don't mess with the original data
    data = df.copy()
    
    # Remove any rows with missing values
    data = data.dropna()
    print(f"Data shape after dropping NaN: {data.shape}")
    
    # Create some additional features that might help our predictions
    data['Goal_Difference'] = data['FTHG'] - data['FTAG']  # How many more goals home team scored
    data['Total_Goals'] = data['FTHG'] + data['FTAG']     # Total goals in the match
    data['Home_Shots_Per_Goal'] = data['FTHG'] / (data['HS'] + 1)  # Efficiency of home team shots
    data['Away_Shots_Per_Goal'] = data['FTAG'] / (data['AS'] + 1)  # Efficiency of away team shots
    
    # Convert team names to numbers since machine learning models work with numbers
    le_home = LabelEncoder()
    le_away = LabelEncoder()
    
    data['HomeTeam_encoded'] = le_home.fit_transform(data['HomeTeam'])
    data['AwayTeam_encoded'] = le_away.fit_transform(data['AwayTeam'])
    
    # These are the features we'll use for our predictions
    feature_columns = [
        'HomeTeam_encoded', 'AwayTeam_encoded', 
        'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 
        'HC', 'AC', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR'
    ]
    
    X = data[feature_columns]
    return X, data, le_home, le_away

def train_match_winner_model(df):
    """
    Train a model to predict which team will win the match
    """
    print("Training Match Winner Prediction Model...")
    
    try:
        # Get our prepared features
        X, data, le_home, le_away = prepare_features(df)
        
        # This is what we want to predict - the match result
        y = data['FTR']  # FTR: Full Time Result (H=Home Win, A=Away Win, D=Draw)
        
        print(f"Target variable distribution:\n{y.value_counts()}")
        
        # Split our data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create and train our model
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        # Test how well our model works
        y_pred = clf.predict(X_test)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Match Winner Model Accuracy: {accuracy:.4f}")
        
        # Save our trained model and encoders for later use
        joblib.dump(clf, 'match_winner_model.pkl')
        joblib.dump(le_home, 'home_team_encoder.pkl')
        joblib.dump(le_away, 'away_team_encoder.pkl')
        
        print("Match winner model saved as 'match_winner_model.pkl'")
        
        return clf, le_home, le_away
    except Exception as e:
        print(f"Error in train_match_winner_model: {str(e)}")
        traceback.print_exc()
        return None, None, None

def train_score_prediction_models(df):
    """
    Train models to predict the exact score of the match
    We need two models - one for home team goals and one for away team goals
    """
    print("\nTraining Exact Score Prediction Models...")
    
    try:
        # Get our prepared features
        X, data, le_home, le_away = prepare_features(df)
        
        # Train model for home team goals
        print("Training FTHG Model...")
        y_fthg = data['FTHG']  # Full-Time Home Goals
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_fthg, test_size=0.2, random_state=42)
        
        reg_fthg = RandomForestRegressor(n_estimators=100, random_state=42)
        reg_fthg.fit(X_train, y_train)
        
        y_pred_fthg = reg_fthg.predict(X_test)
        
        # Check how accurate our model is
        mse_fthg = mean_squared_error(y_test, y_pred_fthg)
        mae_fthg = mean_absolute_error(y_test, y_pred_fthg)
        rmse_fthg = np.sqrt(mse_fthg)
        
        print(f"FTHG Model - MSE: {mse_fthg:.4f}, MAE: {mae_fthg:.4f}, RMSE: {rmse_fthg:.4f}")
        
        # Train model for away team goals
        print("Training FTAG Model...")
        y_ftag = data['FTAG']  # Full-Time Away Goals
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_ftag, test_size=0.2, random_state=42)
        
        reg_ftag = RandomForestRegressor(n_estimators=100, random_state=42)
        reg_ftag.fit(X_train, y_train)
        
        y_pred_ftag = reg_ftag.predict(X_test)
        
        # Check how accurate this model is too
        mse_ftag = mean_squared_error(y_test, y_pred_ftag)
        mae_ftag = mean_absolute_error(y_test, y_pred_ftag)
        rmse_ftag = np.sqrt(mse_ftag)
        
        print(f"FTAG Model - MSE: {mse_ftag:.4f}, MAE: {mae_ftag:.4f}, RMSE: {rmse_ftag:.4f}")
        
        # Save our trained models
        joblib.dump(reg_fthg, 'fthg_model.pkl')
        joblib.dump(reg_ftag, 'ftag_model.pkl')
        
        print("Score prediction models saved as 'fthg_model.pkl' and 'ftag_model.pkl'")
        
        return reg_fthg, reg_ftag
    except Exception as e:
        print(f"Error in train_score_prediction_models: {str(e)}")
        traceback.print_exc()
        return None, None

def main():
    """
    Main function that runs our entire training process
    """
    try:
        # Load our combined dataset
        print("Loading unified dataset...")
        df = pd.read_csv('unified_dataset.csv')
        print(f"Dataset loaded with {len(df)} matches")
        
        # Train our match winner prediction model
        clf, le_home, le_away = train_match_winner_model(df)
        
        # Train our score prediction models
        reg_fthg, reg_ftag = train_score_prediction_models(df)
        
        print("\nAll models trained and saved successfully!")
        print("\nModels created:")
        print("1. match_winner_model.pkl - Predicts match winner (Home Win / Away Win / Draw)")
        print("2. fthg_model.pkl - Predicts Full-Time Home Goals")
        print("3. ftag_model.pkl - Predicts Full-Time Away Goals")
        print("4. home_team_encoder.pkl - Encoder for home teams")
        print("5. away_team_encoder.pkl - Encoder for away teams")
    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()

# This runs when we execute the script directly
if __name__ == "__main__":
    main()