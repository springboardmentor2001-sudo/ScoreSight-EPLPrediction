from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from pathlib import Path
import requests

load_dotenv()

# =============================================================================
# FOOTBALL API CONFIGURATION
# =============================================================================

# Add to your configuration section
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'api-football-v1.p.rapidapi.com'
RAPIDAPI_BASE_URL = 'https://api-football-v1.p.rapidapi.com/v3'

if not RAPIDAPI_KEY or RAPIDAPI_KEY == 'your_actual_rapidapi_key_here':
    print("⚠️  RAPIDAPI_KEY not found in environment variables")
    print("📝 Using fallback match data")
else:
    print("✅ RAPIDAPI_KEY loaded successfully")

def get_real_upcoming_matches():
    """Get real upcoming EPL matches from API-Football"""
    # Check if API key is available
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == 'your_actual_rapidapi_key_here':
        print("❌ No valid RAPIDAPI_KEY, using fallback data")
        return get_sample_upcoming_matches()
    
    try:
        headers = {
            'X-RapidAPI-Key': RAPIDAPI_KEY,
            'X-RapidAPI-Host': RAPIDAPI_HOST
        }
        
        # Get current season - FORCE 2025 SEASON
        current_year = 2025  # Force 2025 season
        season = current_year
        
        # Get fixtures for Premier League (league ID: 39)
        params = {
            'league': '39',  # Premier League
            'season': season,
            'next': '20',  # Get next 20 matches
            'status': 'NS'  # Only not started matches
        }
        
        print(f"🚀 Fetching 2025 EPL matches from API-Football...")
        response = requests.get(f'{RAPIDAPI_BASE_URL}/fixtures', 
                              headers=headers, 
                              params=params,
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            matches = []
            
            print(f"✅ API Response received: {len(data.get('response', []))} fixtures")
            
            for fixture in data.get('response', []):
                fixture_data = fixture['fixture']
                teams_data = fixture['teams']
                league_data = fixture['league']
                
                # Parse date
                match_date = datetime.fromisoformat(fixture_data['date'].replace('Z', '+00:00'))
                local_date = match_date.astimezone()
                
                # Only include matches from 2025
                if match_date.year >= 2025:
                    matches.append({
                        'id': fixture_data['id'],
                        'home_team': teams_data['home']['name'],
                        'away_team': teams_data['away']['name'],
                        'date': local_date.strftime('%Y-%m-%d'),
                        'time': local_date.strftime('%H:%M'),
                        'venue': fixture_data.get('venue', {}).get('name', 'TBD'),
                        'status': fixture_data['status']['short'],
                        'competition': league_data['name'],
                        'matchday': f"Matchday {fixture_data.get('round', 'Regular')}",
                        'season': season
                    })
            
            # If no 2025 matches found, try to get any future matches
            if not matches:
                print("🔍 No 2025 matches found, searching for any future EPL matches...")
                # Remove season filter to get any available matches
                params_without_season = {
                    'league': '39',
                    'next': '20',
                    'status': 'NS'
                }
                
                response_fallback = requests.get(f'{RAPIDAPI_BASE_URL}/fixtures', 
                                               headers=headers, 
                                               params=params_without_season,
                                               timeout=10)
                
                if response_fallback.status_code == 200:
                    fallback_data = response_fallback.json()
                    for fixture in fallback_data.get('response', []):
                        fixture_data = fixture['fixture']
                        teams_data = fixture['teams']
                        league_data = fixture['league']
                        
                        match_date = datetime.fromisoformat(fixture_data['date'].replace('Z', '+00:00'))
                        local_date = match_date.astimezone()
                        
                        # Include any future match
                        if match_date > datetime.now():
                            matches.append({
                                'id': fixture_data['id'],
                                'home_team': teams_data['home']['name'],
                                'away_team': teams_data['away']['name'],
                                'date': local_date.strftime('%Y-%m-%d'),
                                'time': local_date.strftime('%H:%M'),
                                'venue': fixture_data.get('venue', {}).get('name', 'TBD'),
                                'status': fixture_data['status']['short'],
                                'competition': league_data['name'],
                                'matchday': f"Matchday {fixture_data.get('round', 'Regular')}",
                                'season': match_date.year
                            })
            
            # Sort by date
            matches.sort(key=lambda x: (x['date'], x['time']))
            print(f"✅ Processed {len(matches)} upcoming matches")
            
            if matches:
                print(f"📅 Matches date range: {matches[0]['date']} to {matches[-1]['date']}")
            
            return matches
            
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return get_sample_upcoming_matches()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching matches: {e}")
        return get_sample_upcoming_matches()
    except Exception as e:
        print(f"❌ Error processing matches: {e}")
        return get_sample_upcoming_matches()

def get_sample_upcoming_matches():
    """Fallback sample data when API fails - UPDATED FOR 2025"""
    current_date = datetime.now()
    # Create 2025 matches
    sample_matches = [
        {
            'id': 1,
            'home_team': 'Manchester City',
            'away_team': 'Liverpool',
            'date': '2025-01-15',
            'time': '15:00',
            'venue': 'Etihad Stadium',
            'status': 'NS',
            'competition': 'Premier League',
            'matchday': 'Matchday 21',
            'season': 2025
        },
        {
            'id': 2,
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'date': '2025-01-18',
            'time': '17:30',
            'venue': 'Emirates Stadium',
            'status': 'NS',
            'competition': 'Premier League',
            'matchday': 'Matchday 22',
            'season': 2025
        },
        {
            'id': 3,
            'home_team': 'Manchester United',
            'away_team': 'Tottenham Hotspur',
            'date': '2025-01-22',
            'time': '20:00',
            'venue': 'Old Trafford',
            'status': 'NS',
            'competition': 'Premier League',
            'matchday': 'Matchday 23',
            'season': 2025
        },
        {
            'id': 4,
            'home_team': 'Newcastle United',
            'away_team': 'Aston Villa',
            'date': '2025-01-25',
            'time': '15:00',
            'venue': 'St James Park',
            'status': 'NS',
            'competition': 'Premier League',
            'matchday': 'Matchday 24',
            'season': 2025
        },
        {
            'id': 5,
            'home_team': 'Brighton',
            'away_team': 'West Ham',
            'date': '2025-01-29',
            'time': '19:45',
            'venue': 'Amex Stadium',
            'status': 'NS',
            'competition': 'Premier League',
            'matchday': 'Matchday 25',
            'season': 2025
        }
    ]
    return sample_matches

# =============================================================================
# USER MANAGEMENT
# =============================================================================

# User storage file
USER_DATA_FILE = 'users.json'

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

# Load existing users
users_db = load_users()
print(f"📊 Loaded {len(users_db)} users from storage")

# =============================================================================
# GEMINI AI CONFIGURATION - FIXED FOR 2 KEYS
# =============================================================================

# Safe import for Google AI with fallback
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
    print("✓ Google Generative AI imported successfully")
except ImportError as e:
    GOOGLE_AI_AVAILABLE = False
    print(f"✗ Google Generative AI not available: {e}")
    genai = None

# Configure Gemini API with your 2 keys
GEMINI_API_KEYS = [
    os.environ.get('GEMINI_API_KEY_1'),
    os.environ.get('GEMINI_API_KEY_2'),
]

# Filter out empty keys and validate
valid_keys = []
for i, key in enumerate(GEMINI_API_KEYS):
    if key and key.strip() and key != 'your_actual_gemini_api_key_here':
        valid_keys.append(key)
        print(f"✓ API Key {i+1} loaded successfully")
    else:
        print(f"✗ API Key {i+1} is missing or invalid")

GEMINI_API_KEYS = valid_keys

if not GEMINI_API_KEYS:
    print("⚠️  No valid Gemini API keys found")
    GOOGLE_AI_AVAILABLE = False
else:
    print(f"✓ {len(GEMINI_API_KEYS)} valid Gemini API key(s) loaded")

current_key_index = 0
model = None


def initialize_gemini_model():
    global model, current_key_index, GOOGLE_AI_AVAILABLE
    
    if not GOOGLE_AI_AVAILABLE or not GEMINI_API_KEYS:
        print("⚠️  Cannot initialize model - AI not available or no API keys")
        return False
    
    try:
        # Use current API key
        api_key = GEMINI_API_KEYS[current_key_index]
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Use gemini-2.5-flash - the latest stable model
        model_name = 'models/gemini-2.5-flash'
        
        print(f"Using model: {model_name}")
        
        # Initialize the model
        model = genai.GenerativeModel(model_name)
        
        # Test the model with a simple request
        test_response = model.generate_content("Hello")
        
        if test_response and hasattr(test_response, 'text') and test_response.text:
            print(f"✓ Gemini model initialized successfully (Key {current_key_index + 1}/{len(GEMINI_API_KEYS)})")
            return True
        else:
            print(f"✗ Model test returned empty response")
            return False
            
    except Exception as e:
        print(f"✗ Model initialization failed with key {current_key_index + 1}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def rotate_api_key():
    global current_key_index, model
    
    if len(GEMINI_API_KEYS) <= 1:
        print("⚠️  Only one API key available, cannot rotate")
        return False
    
    current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
    print(f"🔄 Rotating to API key {current_key_index + 1}/{len(GEMINI_API_KEYS)}")
    
    return initialize_gemini_model()


# Initialize the model at startup
if GOOGLE_AI_AVAILABLE and GEMINI_API_KEYS:
    model_initialized = initialize_gemini_model()
    print(f"Model Initialized: {'Yes' if model_initialized else 'No'}")
else:
    print("⚠️  Gemini API not configured - chatbot will be unavailable")
    print("Model Initialized: No")

# =============================================================================
# FLASK APP SETUP
# =============================================================================

app = Flask(__name__)

# Enhanced configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enhanced CORS configuration
CORS(app, 
     resources={
         r"/*": {
             'origins': ['http://localhost:3000', 'http://127.0.0.1:3000', 
                        'http://localhost:5173', 'http://127.0.0.1:5173',
                        'http://localhost:3001'],
             'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
             'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
             'supports_credentials': True,
             'max_age': 600
         }
     })

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_PATH='/'
)

# Handle preflight requests globally
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

print("=" * 60)
print("ScoreSight EPL Predictor API - Starting Up")
print("=" * 60)
print(f"Google AI Available: {'Yes' if GOOGLE_AI_AVAILABLE else 'No'}")
print(f"Gemini API Keys Loaded: {len(GEMINI_API_KEYS)}")
print(f"Current API Key Index: {current_key_index + 1}/{len(GEMINI_API_KEYS)}")
print(f"Model Initialized: {'Yes' if model else 'No'}")
print("=" * 60)

def get_football_context():
    """Provide context about the EPL predictor to the AI"""
    return """
    You are an expert football analyst assistant for the English Premier League (EPL) Match Predictor. 
    Your role is to help users with:
    1. Match predictions and analysis
    2. Team performance insights
    3. Player statistics and form
    4. Historical match data
    5. Football tactics and strategies

    Available teams: Arsenal, Aston Villa, Bournemouth, Brighton, Brentford, Chelsea, 
    Crystal Palace, Everton, Fulham, Leicester, Liverpool, Manchester City, Manchester United, 
    Newcastle, Nottingham Forest, Southampton, Tottenham, West Ham, Wolverhampton

    Be helpful, informative, and focus on football analytics.
    Season: 2024-2025 Premier League
    """

def load_historical_data():
    """Load historical match data"""
    try:
        data_path = os.path.join(DATA_DIR, 'master_dataset_with_features.csv')
        if os.path.exists(data_path):
            historical_data = pd.read_csv(data_path)
            historical_data['Date'] = pd.to_datetime(historical_data['Date'])
            print(f"✓ Loaded historical data with {len(historical_data)} rows")
            return historical_data
        else:
            print(f"✗ Historical data not found, creating sample data")
            return create_sample_data()
    except Exception as e:
        print(f"✗ Error loading historical data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample historical data"""
    sample_data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'HomeTeam': ['Man City', 'Liverpool', 'Arsenal', 'Chelsea', 'Man United'],
        'AwayTeam': ['Liverpool', 'Arsenal', 'Chelsea', 'Man United', 'Tottenham'],
        'FTHG': [2, 1, 3, 2, 1],
        'FTAG': [1, 2, 1, 2, 1],
        'FTR': ['H', 'A', 'H', 'D', 'D'],
        'HTHG': [1, 0, 2, 1, 0],
        'HTAG': [0, 1, 0, 1, 1],
        'HS': [15, 12, 18, 14, 10],
        'AS': [10, 14, 8, 13, 12],
        'HST': [6, 4, 8, 5, 3],
        'AST': [4, 6, 3, 5, 4],
        'HC': [7, 5, 8, 6, 4],
        'AC': [4, 7, 3, 5, 6],
        'HF': [12, 14, 10, 13, 15],
        'AF': [14, 12, 16, 11, 13],
        'HY': [1, 2, 1, 1, 2],
        'AY': [2, 1, 2, 1, 1],
        'HR': [0, 0, 0, 0, 0],
        'AR': [0, 0, 0, 0, 0]
    }
    return pd.DataFrame(sample_data)

# Load historical data
historical_data = load_historical_data()

# Authentication helpers - SESSION BASED
def is_authenticated():
    """Check if user is authenticated using session + user storage"""
    username = session.get('user_id')
    authenticated = session.get('authenticated')
    
    # Check session AND verify user exists in storage
    if authenticated and username and username in users_db:
        return True
    
    return False

def get_current_user():
    """Get current user data from session"""
    if is_authenticated():
        username = session.get('user_id')
        # Return basic user info from session
        return {
            'username': username,
            'name': session.get('user_name', username),
            'email': session.get('user_email', '')
        }
    return None

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def signup():
    """User registration - stores in persistent storage"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', username)

        if not username or not password or not email:
            return jsonify({'success': False, 'error': 'All fields required'}), 400

        # Check if username already exists
        if username in users_db:
            return jsonify({'success': False, 'error': 'Username already exists'}), 400

        # Check if email already exists
        for user in users_db.values():
            if user.get('email') == email:
                return jsonify({'success': False, 'error': 'Email already exists'}), 400

        # Create new user
        users_db[username] = {
            'password': password,  # In production, hash this!
            'name': name,
            'email': email
        }
        
        # Save to persistent storage
        save_users(users_db)

        # Create session
        session['user_id'] = username
        session['user_name'] = name
        session['user_email'] = email
        session['authenticated'] = True
        session.permanent = True

        print(f"✅ New user registered: {username}")
        print(f"📊 Total users: {len(users_db)}")

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {'username': username, 'name': name, 'email': email},
            'access_token': f'token-{username}-{datetime.now().timestamp()}'
        })

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500
    
@app.route('/api/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    """User login - validates against persistent storage"""
    try:
        data = request.json
        login_input = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not login_input or not password:
            return jsonify({'success': False, 'error': 'Credentials required'}), 400

        # Find user by username or email
        user = None
        username = None
        
        # First check by username
        if login_input in users_db:
            user = users_db[login_input]
            username = login_input
        else:
            # Check by email
            for uname, user_data in users_db.items():
                if user_data.get('email') == login_input:
                    user = user_data
                    username = uname
                    break

        # Validate password
        if user and user['password'] == password:
            # Create session
            session['user_id'] = username
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['authenticated'] = True
            session.permanent = True

            print(f"✓ User logged in: {username}")

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'name': user['name'],
                    'email': user['email']
                },
                'access_token': f'token-{username}-{datetime.now().timestamp()}'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def logout():
    """User logout"""
    try:
        username = session.get('user_id')
        session.clear()
        print(f"✓ User logged out: {username}")
        return jsonify({'success': True, 'message': 'Logout successful'})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Logout failed'}), 500

@app.route('/api/check-auth', methods=['GET'])
@cross_origin(supports_credentials=True)
def check_auth():
    """Check authentication status"""
    try:
        if is_authenticated():
            username = session.get('user_id')
            user_data = users_db.get(username)
            if user_data:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'username': username,
                        'name': user_data['name'],
                        'email': user_data['email']
                    }
                })
        
        return jsonify({'authenticated': False, 'user': None})
    except Exception as e:
        print(f"Auth check error: {e}")
        return jsonify({'authenticated': False, 'user': None})

# =============================================================================
# MATCHES ENDPOINT (UPDATED FOR 2025)
# =============================================================================

@app.route('/api/matches', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_upcoming_matches():
    """Get real upcoming matches from API"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401

        matches = get_real_upcoming_matches()
        
        return jsonify({
            'matches': matches, 
            'count': len(matches), 
            'timestamp': datetime.now().isoformat(),
            'source': 'api-football' if len(matches) > 3 else 'fallback',
            'season': 2025
        })

    except Exception as e:
        print(f"Error fetching matches: {str(e)}")
        # Return fallback data even on error
        fallback_matches = get_sample_upcoming_matches()
        return jsonify({
            'matches': fallback_matches, 
            'count': len(fallback_matches), 
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback',
            'season': 2025,
            'error': 'Using fallback data'
        }), 200

# =============================================================================
# PREDICTION ENDPOINT
# =============================================================================

@app.route('/predict-ai-fixed', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def predict_ai_fixed():
    """AI prediction"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        home_team = data.get('HomeTeam')
        away_team = data.get('AwayTeam')
        match_date = data.get('Date', pd.Timestamp.now().strftime('%Y-%m-%d'))
        
        if not home_team or not away_team:
            return jsonify({'error': 'Teams required'}), 400
        
        if home_team == away_team:
            return jsonify({'error': 'Teams must be different'}), 400
        
        home_form = calculate_team_form_fixed(home_team, match_date, 5)
        away_form = calculate_team_form_fixed(away_team, match_date, 5)
        h2h_stats = calculate_h2h_stats_fixed(home_team, away_team, match_date)
        
        form_diff = home_form['Points'] - away_form['Points']
        
        if form_diff > 4:
            outcome = 'Home Win'
        elif form_diff < -4:
            outcome = 'Away Win'
        else:
            outcome = 'Draw'
        
        home_goals, away_goals = calculate_realistic_goals(outcome, home_form, away_form, h2h_stats)
        
        if outcome == 'Home Win':
            home_points, away_points = 3, 0
        elif outcome == 'Away Win':
            home_points, away_points = 0, 3
        else:
            home_points, away_points = 1, 1
        
        confidence = calculate_realistic_confidence(outcome, home_form, away_form, h2h_stats)
        
        return jsonify({
            'outcome': outcome,
            'goalDifference': home_goals - away_goals,
            'homeGoals': home_goals,
            'awayGoals': away_goals,
            'homePoints': home_points,
            'awayPoints': away_points,
            'confidence': confidence
        })
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

# =============================================================================
# CHAT ENDPOINT WITH PROPER ERROR HANDLING
# =============================================================================

@app.route('/chat', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def chat():
    """Chat endpoint with automatic API key rotation"""
    try:
        # Check authentication
        if not is_authenticated():
            return jsonify({
                'error': 'Authentication required. Please login first.',
                'code': 'AUTH_REQUIRED'
            }), 401

        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation', [])

        if not user_message:
            return jsonify({'error': 'Message required'}), 400

        username = session.get('user_id')
        print(f"💬 Chat from {username}: {user_message[:50]}...")

        # Check AI availability
        if not GOOGLE_AI_AVAILABLE:
            return jsonify({
                'response': "⚠️ AI service is not available. Google Generative AI is not configured.",
                'fallback': True,
                'timestamp': datetime.now().isoformat()
            }), 200

        if model is None:
            return jsonify({
                'response': "⚠️ AI model is not initialized. Please check your API keys.",
                'fallback': True,
                'timestamp': datetime.now().isoformat()
            }), 200

        # Build prompt
        context = get_football_context()
        history_text = ""
        for msg in conversation_history[-6:]:
            role = "User" if msg.get('sender') == 'user' else "Assistant"
            history_text += f"{role}: {msg.get('text', '')}\n"

        prompt = f"""{context}

Recent conversation:
{history_text}

User: {user_message}

Provide a helpful response about EPL football. Keep it concise."""

        print("🚀 Generating response...")
        
        try:
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                print(f"✅ Response generated with API Key {current_key_index + 1}")
                return jsonify({
                    'response': response.text,
                    'timestamp': datetime.now().isoformat(),
                    'success': True,
                    'api_key_used': current_key_index + 1
                })
            else:
                return jsonify({
                    'response': "I couldn't generate a response. Please try again.",
                    'fallback': True,
                    'timestamp': datetime.now().isoformat()
                }), 200
                
        except Exception as gen_error:
            error_msg = str(gen_error)
            print(f"❌ Generation error with API Key {current_key_index + 1}: {error_msg}")
            
            # Check if it's a quota error and rotate key
            if 'quota' in error_msg.lower() or '429' in error_msg or 'exceeded' in error_msg.lower():
                print("🔄 Quota exceeded, attempting to rotate API key...")
                if rotate_api_key():
                    # Retry the request with new key
                    try:
                        print("🔄 Retrying request with new API key...")
                        response = model.generate_content(prompt)
                        if response and hasattr(response, 'text') and response.text:
                            print(f"✅ Response generated with new API Key {current_key_index + 1}")
                            return jsonify({
                                'response': response.text,
                                'timestamp': datetime.now().isoformat(),
                                'success': True,
                                'api_key_used': current_key_index + 1,
                                'key_rotated': True
                            })
                    except Exception as retry_error:
                        print(f"❌ Retry also failed: {retry_error}")
            
            return jsonify({
                'response': f"AI service temporarily unavailable. Please try again in a moment.",
                'fallback': True,
                'timestamp': datetime.now().isoformat()
            }), 200

    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return jsonify({
            'response': "An error occurred. Please try again.",
            'error': str(e),
            'fallback': True
        }), 500

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.route('/test', methods=['GET'])
def test_connection():
    """Test endpoint"""
    return jsonify({
        'message': 'Server running',
        'status': 'success',
        'ai_available': GOOGLE_AI_AVAILABLE and model is not None,
        'total_api_keys': len(GEMINI_API_KEYS),
        'current_api_key': current_key_index + 1,
        'model_initialized': model is not None,
        'timestamp': datetime.now().isoformat(),
        'season': 2025
    })

@app.route('/api/chat-status', methods=['GET'])
@cross_origin(supports_credentials=True)
def chat_status():
    """Check chatbot status and current API key"""
    return jsonify({
        'ai_available': GOOGLE_AI_AVAILABLE and model is not None,
        'total_api_keys': len(GEMINI_API_KEYS),
        'current_api_key_index': current_key_index + 1,
        'model_initialized': model is not None,
        'timestamp': datetime.now().isoformat(),
        'season': 2025
    })

@app.route('/api/debug-session', methods=['GET'])
@cross_origin(supports_credentials=True)
def debug_session():
    """Debug session information"""
    return jsonify({
        'session_id': session.sid if hasattr(session, 'sid') else 'no-sid',
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'authenticated': session.get('authenticated'),
        'session_keys': list(session.keys())
    })

@app.route('/')
def home():
    return jsonify({
        'message': 'ScoreSight EPL Predictor API',
        'version': '1.0',
        'status': 'running',
        'ai_available': GOOGLE_AI_AVAILABLE and model is not None,
        'total_api_keys': len(GEMINI_API_KEYS),
        'current_api_key': current_key_index + 1,
        'model_initialized': model is not None,
        'season': 2025,
        'endpoints': {
            '/api/login': 'POST',
            '/api/signup': 'POST',
            '/api/logout': 'POST',
            '/api/check-auth': 'GET',
            '/api/matches': 'GET',
            '/predict-ai-fixed': 'POST',
            '/chat': 'POST'
        }
    })

# Helper functions
def calculate_team_form_fixed(team_name, date, n_matches=5):
    """Calculate team form"""
    try:
        date = pd.Timestamp(date)
        team_matches = historical_data[
            ((historical_data['HomeTeam'] == team_name) | 
             (historical_data['AwayTeam'] == team_name)) &
            (historical_data['Date'] < date)
        ].sort_values('Date', ascending=False).head(n_matches)
        
        if len(team_matches) == 0:
            return {'GoalsFor': 0, 'GoalsAgainst': 0, 'Points': 0, 'Wins': 0}
        
        goals_for = 0
        goals_against = 0
        points = 0
        wins = 0
        
        for _, match in team_matches.iterrows():
            if match['HomeTeam'] == team_name:
                goals_for += match['FTHG']
                goals_against += match['FTAG']
                if match['FTHG'] > match['FTAG']:
                    points += 3
                    wins += 1
                elif match['FTHG'] == match['FTAG']:
                    points += 1
            else:
                goals_for += match['FTAG']
                goals_against += match['FTHG']
                if match['FTAG'] > match['FTHG']:
                    points += 3
                    wins += 1
                elif match['FTAG'] == match['FTHG']:
                    points += 1
        
        return {'GoalsFor': goals_for, 'GoalsAgainst': goals_against, 'Points': points, 'Wins': wins}
    except Exception as e:
        print(f"Form calculation error: {e}")
        return {'GoalsFor': 0, 'GoalsAgainst': 0, 'Points': 0, 'Wins': 0}

def calculate_h2h_stats_fixed(home_team, away_team, date):
    """Calculate H2H stats"""
    try:
        date = pd.Timestamp(date)
        h2h_matches = historical_data[
            (((historical_data['HomeTeam'] == home_team) & (historical_data['AwayTeam'] == away_team)) |
             ((historical_data['HomeTeam'] == away_team) & (historical_data['AwayTeam'] == home_team))) &
            (historical_data['Date'] < date)
        ].head(10)
        
        if len(h2h_matches) == 0:
            return {
                'H2H_HomeWins': 0, 'H2H_AwayWins': 0, 'H2H_Draws': 0,
                'H2H_TotalMatches': 0, 'H2H_HomeWinRate': 0
            }
        
        home_wins = away_wins = draws = 0
        
        for _, match in h2h_matches.iterrows():
            if match['HomeTeam'] == home_team:
                if match['FTHG'] > match['FTAG']:
                    home_wins += 1
                elif match['FTAG'] > match['FTHG']:
                    away_wins += 1
                else:
                    draws += 1
            else:
                if match['FTAG'] > match['FTHG']:
                    home_wins += 1
                elif match['FTHG'] > match['FTAG']:
                    away_wins += 1
                else:
                    draws += 1
        
        total = len(h2h_matches)
        return {
            'H2H_HomeWins': home_wins,
            'H2H_AwayWins': away_wins,
            'H2H_Draws': draws,
            'H2H_TotalMatches': total,
            'H2H_HomeWinRate': home_wins / total if total > 0 else 0
        }
    except Exception as e:
        print(f"H2H calculation error: {e}")
        return {'H2H_HomeWins': 0, 'H2H_AwayWins': 0, 'H2H_Draws': 0, 'H2H_TotalMatches': 0, 'H2H_HomeWinRate': 0}

def calculate_realistic_goals(outcome, home_form, away_form, h2h_stats):
    """Calculate goals"""
    if outcome == 'Home Win':
        return 2, 1
    elif outcome == 'Away Win':
        return 1, 2
    else:
        return 1, 1

def calculate_realistic_confidence(outcome, home_form, away_form, h2h_stats):
    """Calculate confidence"""
    base = 70
    form_diff = abs(home_form['Points'] - away_form['Points'])
    return min(90, base + (form_diff * 2))

if __name__ == '__main__':
    print("\nStarting server...")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)