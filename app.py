from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# ================== Load Models & Encoders ==================
away_goals_model = pickle.load(open('models/away_goals_model (1).pkl', 'rb'))
home_goals_model = pickle.load(open('models/home_goals_model (1).pkl', 'rb'))
result_encoder = pickle.load(open('models/result_encoder.pkl', 'rb'))
team_encoder = pickle.load(open('models/team_encoder.pkl', 'rb'))
winner_model = pickle.load(open('models/winner_model (1).pkl', 'rb'))

# ====================== Dataset Path ======================
DATA_CSV = os.path.join('dataset', 'epl_final.csv')

# ====================== Get All Teams ======================
def get_team_list():
    """Fetch all unique team names from dataset or use default list"""
    if not os.path.exists(DATA_CSV):
        return sorted([
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
            "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds",
            "Leicester", "Liverpool", "Man City", "Man United", "Newcastle",
            "Nottingham Forest", "Southampton", "Tottenham", "Wolves", "West Ham"
        ])
    df = pd.read_csv(DATA_CSV)
    teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).dropna().unique()
    return sorted([t for t in teams])

# ====================== Home Route ======================
@app.route('/')
def home():
    teams = get_team_list()
    return render_template('index.html', teams=teams)

# ====================== Predict Route ======================
@app.route('/predict', methods=['POST'])
def predict():
    # --- Get user inputs ---
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    match_date = request.form.get('match_date')

    if not home_team or not away_team or not match_date:
        return "<h3>Please select all fields (Home, Away, and Date)</h3>"

    # --- Convert date to numeric ---
    date_obj = datetime.strptime(match_date, "%Y-%m-%d")
    match_year, match_month, match_day = date_obj.year, date_obj.month, date_obj.day

    # --- Encode teams ---
    try:
        home_enc = team_encoder.transform([home_team])[0]
        away_enc = team_encoder.transform([away_team])[0]
    except Exception:
        return render_template(
            'result.html',
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            winner="⚠️ Unknown team name",
            home_goals="-",
            away_goals="-",
            home_win_prob=0,
            away_win_prob=0
        )

    # --- Prepare numeric features ---
    features = np.array([[home_enc, away_enc, match_year, match_month, match_day,
                          float(request.form['HS']), float(request.form['AS']),
                          float(request.form['HST']), float(request.form['AST']),
                          float(request.form['HF']), float(request.form['AF']),
                          float(request.form['HY']), float(request.form['AY']),
                          float(request.form['HR']), float(request.form['AR'])]])

    # --- Predict goals ---
    home_goals = round(home_goals_model.predict(features)[0])
    away_goals = round(away_goals_model.predict(features)[0])

    # --- Predict winner (classification model) ---
    winner_pred = winner_model.predict(features)[0]
    winner_label = result_encoder.inverse_transform([winner_pred])[0]

    # --- Decide final winner for UI ---
    if home_goals > away_goals:
        winner = f"{home_team} Wins 🏆"
    elif away_goals > home_goals:
        winner = f"{away_team} Wins 🥇"
    else:
        winner = "Match Draw 🤝"

    # --- Calculate probabilities (corrected) ---
    
    
            # Initialize probabilities
            
        home_win_prob, draw_prob, away_win_prob = 0, 0, 0
        
    if hasattr(winner_model, "predict_proba"):
        probs = winner_model.predict_proba(features)[0]
        label_map = dict(zip(result_encoder.classes_, probs))  # dynamic mapping
        
        # Assign safely (if label missing, default 0)
        home_win_prob = round(float(label_map.get('H', 0)) * 100, 2)
        draw_prob = round(float(label_map.get('D', 0)) * 100, 2)
        away_win_prob = round(float(label_map.get('A', 0)) * 100, 2)
       
    # --- Render result page ---
    return render_template(
        'result.html',
        home_team=home_team,
        away_team=away_team,
        match_date=match_date,
        winner=winner,
        home_goals=home_goals,
        away_goals=away_goals,
        home_win_prob=home_win_prob,
        away_win_prob=away_win_prob,
        draw_prob=draw_prob  # ✅ add this
    )

# ====================== Run App ======================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render port environment variable
    app.run(host='0.0.0.0', port=port, debug=False)
