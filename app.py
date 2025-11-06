from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from dotenv import load_dotenv

# -------------------------------
# Load environment variables first
# -------------------------------
load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key_123")

# ✅ Define API_URL immediately here
API_URL = "https://v3.football.api-sports.io/fixtures?live=all"

# -------------------------------
# Initialize Flask app immediately
# -------------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY  # ✅ set before anything else
# -------------------------------
# Import remaining modules
# -------------------------------
import pickle
import pandas as pd
from module import log_user_activity, create_logs_table, create_users_table
import requests
import numpy as np
import google.generativeai as genai
import json
import io
import base64
import matplotlib.pyplot as plt
from datetime import datetime
from database import get_db_connection

# Create tables after app setup
create_users_table()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel("models/gemini-2.5-flash")


# -------------------------------
# Load saved models and objects
# -------------------------------
model_path = "models"

# Fulltime Random Forest model
with open(os.path.join(model_path, "Best_Model_Random_Forest.pkl"), "rb") as f:
    fulltime_model = pickle.load(f)

with open(os.path.join(model_path, "Scaler.pkl"), "rb") as f:
    fulltime_scaler = pickle.load(f)

with open(os.path.join(model_path, "Feature_Columns.pkl"), "rb") as f:
    fulltime_feature_columns = pickle.load(f)

with open(os.path.join(model_path, "HomeTeam_Encoder.pkl"), "rb") as f:
    home_encoder = pickle.load(f)

with open(os.path.join(model_path, "AwayTeam_Encoder.pkl"), "rb") as f:
    away_encoder = pickle.load(f)

# -----------------
# Full-time models
# -----------------
with open(os.path.join(model_path, "home_goals_model.pkl"), "rb") as f:
    home_goals_model = pickle.load(f)

with open(os.path.join(model_path, "away_goals_model.pkl"), "rb") as f:
    away_goals_model = pickle.load(f)

with open(os.path.join(model_path, "goals_scaler.pkl"), "rb") as f:
    goals_scaler = pickle.load(f)  # renamed from 'scaler'

with open(os.path.join(model_path, "Goal_Feature_Columns.pkl"), "rb") as f:
    goal_feature_columns = pickle.load(f)  # renamed

with open(os.path.join(model_path, "HomeTeam_Encoder.pkl"), "rb") as f:
    home_team_encoder = pickle.load(f)  # renamed

with open(os.path.join(model_path, "AwayTeam_Encoder.pkl"), "rb") as f:
    away_team_encoder = pickle.load(f)  # renamed

# -----------------
# Half-time models
# -----------------
with open(os.path.join(model_path, "HalfTime_HomeGoals_Model.pkl"), "rb") as f:
    halftime_home_model = pickle.load(f)

with open(os.path.join(model_path, "HalfTime_AwayGoals_Model.pkl"), "rb") as f:
    halftime_away_model = pickle.load(f)

with open(os.path.join(model_path, "HalfTime_Scaler.pkl"), "rb") as f:
    halftime_scaler = pickle.load(f)  # renamed from 'scaler'

with open(os.path.join(model_path, "HalfTime_HomeTeam_Encoder.pkl"), "rb") as f:
    halftime_home_encoder = pickle.load(f)  # renamed

with open(os.path.join(model_path, "HalfTime_AwayTeam_Encoder.pkl"), "rb") as f:
    halftime_away_encoder = pickle.load(f)  # renamed

with open(os.path.join(model_path, "HalfTime_Feature_Columns.pkl"), "rb") as f:
    halftime_feature_columns = pickle.load(f)  # renamed
    
team_stats_path = os.path.join(os.path.dirname(__file__), "team_stats.json")

if os.path.exists(team_stats_path):
    with open(team_stats_path, "r") as f:
        team_stats = json.load(f)
    print(f"✅ Loaded {len(team_stats)} teams from team_stats.json")
else:
    print("⚠️ team_stats.json not found. Using defaults.")
    team_stats = {}
    
csv_path = os.path.join(os.path.dirname(__file__), "2010-2020.csv")

if os.path.exists(csv_path):
    df_stats = pd.read_csv(csv_path)
    df_stats.columns = df_stats.columns.str.strip().str.replace(" ", "_")
    print(f"✅ Loaded stats CSV with {len(df_stats)} matches")
else:
    print("⚠️ CSV file not found — match stats will be unavailable.")
    df_stats = pd.DataFrame()
    
real_stats = {
    "num_seasons": "33 (since 1992–93)",
    "num_teams": "50+ teams have participated",
    "most_champions": "Manchester United (13 titles)",
    "current_champion": "Manchester City (2024–25 season)",
    "most_goals_team": "Manchester City (100+ goals in 2017–18)",
    "top_scorer": "Erling Haaland (36 goals in 2022–23 season)"
}
    
teams = [
    "Arsenal", "Aston Villa", "Birmingham", "Blackburn", "Blackpool", "Bolton",
    "Bournemouth", "Brighton", "Burnley", "Cardiff", "Chelsea", "Crystal Palace",
    "Everton", "Fulham", "Huddersfield", "Hull", "Leicester", "Liverpool",
    "Man City", "Man United", "Middlesbrough", "Newcastle",
    "Norwich", "QPR", "Reading", "Sheffield United", "Southampton", "Stoke",
    "Sunderland", "Swansea", "Tottenham", "Watford", "West Brom", "West Ham",
    "Wigan", "Wolves"
]

# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["first_name"] = user["first_name"]
            session["email"] = user["email"]  # ✅ Add this line
            
            # optional: log login activity immediately
            from module import log_user_activity
            ip = request.remote_addr
            log_user_activity(email, "Logged in", page_name="/login", ip_address=ip)
            
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (first_name,last_name,email,mobile,password) VALUES (%s,%s,%s,%s,%s)",
            (first_name, last_name, email, mobile, password)
        )
        conn.commit()
        conn.close()
        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", first_name=session["first_name"])

@app.route("/stats", methods=["GET", "POST"])
def stats():
    if "user_id" not in session:
        return redirect(url_for("login"))

    matches = None
    error = None

    if request.method == "POST":
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]

        if not df_stats.empty:
            # Filter for ALL matches between those two teams
            matches = df_stats[(df_stats["HomeTeam"] == home_team) & (df_stats["AwayTeam"] == away_team)]

            if matches.empty:
                error = f"No matches found between {home_team} and {away_team}."
        else:
            error = "Match data not available."

    return render_template(
        "stats.html",
        real_stats=real_stats,
        teams=teams,         # ✅ using your existing list
        matches=matches,     # ✅ all matches, not just one
        error=error
    )

@app.route("/live")
def live():
    headers = {
        "x-apisports-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }

    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        return f"Error fetching data: {response.status_code}"

    data = response.json()
    matches = data.get("response", [])

    # Extract useful info for frontend
    live_data = []
    for match in matches:
        fixture = match["fixture"]
        league = match["league"]
        teams = match["teams"]
        goals = match["goals"]

        live_data.append({
            "league_name": league["name"],
            "league_logo": league["logo"],
            "home_team": teams["home"]["name"],
            "home_logo": teams["home"]["logo"],
            "away_team": teams["away"]["name"],
            "away_logo": teams["away"]["logo"],
            "home_goals": goals["home"],
            "away_goals": goals["away"],
            "status": fixture["status"]["long"],
            "elapsed": fixture["status"]["elapsed"],
            "venue": fixture["venue"]["name"],
            "country": league["country"]
        })

    return render_template("live.html", matches=live_data)

@app.route("/predict")
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("predict.html")

# -------------------------------
# Fulltime Prediction (GET + POST)
# -------------------------------
@app.route("/predict/fulltime", methods=["GET", "POST"])
def fulltime():
    if "user_id" not in session:
        return redirect(url_for("login"))

    prediction = None
    probabilities = None
    home_team_name = ""
    away_team_name = ""
    date_str = ""

    if request.method == "POST":
        try:
            # Get form data
            home_team_name = request.form['HomeTeam']
            away_team_name = request.form['AwayTeam']
            date = datetime.strptime(request.form['Date'], "%Y-%m-%d")
            date_str = date.strftime("%d-%m-%Y")

            # Numerical stats input
            HS = int(request.form['HS'])
            AS = int(request.form['AS'])
            HST = int(request.form['HST'])
            AST = int(request.form['AST'])
            HC = int(request.form['HC'])
            AC = int(request.form['AC'])
            HF = int(request.form['HF'])
            AF = int(request.form['AF'])
            HY = int(request.form['HY'])
            AY = int(request.form['AY'])
            HR = int(request.form['HR'])
            AR = int(request.form['AR'])

            # Encode teams: try encoder.transform, fallback to index lookup
            try:
                home_encoded = home_encoder.transform([home_team_name])[0]
            except Exception as e_enc_home:
                print(f"[WARN] home encoder transform failed: {e_enc_home} — falling back to index.")
                # fallback: numeric index (ensure this matches how you trained features)
                home_encoded = teams.index(home_team_name) if home_team_name in teams else 0

            try:
                away_encoded = away_encoder.transform([away_team_name])[0]
            except Exception as e_enc_away:
                print(f"[WARN] away encoder transform failed: {e_enc_away} — falling back to index.")
                away_encoded = teams.index(away_team_name) if away_team_name in teams else 0

            # Derived features (same as you had)
            TotalGoals = HS + AS
            ShotAccuracy_Home = HST / (HS + 1e-5)
            ShotAccuracy_Away = AST / (AS + 1e-5)
            ShotDiff = HS - AS
            ShotOnTargetDiff = HST - AST
            CornerRatio = HC / (AC + 1e-5)
            CornerDiff = HC - AC
            FoulDifference = HF - AF
            Home_CardRatio = (HY + HR) / (HS + 1e-5)
            Away_CardRatio = (AY + AR) / (AS + 1e-5)
            AttackBalance = ShotAccuracy_Home / (ShotAccuracy_Home + ShotAccuracy_Away + 1e-5)
            DayOfWeek_encoded = date.weekday()
            Season_encoded = date.year
            Year, Month, Day = date.year, date.month, date.day

            # Feature dict
            match_features = {
                'HomeTeam': home_encoded,
                'AwayTeam': away_encoded,
                'HS': HS, 'AS': AS,
                'HST': HST, 'AST': AST,
                'HC': HC, 'AC': AC,
                'HF': HF, 'AF': AF,
                'HY': HY, 'AY': AY,
                'HR': HR, 'AR': AR,
                'TotalGoals': TotalGoals,
                'ShotAccuracy_Home': ShotAccuracy_Home,
                'ShotAccuracy_Away': ShotAccuracy_Away,
                'ShotDiff': ShotDiff,
                'ShotOnTargetDiff': ShotOnTargetDiff,
                'CornerRatio': CornerRatio,
                'CornerDiff': CornerDiff,
                'FoulDifference': FoulDifference,
                'Home_CardRatio': Home_CardRatio,
                'Away_CardRatio': Away_CardRatio,
                'AttackBalance': AttackBalance,
                'DayOfWeek_encoded': DayOfWeek_encoded,
                'Season_encoded': Season_encoded,
                'Year': Year,
                'Month': Month,
                'Day': Day
            }

            # Prepare DataFrame and scale
            match_df = pd.DataFrame([match_features])
            match_df = match_df.reindex(columns=fulltime_feature_columns, fill_value=0)
            match_scaled = fulltime_scaler.transform(match_df)

            # Predict
            prediction = fulltime_model.predict(match_scaled)[0]
            pred_proba = fulltime_model.predict_proba(match_scaled)[0]
            probabilities = {cls: round(float(prob)*100,2) for cls, prob in zip(fulltime_model.classes_, pred_proba)}

        except Exception as e:
            # Log error and show friendly message
            print("[ERROR] Prediction failed:", e)
            import traceback; traceback.print_exc()
            flash("Prediction failed — check server logs. Make sure model files and encoders match your team names.")
            # Ensure variables exist for template rendering
            prediction = None
            probabilities = None

    return render_template(
        "fulltime.html",
        teams=teams,
        prediction=prediction,
        probabilities=probabilities,
        home_team=home_team_name,
        away_team=away_team_name,
        date=date_str
    )


@app.route("/predict/halftime", methods=["GET", "POST"])
def halftime():
    if request.method == "GET":
        # Render the form initially
        return render_template("halftime.html", teams=teams, prediction=None)

    try:
        # -------------------------
        # 1️⃣ Get input from form
        # -------------------------
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]
        hthg = int(request.form["hthg"])  # halftime home goals
        htag = int(request.form["htag"])  # halftime away goals

        # -------------------------
        # 2️⃣ Encode and prepare data
        # -------------------------
        # Encode teams using half-time encoders
        home_encoded = halftime_home_encoder.transform([home_team])[0]
        away_encoded = halftime_away_encoder.transform([away_team])[0]

        # Prepare input array and scale using half-time scaler
        X_input = np.array([[home_encoded, away_encoded, hthg, htag]])
        X_scaled = halftime_scaler.transform(X_input)

        # Predict full-time goals
        predicted_home_goals = int(round(halftime_home_model.predict(X_scaled)[0]))
        predicted_away_goals = int(round(halftime_away_model.predict(X_scaled)[0]))
        # -------------------------
        # 4️⃣ Determine result
        # -------------------------
        if predicted_home_goals > predicted_away_goals:
            predicted_result = "Home Win"
        elif predicted_home_goals < predicted_away_goals:
            predicted_result = "Away Win"
        else:
            predicted_result = "Draw"

        # -------------------------
        # 5️⃣ Create bar chart
        # -------------------------
        labels = ["Home Team", "Away Team"]
        halftime_goals = [hthg, htag]
        fulltime_goals = [predicted_home_goals, predicted_away_goals]

        fig, ax = plt.subplots(figsize=(6, 2))
        width = 0.45
        x = np.arange(len(labels))

        ax.bar(x - width/2, halftime_goals, width, label="1st Half (Given)", color="skyblue")
        ax.bar(x + width/2, fulltime_goals, width, label="Full Time (Predicted)", color="orange")

        ax.set_xlabel("Teams")
        ax.set_ylabel("Goals")
        ax.set_title("Comparison: First Half vs Full Time Goals")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        # Convert plot to base64 image
        img_buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        graph_url = base64.b64encode(img_buf.getvalue()).decode()
        plt.close(fig)

        # -------------------------
        # 6️⃣ Render result + graph
        # -------------------------
        return render_template(
            "halftime.html",
            teams=teams,
            prediction=predicted_result,
            home_team=home_team,
            away_team=away_team,
            hthg=hthg,
            htag=htag,
            predicted_home_goals=predicted_home_goals,
            predicted_away_goals=predicted_away_goals,
            graph_url=graph_url
        )

    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return render_template("halftime.html", teams=teams, prediction=None)


@app.route("/predict/goals", methods=["GET", "POST"])
def predict_goals():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    home_goals = None
    away_goals = None
    home_team = ""
    away_team = ""
    match_date_str = ""

    if request.method == "POST":
        try:
            # Get form data
            home_team = request.form["home_team"]
            away_team = request.form["away_team"]
            match_date = datetime.strptime(request.form["match_date"], "%Y-%m-%d")
            match_date_str = match_date.strftime("%d-%m-%Y")

            # Encode teams safely
            try:
                home_encoded = home_encoder.transform([home_team])[0]
            except:
                home_encoded = teams.index(home_team) if home_team in teams else 0

            try:
                away_encoded = away_encoder.transform([away_team])[0]
            except:
                away_encoded = teams.index(away_team) if away_team in teams else 0

            # Load stats
            home_stats = team_stats.get(home_team, {"AvgGoals_Last5": 1.4, "AvgConcede_Last5": 1.2, "ShotAccuracy": 0.45})
            away_stats = team_stats.get(away_team, {"AvgGoals_Last5": 1.2, "AvgConcede_Last5": 1.3, "ShotAccuracy": 0.40})

            # Prepare features
            features = {
                "HomeTeam": home_encoded,
                "AwayTeam": away_encoded,
                "AvgGoals_Last5": home_stats.get("AvgGoals_Last5", 1.4),
                "AvgConcede_Last5": away_stats.get("AvgConcede_Last5", 1.2),
                "ShotAccuracy_Home": home_stats.get("ShotAccuracy", 0.45),
                "ShotAccuracy_Away": away_stats.get("ShotAccuracy", 0.40),
                "DayOfWeek": match_date.weekday(),
                "Month": match_date.month,
                "Year": match_date.year
            }

           # Scale features using full-time scaler
            new_match_df = pd.DataFrame([features])
            new_match_df = new_match_df.reindex(columns=goal_feature_columns, fill_value=0)
            X_scaled = goals_scaler.transform(new_match_df)

            home_goals = max(0, int(round(home_goals_model.predict(X_scaled)[0])))
            away_goals = max(0, int(round(away_goals_model.predict(X_scaled)[0])))

            # Determine result
            if home_goals > away_goals:
                result = "Home Win"
            elif home_goals < away_goals:
                result = "Away Win"
            else:
                result = "Draw"

        except Exception as e:
            print("[ERROR] Goal prediction failed:", e)
            result = "Error: " + str(e)

    return render_template(
        "goals.html",
        teams=teams,
        result=result,
        home_goals=home_goals,
        away_goals=away_goals,
        home_team=home_team,
        away_team=away_team,
        match_date=match_date_str
    )
# -------------------------------
# Gemini Chatbot (GET + POST)
# -------------------------------
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "GET":
        # Reset session when the page is loaded fresh
        session["mode"] = None
        session["chat_state"] = {}
        return render_template("chatbot.html")

    # Handle user input (POST)
    data = request.get_json()
    user_message = data.get("query", "").strip()
    chat_state = session.get("chat_state", {})
    mode = session.get("mode")

    # === Step 1: Choose Mode ===
    if not mode:
        if "predict" in user_message.lower():
            session["mode"] = "predict"
            session["chat_state"] = {}
            return jsonify({"reply": "Okay! Let’s start the prediction. What’s the home team name?"})

        elif "question" in user_message.lower():
            session["mode"] = "question"
            return jsonify({"reply": "Sure! You can now ask any EPL or football-related question."})

        else:
            return jsonify({"reply": "Hi! Would you like to 'Predict Match' or 'Ask Question'?"})

    # === Mode 1: Predict Match ===
    if mode == "predict":
        try:
            if "home_team" not in chat_state:
                chat_state["home_team"] = user_message
                session["chat_state"] = chat_state
                return jsonify({"reply": "Got it. Who’s the away team?"})

            elif "away_team" not in chat_state:
                chat_state["away_team"] = user_message
                session["chat_state"] = chat_state
                return jsonify({"reply": "Enter home shots (HS):"})

            elif "HS" not in chat_state:
                chat_state["HS"] = int(user_message)
                session["chat_state"] = chat_state
                return jsonify({"reply": "Enter away shots (AS):"})

            elif "AS" not in chat_state:
                chat_state["AS"] = int(user_message)
                session["chat_state"] = chat_state
                return jsonify({"reply": "Enter home shots on target (HST):"})

            elif "HST" not in chat_state:
                chat_state["HST"] = int(user_message)
                session["chat_state"] = chat_state
                return jsonify({"reply": "Enter away shots on target (AST):"})

            elif "AST" not in chat_state:
                chat_state["AST"] = int(user_message)
                session["chat_state"] = chat_state
                return jsonify({"reply": "Enter home fouls (HF):"})

            elif "HF" not in chat_state:
                chat_state["HF"] = int(user_message)
                session["chat_state"] = chat_state
                return jsonify({"reply": "Enter away fouls (AF):"})

            elif "AF" not in chat_state:
                chat_state["AF"] = int(user_message)
                session["chat_state"] = chat_state
                # ✅ All inputs collected → Run prediction
                return run_full_prediction(chat_state)

        except Exception as e:
            print("Prediction error:", e)
            return jsonify({"reply": "Invalid input! Please enter numeric values properly."})

    # === Mode 2: Ask Question (Gemini Normal Chat) ===
    elif mode == "question":
        try:
            response = model_gemini.generate_content(
                f"Answer this football or EPL-related question in a brief and clear way: {user_message}"
            )
            return jsonify({"reply": response.text})
        except Exception as e:
            print("Gemini error:", e)
            return jsonify({"reply": "Sorry, I couldn’t get that. Try again!"})

def run_full_prediction(chat_state):
    try:
        # Collect user inputs
        home_team = chat_state["home_team"]
        away_team = chat_state["away_team"]
        HS, AS, HST, AST, HF, AF = (
            chat_state["HS"], chat_state["AS"], chat_state["HST"],
            chat_state["AST"], chat_state["HF"], chat_state["AF"]
        )

        # Encode team names
        home_encoded = home_encoder.transform([home_team])[0]
        away_encoded = away_encoder.transform([away_team])[0]

        # Derived stats
        TotalGoals = HS + AS
        ShotAccuracy_Home = HST / (HS + 1e-5)
        ShotAccuracy_Away = AST / (AS + 1e-5)
        ShotDiff = HS - AS
        FoulDiff = HF - AF

        # Build feature set
        match_features = {
            'HomeTeam': home_encoded,
            'AwayTeam': away_encoded,
            'HS': HS, 'AS': AS,
            'HST': HST, 'AST': AST,
            'HF': HF, 'AF': AF,
            'TotalGoals': TotalGoals,
            'ShotAccuracy_Home': ShotAccuracy_Home,
            'ShotAccuracy_Away': ShotAccuracy_Away,
            'ShotDiff': ShotDiff,
            'FoulDifference': FoulDiff,
        }

        match_df = pd.DataFrame([match_features])
        match_df = match_df.reindex(columns=fulltime_feature_columns, fill_value=0)
        match_scaled = fulltime_scaler.transform(match_df)

        # Predict result
        prediction = fulltime_model.predict(match_scaled)[0]
        pred_proba = fulltime_model.predict_proba(match_scaled)[0]
        probabilities = {cls: round(float(prob)*100, 2) for cls, prob in zip(fulltime_model.classes_, pred_proba)}

        # Generate natural summary using Gemini
        summary_prompt = f"""
        The model predicted '{prediction}' for the match between {home_team} and {away_team}.
        Probabilities: {probabilities}.
        Explain this result in a football analysis style with short reasoning.
        """
        summary = model_gemini.generate_content(summary_prompt).text

        # Reset session after completion
        session["mode"] = None
        session["chat_state"] = {}

        return jsonify({"reply": f"🏁 Prediction: {prediction}\n\n{summary}"})

    except Exception as e:
        print("run_full_prediction error:", e)
        return jsonify({"reply": "Something went wrong while predicting the match."})

@app.before_request
def track_user_activity():
    if request.endpoint not in ("static", "login"):  # Skip static files & login itself
        email = session.get("email", "Guest")
        page = request.path
        ip = request.remote_addr

        from module import log_user_activity
        log_user_activity(email, f"Accessed {page}", page_name=page, ip_address=ip)


if __name__ == "__main__":
    app.run(debug=True)
