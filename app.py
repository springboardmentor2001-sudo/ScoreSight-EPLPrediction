# -------------------------------------------------------
# 🏆 EPL Predictor — Flask App 
# -------------------------------------------------------
import requests
from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
from datetime import datetime
import re
import joblib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import string
import os
import random
import json
from dotenv import load_dotenv
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import google.generativeai as genai

# --- User Authentication Imports ---
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user,
    login_required, current_user
)
from flask_bcrypt import Bcrypt

# -------------------------------------------------------
#  APP INITIALIZATION
# -------------------------------------------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# -------------------------------------------------------
#  USER MODEL (Username + Password)
# -------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------------------------------------
#  LOAD ML MODELS
# -------------------------------------------------------
rf_home = joblib.load(r"C:\Users\sushm\OneDrive\Desktop\Scoresight\models\rf2_home.pkl")
rf_away = joblib.load(r"C:\Users\sushm\OneDrive\Desktop\Scoresight\models\rf2_away.pkl")
print("✅ Models loaded successfully!")

# -------------------------------------------------------
#  TEAM LIST
# -------------------------------------------------------
teams = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
    "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
    "Liverpool", "Luton Town", "Manchester City", "Manchester United",
    "Newcastle United", "Nottingham Forest", "Sheffield United",
    "Tottenham Hotspur", "West Ham United", "Wolverhampton"
]

# -------------------------------------------------------
#  AUTHENTICATION ROUTES
# -------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("⚠️ Username already taken! Please choose another.", "warning")
            return redirect(url_for('signup'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("✅ Account created! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.username}! 🎉", "success")
            return redirect(url_for('home'))
        else:
            flash("❌ Invalid username or password.", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", "info")
    return redirect(url_for('login'))

# -------------------------------------------------------
# MAIN ROUTES (Protected)
# -------------------------------------------------------
@app.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)
# -------------------------------------------------------
# API: Upcoming Matches
# -------------------------------------------------------
FD_API_KEY = os.getenv("FD_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

@app.route("/matches")
def get_matches():
    fd_url = "https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED"
    headers_fd = {"X-Auth-Token": FD_API_KEY}

    fd_response = requests.get(fd_url, headers=headers_fd)
    fd_data = fd_response.json()
    fd_matches = fd_data.get("matches", [])

    matches_data = []
    for match in fd_matches[:5]:
        matches_data.append({
            "homeTeam": match["homeTeam"]["name"],
            "awayTeam": match["awayTeam"]["name"],
            "utcDate": match["utcDate"][:10],
            "status": "Upcoming",
            "score": "-"
        })

    return render_template("matches.html", matches=matches_data)

# -------------------------------------------------------
# Matches insights 
# -------------------------------------------------------
@app.route("/match_insights", methods=["GET"])
def match_insights():
    try:
        # Alphabetical dropdown list
        teams = sorted([
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
            "Liverpool", "Luton Town", "Manchester City", "Manchester United",
            "Newcastle United", "Nottingham Forest", "Sheffield United",
            "Tottenham Hotspur", "West Ham United", "Wolverhampton"
        ])

        # Map dropdown names → API names
        team_name_map = {
            "Arsenal": "Arsenal FC",
            "Aston Villa": "Aston Villa FC",
            "Bournemouth": "AFC Bournemouth",
            "Brentford": "Brentford FC",
            "Brighton": "Brighton & Hove Albion FC",
            "Burnley": "Burnley FC",
            "Chelsea": "Chelsea FC",
            "Crystal Palace": "Crystal Palace FC",
            "Everton": "Everton FC",
            "Fulham": "Fulham FC",
            "Liverpool": "Liverpool FC",
            "Luton Town": "Luton Town FC",
            "Manchester City": "Manchester City FC",
            "Manchester United": "Manchester United FC",
            "Newcastle United": "Newcastle United FC",
            "Nottingham Forest": "Nottingham Forest FC",
            "Sheffield United": "Sheffield United FC",
            "Tottenham Hotspur": "Tottenham Hotspur FC",
            "West Ham United": "West Ham United FC",
            "Wolverhampton": "Wolverhampton Wanderers FC"
        }

        selected_team = request.args.get("team_name")
        stats = None

        if selected_team:
            api_team_name = team_name_map.get(selected_team)

            r = requests.get(f"{FD_BASE_URL}/standings", headers=headers_fd)
            data = r.json()
            standings = data["standings"][0]["table"]

            team_stats = next(
                (t for t in standings if t["team"]["name"] == api_team_name),
                None
            )

            if team_stats:
                stats = {
                    "played": team_stats["playedGames"],
                    "wins": team_stats["won"],
                    "draws": team_stats["draw"],
                    "losses": team_stats["lost"],
                    "goals_for": team_stats["goalsFor"],
                    "goals_against": team_stats["goalsAgainst"]
                }

        return render_template("match_insights.html", teams=teams, team=selected_team, stats=stats, error=None)

    except Exception as e:
        print("❌ Match Insights Error:", e)
        return render_template("match_insights.html", teams=teams, team=None, stats=None, error="Could not fetch match insights. Try again later.")

# -------------------------------------------------------
# HALF TIME 
# -------------------------------------------------------
@app.route('/halftime', methods=['GET', 'POST'])
@login_required
def halftime():
    if request.method == 'GET':
        return render_template('half_time.html', teams=teams)

    try:
        home_team = request.form['home_team']
        away_team = request.form['away_team']

        features = [
            float(request.form['HS']), float(request.form['AS']),
            float(request.form['HST']), float(request.form['AST']),
            float(request.form['HF']), float(request.form['AF']),
            float(request.form['HC']), float(request.form['AC']),
            float(request.form['HY']), float(request.form['AY']),
            float(request.form['HR']), float(request.form['AR'])
        ]
        while len(features) < 17:
            features.append(0.0)

        features = np.array(features).reshape(1, -1)
        home_goals = rf_home.predict(features)[0]
        away_goals = rf_away.predict(features)[0]

        if home_goals > away_goals:
            result = f"{home_team} (Home)"
            home_prob, draw_prob, away_prob = 65, 5, 30
        elif away_goals > home_goals:
            result = f"{away_team} (Away)"
            home_prob, draw_prob, away_prob = 30, 5, 65
        else:
            result = "Draw"
            home_prob, draw_prob, away_prob = 45, 10, 45

        plt.figure(facecolor='white')
        plt.pie([home_prob, draw_prob, away_prob],
                labels=['Home', 'Draw', 'Away'],
                autopct='%1.1f%%', startangle=90)
        os.makedirs('static', exist_ok=True)
        plt.savefig(os.path.join('static', 'half_pie.png'))
        plt.close()

        return render_template(
            'half_time_result.html',
            home_team=home_team, away_team=away_team,
            hthg=round(home_goals, 2), htag=round(away_goals, 2),
            result=result,
            home_prob=home_prob, draw_prob=draw_prob, away_prob=away_prob
        )
    except Exception as e:
        return f"Error during half-time prediction: {e}"
    
# -------------------------------------------------------
#  FULL TIME 
# -------------------------------------------------------
@app.route('/fulltime', methods=['GET', 'POST'])
@login_required
def fulltime():
    if request.method == 'GET':
        return render_template('full_time.html', teams=teams)

    try:
        home_team = request.form['home_team']
        away_team = request.form['away_team']
        ht_home = float(request.form.get('ht_home', 0))
        ht_away = float(request.form.get('ht_away', 0))

        features = [ht_home, ht_away]
        while len(features) < 17:
            features.append(0.0)
        features = np.array(features).reshape(1, -1)

        ft_home_pred = rf_home.predict(features)[0]
        ft_away_pred = rf_away.predict(features)[0]
        ft_home = ht_home + ft_home_pred
        ft_away = ht_away + ft_away_pred

        if ft_home > ft_away:
            result = f"{home_team} (Home)"
            home_prob, draw_prob, away_prob = 70, 20, 10
        elif ft_away > ft_home:
            result = f"{away_team} (Away)"
            home_prob, draw_prob, away_prob = 10, 20, 70
        else:
            result = "Draw"
            home_prob, draw_prob, away_prob = 33, 34, 33

        plt.figure(facecolor='white')
        plt.pie([home_prob, draw_prob, away_prob],
                labels=['Home Win', 'Draw', 'Away Win'],
                autopct='%1.1f%%', startangle=90,
                colors=['#38b000', '#ffb703', '#d62828'])
        plt.axis('equal')

        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        chart_img = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()

        return render_template(
            'full_time_result.html',
            home_team=home_team, away_team=away_team,
            hthg=int(ht_home), htag=int(ht_away),
            ft_home=int(ft_home), ft_away=int(ft_away),
            result=result,
            home_prob=home_prob, draw_prob=draw_prob, away_prob=away_prob,
            chart_img=chart_img
        )
    except Exception as e:
        return f"Error during full-time prediction: {e}"
    
# -------------------------------------------------------
#  ABOUT 
# -------------------------------------------------------
@app.route('/about')
def about():
    return render_template('about.html')

# -------------------------------------------------------
# FIXTURES 
# -------------------------------------------------------
DATA_PATH = r"C:\Users\sushm\OneDrive\Desktop\Scoresight\Dataset of epl\EPL_features.csv"
LOGO_PATH = r"C:\Users\sushm\OneDrive\Desktop\Scoresight\static\team_logo"

TEAM_NAME_MAP = {
    "man city": "Manchester City",
    "man united": "Manchester United",
    "wolves": "Wolverhampton",
    "spurs": "Tottenham Hotspur",
    "newcastle": "Newcastle United",
    "forest": "Nottingham Forest",
    "brighton": "Brighton",
    "villa": "Aston Villa",
    "sheff utd": "Sheffield United",
    "luton": "Luton Town",
}


@app.route('/fixtures')
def fixtures_page():
    # Read dataset
    df = pd.read_csv(DATA_PATH, parse_dates=['Date'])
    df['HomeTeam'] = df['HomeTeam'].apply(lambda x: TEAM_NAME_MAP.get(str(x).lower(), x))
    df['AwayTeam'] = df['AwayTeam'].apply(lambda x: TEAM_NAME_MAP.get(str(x).lower(), x))

    teams = sorted(df['HomeTeam'].unique())
    selected_team = request.args.get('team', 'All Teams')

    # Filter fixtures
    if selected_team != "All Teams":
        df_filtered = df[(df['HomeTeam'] == selected_team) | (df['AwayTeam'] == selected_team)]
    else:
        df_filtered = df.copy()

    # Sort and format
    df_filtered = df_filtered[['Date', 'HomeTeam', 'AwayTeam', 'FTR']].sort_values('Date')
    df_filtered['Date'] = df_filtered['Date'].dt.strftime('%Y-%m-%d')

    # Match team logos
    team_logos = {}
    for team in teams:
        team_lower = team.replace(" ", "").lower()
        found = None
        for file in os.listdir(LOGO_PATH):
            file_lower = file.replace(" ", "").replace("_", "").lower()
            if team_lower in file_lower:
                found = file
                break
        team_logos[team] = found

    return render_template(
        "fixtures.html",
        teams=teams,
        selected_team=selected_team,
        fixtures=df_filtered.to_dict(orient='records'),
        team_logos=team_logos
    )


@app.route('/get_logo/<team>')
def get_logo_api(team):
    logo_folder = os.path.join('static', 'team_logo')
    team_clean = re.sub(r'[^a-z0-9]', '', team.lower())

    for file in os.listdir(logo_folder):
        file_clean = re.sub(r'[^a-z0-9]', '', file.lower().replace('.svg', ''))
        if team_clean in file_clean:
            return jsonify({'logo': url_for('static', filename=f'team_logo/{file}')})
    return jsonify({'logo': None})

# -------------------------------------------------------
# CHATBOT ROUTES
# -------------------------------------------------------
# Get API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

# Configure Gemini

from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Football Data API
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

# ---------------- CHATBOT ROUTES ----------------
@app.route("/chat")
def chat():
    return render_template("chat.html")


from datetime import datetime, timedelta
import pytz

@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        user_input = request.json.get("message", "").strip()
        user_input_clean = user_input.translate(str.maketrans('', '', string.punctuation)).lower()
        print("🗣 User said:", user_input_clean)

        reply = None

        # Load environment keys
        FD_API_KEY = os.getenv("FD_API_KEY")
        API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        # API URLs & headers
        FD_BASE_URL = "https://api.football-data.org/v4/competitions/PL"
        headers_fd = {"X-Auth-Token": FD_API_KEY}

        API_BASE_URL = "https://v3.football.api-sports.io"
        headers_api = {"x-apisports-key": API_FOOTBALL_KEY}

        # Helper: Convert UTC → IST
        def utc_to_ist(utc_time_str):
            try:
                utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S%z")
                ist_time = utc_time.astimezone(pytz.timezone("Asia/Kolkata"))
                return ist_time.strftime("%Y-%m-%d %I:%M %p")
            except Exception:
                return utc_time_str

        # ---------------- BASIC GREETINGS ----------------
        if user_input_clean in ["hi", "hello", "hey", "yo", "hii", "hiii"]:
            reply = "Hey there! 👋 Ready for some football talk?"
        elif user_input_clean in ["bye", "goodbye", "see you", "bye bye"]:
            reply = "Goodbye! ⚽ Catch you after the next match!"

        # ---------------- LIVE MATCHES (Premier League only) ----------------
        elif any(word in user_input_clean for word in ["live", "score", "ongoing", "current match", "match today"]):
            r = requests.get(f"{API_BASE_URL}/fixtures?live=all", headers=headers_api)
            data = r.json()

            live_matches = [
                m for m in data.get("response", [])
                if m["league"]["name"].lower() == "premier league"
            ]

            if live_matches:
                m = live_matches[0]
                home = m["teams"]["home"]["name"]
                away = m["teams"]["away"]["name"]
                score_home = m["goals"]["home"]
                score_away = m["goals"]["away"]
                minute = m["fixture"]["status"]["elapsed"]
                reply = f"⚽ Live now: {home} {score_home} - {score_away} {away} ({minute}’)"
            else:
                reply = "No Premier League matches live right now ⏳"

        # ---------------- PREVIOUS MATCH ----------------
        elif any(word in user_input_clean for word in ["previous", "last match", "recent match"]):
            r = requests.get(f"{FD_BASE_URL}/matches?status=FINISHED", headers=headers_fd)
            data = r.json()
            matches = data.get("matches", [])
            if matches:
                m = matches[-1]
                reply = f"📅 Last Match: {m['homeTeam']['name']} {m['score']['fullTime']['home']} - {m['score']['fullTime']['away']} {m['awayTeam']['name']}"
            else:
                reply = "No finished matches found recently 🤔"

        # ---------------- NEXT MATCH (IST formatted) ----------------
        elif any(word in user_input_clean for word in ["next match", "upcoming", "fixture", "future match"]):
            r = requests.get(f"{FD_BASE_URL}/matches?status=SCHEDULED", headers=headers_fd)
            data = r.json()
            matches = data.get("matches", [])
            if matches:
                m = matches[0]
                date_utc = m["utcDate"].replace("Z", "+00:00")
                date_ist = utc_to_ist(date_utc)
                reply = f"📆 Next Match: {m['homeTeam']['name']} vs {m['awayTeam']['name']} on {date_ist} (IST)"
            else:
                reply = "No upcoming matches found 📭"

        # ---------------- LAST SEASON WINNER ----------------
        elif "who won" in user_input_clean and "last" in user_input_clean:
            try:
                r = requests.get(f"{FD_BASE_URL}/standings?season=2023", headers=headers_fd)
                data = r.json()
                winner = data["standings"][0]["table"][0]["team"]["name"]
                reply = f"🏆 {winner} won the Premier League 2023–24 season!"
            except Exception:
                reply = "Couldn’t fetch last season’s winner 😕"

        # ---------------- STANDINGS ----------------
        elif any(word in user_input_clean for word in ["table", "standings", "top 5", "top teams"]):
            r = requests.get(f"{FD_BASE_URL}/standings", headers=headers_fd)
            data = r.json()
            table = data["standings"][0]["table"][:5]
            reply = "🏆 Top 5 Teams:\n" + "\n".join(
                [f"{t['position']}. {t['team']['name']} ({t['points']} pts)" for t in table]
            )

        # ---------------- NON-FOOTBALL TOPICS ----------------
        elif any(word in user_input_clean for word in [
            "weather", "movie", "news", "food", "song", "music", "joke", "time"
        ]):
            reply = "I’m all about football ⚽! Try asking about matches, teams, or standings."

        # ---------------- GEMINI FALLBACK ----------------
        else:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            response = model.generate_content(
                f"Act like a fun football chatbot. User said: '{user_input_clean}'. Reply casually and briefly about football only."
            )
            reply = response.text

        print("🤖 Reply:", reply)
        return jsonify({"response": reply})

    except Exception as e:
        print("❌ Server Error:", e)
        return jsonify({"response": "⚠️ Internal error, please try again later."})
# -------------------------------------------------------
#  RUN APP 
# -------------------------------------------------------
if __name__ == "__main__":
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
