from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import pandas as pd
import os
from datetime import datetime, timedelta

# Safe import for Google AI with fallback
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
    print("✓ Google Generative AI imported successfully")
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("✗ Google Generative AI not available - chatbot disabled")
    # Create a dummy genai module for fallback
    class DummyGenAI:
        def configure(self, *args, **kwargs): pass
        class GenerativeModel:
            def __init__(self, *args, **kwargs): pass
            def generate_content(self, *args, **kwargs):
                class Response:
                    text = "Chatbot is currently unavailable. Please make sure 'google-generativeai' package is installed."
                return Response()
    genai = DummyGenAI()

app = Flask(__name__)

# Enhanced configuration - using Flask's built-in session
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enhanced CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000", "http://127.0.0.1:3000", 
                        "http://localhost:5173", "http://127.0.0.1:5173",
                        "http://localhost:3001"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"],
             "max_age": 600
         }
     })

# Handle preflight requests globally
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Access-Control-Allow-Origin", 
                           request.headers.get("Origin", "http://localhost:5173"))
        response.headers.add("Access-Control-Allow-Headers", 
                           "Content-Type, Authorization, Access-Control-Allow-Credentials")
        response.headers.add("Access-Control-Allow-Methods", 
                           "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

# Configure Gemini API only if available
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️  GEMINI_API_KEY not found in environment variables")
    print("⚠️  Chatbot will run in fallback mode")
    GOOGLE_AI_AVAILABLE = False

model = None

if GOOGLE_AI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Try the latest model names
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("✓ Using gemini-1.5-flash model")
        except Exception as e:
            try:
                model = genai.GenerativeModel('gemini-1.0-pro')
                print("✓ Using gemini-1.0-pro model")
            except Exception as e:
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    print("✓ Using gemini-pro model")
                except Exception as e:
                    print(f"✗ All model attempts failed: {e}")
                    model = None
    except Exception as e:
        print(f"✗ Gemini API configuration failed: {e}")
        model = None
else:
    model = None
    print("✗ Gemini API not configured - using fallback mode")

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

print("=" * 60)
print("ScoreSight EPL Predictor API - Starting Up")
print("=" * 60)
print(f"Google AI Available: {'Yes' if GOOGLE_AI_AVAILABLE else 'No'}")
print(f"Gemini API Key: {'Set' if GEMINI_API_KEY else 'Not Set'}")
print(f"Model Initialized: {'Yes' if model else 'No'}")

# Enhanced user database with email support
users_db = {
    'admin': {'password': 'admin123', 'name': 'Administrator', 'email': 'admin@scoresight.com'},
    'user': {'password': 'user123', 'name': 'Test User', 'email': 'user@scoresight.com'},
    'demo': {'password': 'demo123', 'name': 'Demo User', 'email': 'demo@scoresight.com'}
}

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

    Available teams in the system:
    - Arsenal, Aston Villa, Bournemouth, Brighton, Burnley
    - Chelsea, Crystal Palace, Everton, Fulham, Leicester
    - Liverpool, Man City, Man United, Newcastle, Norwich
    - Southampton, Tottenham, Watford, West Ham, Wolves

    The prediction system uses:
    - Team form from recent matches
    - Head-to-head statistics
    - Historical performance data
    - Machine learning models

    Be helpful, informative, and focus on football analytics. If users ask about non-football topics, 
    politely steer them back to EPL discussions.

    Current season: 2024-2025 Premier League
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
            print(f"✗ Historical data not found at {data_path}")
            # Create sample data for testing
            print("✓ Creating sample data for testing")
            return create_sample_data()
    except Exception as e:
        print(f"✗ Error loading historical data: {e}")
        print("✓ Creating sample data for testing")
        return create_sample_data()

def create_sample_data():
    """Create sample historical data for testing"""
    sample_data = {
        'Date': [
            '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
            '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'
        ],
        'HomeTeam': [
            'Man City', 'Liverpool', 'Arsenal', 'Chelsea', 'Man United',
            'Tottenham', 'Newcastle', 'West Ham', 'Leicester', 'Aston Villa'
        ],
        'AwayTeam': [
            'Liverpool', 'Arsenal', 'Chelsea', 'Man United', 'Tottenham',
            'Newcastle', 'West Ham', 'Leicester', 'Aston Villa', 'Man City'
        ],
        'FTHG': [2, 1, 3, 2, 1, 2, 1, 0, 2, 1],  # Full Time Home Goals
        'FTAG': [1, 2, 1, 2, 1, 0, 2, 1, 1, 3],  # Full Time Away Goals
        'FTR': ['H', 'A', 'H', 'D', 'D', 'H', 'A', 'A', 'H', 'A'],  # Full Time Result (H=Home, A=Away, D=Draw)
        'HTHG': [1, 0, 2, 1, 0, 1, 0, 0, 1, 0],  # Half Time Home Goals
        'HTAG': [0, 1, 0, 1, 1, 0, 1, 1, 0, 2],  # Half Time Away Goals
        'HS': [15, 12, 18, 14, 10, 16, 11, 8, 13, 9],   # Home Shots
        'AS': [10, 14, 8, 13, 12, 6, 15, 12, 9, 16],    # Away Shots
        'HST': [6, 4, 8, 5, 3, 7, 4, 2, 5, 3],   # Home Shots on Target
        'AST': [4, 6, 3, 5, 4, 2, 7, 4, 3, 8],   # Away Shots on Target
        'HC': [7, 5, 8, 6, 4, 7, 5, 3, 6, 4],    # Home Corners
        'AC': [4, 7, 3, 5, 6, 2, 8, 5, 4, 7],    # Away Corners
        'HF': [12, 14, 10, 13, 15, 11, 16, 18, 12, 17],  # Home Fouls
        'AF': [14, 12, 16, 11, 13, 15, 10, 12, 14, 11],  # Away Fouls
        'HY': [1, 2, 1, 1, 2, 1, 3, 2, 1, 2],    # Home Yellow Cards
        'AY': [2, 1, 2, 1, 1, 2, 1, 1, 2, 1],    # Away Yellow Cards
        'HR': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],    # Home Red Cards
        'AR': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # Away Red Cards
    }
    return pd.DataFrame(sample_data)

# Load historical data
historical_data = load_historical_data()

# Authentication helper functions
def is_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False) and session.get('user_id') in users_db

def get_current_user():
    """Get current user data"""
    if is_authenticated():
        username = session.get('user_id')
        return users_db.get(username)
    return None

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def signup():
    """User registration endpoint"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', username)

        if not username or not password or not email:
            return jsonify({
                'success': False,
                'error': 'Username, email and password are required'
            }), 400

        # Check if user already exists
        if username in users_db:
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 400

        # Check if email already exists
        for user in users_db.values():
            if user.get('email') == email:
                return jsonify({
                    'success': False,
                    'error': 'Email already registered'
                }), 400

        # Add new user
        users_db[username] = {
            'password': password,
            'name': name,
            'email': email
        }

        # Create session
        session['user_id'] = username
        session['authenticated'] = True
        session.permanent = True

        print(f"✓ New user registered: {username}")

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'username': username,
                'name': name,
                'email': email
            },
            'access_token': f'token-{username}-{datetime.now().timestamp()}'
        })

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    """User login endpoint"""
    try:
        data = request.json
        login_input = data.get('username') or data.get('email')
        password = data.get('password')

        if not login_input or not password:
            return jsonify({
                'success': False,
                'error': 'Username/email and password are required'
            }), 400

        # Find user by username or email
        user = None
        username = None
        
        # Check if login input is username
        if login_input in users_db:
            user = users_db[login_input]
            username = login_input
        else:
            # Check if login input is email
            for uname, user_data in users_db.items():
                if user_data.get('email') == login_input:
                    user = user_data
                    username = uname
                    break

        # Check if user exists and password matches
        if user and user['password'] == password:
            # Create session
            session['user_id'] = username
            session['authenticated'] = True
            session.permanent = True

            print(f"✓ User logged in: {username}")

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'name': user['name'],
                    'email': user.get('email', '')
                },
                'access_token': f'token-{username}-{datetime.now().timestamp()}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid username/email or password'
            }), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/logout', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def logout():
    """User logout endpoint"""
    try:
        username = session.get('user_id')
        session.clear()
        print(f"✓ User logged out: {username}")
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500

@app.route('/api/check-auth', methods=['GET'])
@cross_origin(supports_credentials=True)
def check_auth():
    """Check if user is authenticated"""
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
                        'email': user_data.get('email', '')
                    }
                })
        
        return jsonify({
            'authenticated': False,
            'user': None
        })
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'user': None
        })

# =============================================================================
# MATCHES ENDPOINT - SINGLE VERSION
# =============================================================================

@app.route('/api/matches', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_upcoming_matches():
    """Get upcoming matches data"""
    try:
        # Check authentication
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401

        # Sample upcoming matches data
        upcoming_matches = [
            {
                'id': 1,
                'home_team': 'Man City',
                'away_team': 'Liverpool',
                'date': '2024-12-15',
                'time': '15:00',
                'venue': 'Etihad Stadium'
            },
            {
                'id': 2,
                'home_team': 'Arsenal',
                'away_team': 'Chelsea',
                'date': '2024-12-16',
                'time': '17:30',
                'venue': 'Emirates Stadium'
            },
            {
                'id': 3,
                'home_team': 'Man United',
                'away_team': 'Tottenham',
                'date': '2024-12-17',
                'time': '15:00',
                'venue': 'Old Trafford'
            },
            {
                'id': 4,
                'home_team': 'Newcastle',
                'away_team': 'Aston Villa',
                'date': '2024-12-18',
                'time': '15:00',
                'venue': 'St James Park'
            },
            {
                'id': 5,
                'home_team': 'West Ham',
                'away_team': 'Brighton',
                'date': '2024-12-19',
                'time': '19:45',
                'venue': 'London Stadium'
            }
        ]

        return jsonify({
            'matches': upcoming_matches,
            'count': len(upcoming_matches),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in get_upcoming_matches: {str(e)}")
        return jsonify({'error': 'Failed to fetch matches'}), 500

# =============================================================================
# PREDICTION ENDPOINTS
# =============================================================================

@app.route('/predict-ai-fixed', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def predict_ai_fixed():
    """Improved AI prediction with realistic goal calculation"""
    try:
        # Check authentication
        if not is_authenticated():
            return jsonify({'error': 'Authentication required. Please login first.'}), 401

        print("\n" + "="*40)
        print("PREDICTION REQUEST RECEIVED")
        print("="*40)
        
        data = request.json
        home_team = data.get('HomeTeam')
        away_team = data.get('AwayTeam')
        match_date = data.get('Date', pd.Timestamp.now().strftime('%Y-%m-%d'))
        
        print(f"Prediction for: {home_team} vs {away_team} on {match_date}")
        
        if not home_team or not away_team:
            return jsonify({'error': 'HomeTeam and AwayTeam are required'}), 400
        
        if home_team == away_team:
            return jsonify({'error': 'Teams must be different'}), 400
        
        # Calculate features
        print("Calculating team form...")
        home_form = calculate_team_form_fixed(home_team, match_date, 5)
        away_form = calculate_team_form_fixed(away_team, match_date, 5)
        
        print("Calculating H2H statistics...")
        h2h_stats = calculate_h2h_stats_fixed(home_team, away_team, match_date)
        
        # Simple prediction logic based on form
        form_diff = home_form['Points'] - away_form['Points']
        h2h_diff = h2h_stats['H2H_HomeWins'] - h2h_stats['H2H_AwayWins']
        
        # Combined decision making
        if form_diff > 4 or (form_diff > 2 and h2h_diff > 2):
            outcome = 'Home Win'
        elif form_diff < -4 or (form_diff < -2 and h2h_diff < -2):
            outcome = 'Away Win'
        else:
            outcome = 'Draw'
        
        # Calculate realistic goals
        home_goals, away_goals = calculate_realistic_goals(outcome, home_form, away_form, h2h_stats)
        
        # Calculate points
        if outcome == 'Home Win':
            home_points, away_points = 3, 0
        elif outcome == 'Away Win':
            home_points, away_points = 0, 3
        else:
            home_points, away_points = 1, 1
        
        # Calculate realistic confidence
        confidence = calculate_realistic_confidence(outcome, home_form, away_form, h2h_stats)
        
        response = {
            'outcome': outcome, 
            'goalDifference': home_goals - away_goals,
            'homeGoals': home_goals, 
            'awayGoals': away_goals,
            'homePoints': home_points, 
            'awayPoints': away_points,
            'confidence': confidence, 
            'predictionMethod': 'Form-based AI Model',
            'insights': {
                'homeForm': f"{home_form['Wins']} wins, {home_form['Points']} pts",
                'awayForm': f"{away_form['Wins']} wins, {away_form['Points']} pts",
                'h2hRecord': f"{h2h_stats['H2H_HomeWins']}-{h2h_stats['H2H_Draws']}-{h2h_stats['H2H_AwayWins']}",
                'formDifference': f"{form_diff} points"
            }
        }
        
        print(f"Prediction: {outcome} ({home_goals}-{away_goals}) - Confidence: {confidence:.1f}%")
        print("="*40)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"ERROR in prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

# =============================================================================
# CHAT ENDPOINTS
# =============================================================================

@app.route('/chat', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def chat():
    """Chat endpoint using Gemini AI with fallback"""
    try:
        # Check authentication
        if not is_authenticated():
            return jsonify({'error': 'Authentication required. Please login first.'}), 401

        data = request.json
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation', [])

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        print(f"Chat request: {user_message}")

        # Check if Google AI is available and model is initialized
        if not GOOGLE_AI_AVAILABLE or model is None:
            fallback_response = "I'm currently unavailable. Please make sure the Google Generative AI package is installed and a valid GEMINI_API_KEY is set in your environment variables."
            print("Using fallback response - AI not available")
            return jsonify({
                'response': fallback_response,
                'timestamp': datetime.now().isoformat(),
                'fallback': True
            })

        # Build conversation context
        context = get_football_context()
        
        # Add recent conversation history for context
        history_text = ""
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            sender = "User" if msg.get('sender') == 'user' else "Assistant"
            history_text += f"{sender}: {msg.get('text', '')}\n"

        # Create the prompt
        prompt = f"""
        {context}

        Recent conversation history:
        {history_text}

        Current user message: {user_message}

        Please provide a helpful, accurate response focused on English Premier League football.
        If the user is asking for a specific match prediction, explain the factors that would influence it.
        Keep responses concise but informative.
        """

        # Generate response with error handling
        try:
            response = model.generate_content(prompt)
            
            if response and response.text:
                return jsonify({
                    'response': response.text,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                })
            else:
                return jsonify({
                    'response': "I apologize, but I couldn't generate a response. Please try again.",
                    'timestamp': datetime.now().isoformat(),
                    'fallback': True
                })
                
        except Exception as gen_error:
            print(f"Gemini generation error: {gen_error}")
            return jsonify({
                'response': "I'm having trouble connecting to the AI service right now. Please try again in a moment.",
                'timestamp': datetime.now().isoformat(),
                'fallback': True
            })

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            'response': "I'm experiencing technical difficulties. Please try again later.",
            'error': str(e),
            'fallback': True
        }), 500

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.route('/test', methods=['GET'])
@cross_origin(supports_credentials=True)
def test_connection():
    """Test endpoint to check if server is working"""
    return jsonify({
        'message': 'Flask server is running!',
        'status': 'success',
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ai_chat_available': GOOGLE_AI_AVAILABLE,
        'model_initialized': model is not None,
        'gemini_api_key_set': bool(GEMINI_API_KEY),
        'session_enabled': True
    })

@app.route('/chat-test', methods=['GET'])
@cross_origin(supports_credentials=True)
def test_chat():
    """Test endpoint for chat functionality"""
    return jsonify({
        'message': 'Chat endpoint is working!',
        'ai_chat_available': GOOGLE_AI_AVAILABLE,
        'model_initialized': model is not None,
        'endpoints': {
            '/chat': 'POST - Send chat messages',
            '/predict-ai-fixed': 'POST - Get match predictions'
        }
    })

@app.route('/')
@cross_origin(supports_credentials=True)
def home():
    return jsonify({
        'message': 'ScoreSight EPL Predictor API',
        'version': '1.0',
        'status': 'running',
        'ai_chat_available': GOOGLE_AI_AVAILABLE,
        'model_initialized': model is not None,
        'gemini_api_key_set': bool(GEMINI_API_KEY),
        'endpoints': {
            '/api/login': 'POST - User login',
            '/api/signup': 'POST - User registration',
            '/api/logout': 'POST - User logout',
            '/api/check-auth': 'GET - Check authentication status',
            '/api/matches': 'GET - Get upcoming matches',
            '/test': 'GET - Test connection',
            '/predict-ai-fixed': 'POST - AI prediction with team names',
            '/chat': 'POST - Chat with Gemini AI assistant'
        },
        'demo_credentials': {
            'username': 'demo',
            'password': 'demo123'
        }
    })

# Add the missing helper functions
def calculate_team_form_fixed(team_name, date, n_matches=5):
    """Calculate team form from recent matches"""
    try:
        date = pd.Timestamp(date)
        team_matches = historical_data[
            ((historical_data['HomeTeam'] == team_name) | 
             (historical_data['AwayTeam'] == team_name)) &
            (historical_data['Date'] < date)
        ].sort_values('Date', ascending=False).head(n_matches)
        
        if len(team_matches) == 0:
            print(f"  No recent matches found for {team_name}")
            return {'GoalsFor': 0, 'GoalsAgainst': 0, 'Points': 0, 'Wins': 0}
        
        goals_for = 0
        goals_against = 0
        points = 0
        wins = 0
        
        print(f"  Recent matches for {team_name}:")
        for _, match in team_matches.iterrows():
            if match['HomeTeam'] == team_name:
                result = "W" if match['FTHG'] > match['FTAG'] else ("D" if match['FTHG'] == match['FTAG'] else "L")
                goals_for += match['FTHG']
                goals_against += match['FTAG']
                if match['FTHG'] > match['FTAG']:
                    points += 3
                    wins += 1
                elif match['FTHG'] == match['FTAG']:
                    points += 1
                print(f"    {match['HomeTeam']} {match['FTHG']}-{match['FTAG']} {match['AwayTeam']} ({result})")
            else:
                result = "W" if match['FTAG'] > match['FTHG'] else ("D" if match['FTAG'] == match['FTHG'] else "L")
                goals_for += match['FTAG']
                goals_against += match['FTHG']
                if match['FTAG'] > match['FTHG']:
                    points += 3
                    wins += 1
                elif match['FTAG'] == match['FTHG']:
                    points += 1
                print(f"    {match['AwayTeam']} {match['FTAG']}-{match['FTHG']} {match['HomeTeam']} ({result})")
        
        print(f"  Form summary: {points} pts, {wins} wins, {goals_for} GF, {goals_against} GA")
        return {
            'GoalsFor': goals_for,
            'GoalsAgainst': goals_against,
            'Points': points,
            'Wins': wins
        }
    except Exception as e:
        print(f"Error calculating form for {team_name}: {e}")
        return {'GoalsFor': 0, 'GoalsAgainst': 0, 'Points': 0, 'Wins': 0}

def calculate_h2h_stats_fixed(home_team, away_team, date):
    """Calculate head-to-head statistics"""
    try:
        date = pd.Timestamp(date)
        h2h_matches = historical_data[
            (((historical_data['HomeTeam'] == home_team) & (historical_data['AwayTeam'] == away_team)) |
             ((historical_data['HomeTeam'] == away_team) & (historical_data['AwayTeam'] == home_team))) &
            (historical_data['Date'] < date)
        ].sort_values('Date', ascending=False).head(10)
        
        print(f"  H2H matches found: {len(h2h_matches)}")
        
        if len(h2h_matches) == 0:
            print(f"  No H2H history between {home_team} and {away_team}")
            return {
                'H2H_HomeWins': 0, 'H2H_AwayWins': 0, 'H2H_Draws': 0,
                'H2H_HomeGoals': 0, 'H2H_AwayGoals': 0, 'H2H_TotalMatches': 0,
                'H2H_HomeWinRate': 0, 'H2H_AwayWinRate': 0,
                'H2H_AvgGoals_Home': 0, 'H2H_AvgGoals_Away': 0
            }
        
        home_wins = 0
        away_wins = 0
        draws = 0
        home_goals = 0
        away_goals = 0
        
        print(f"  H2H matches:")
        for _, match in h2h_matches.iterrows():
            if match['HomeTeam'] == home_team:
                home_goals += match['FTHG']
                away_goals += match['FTAG']
                if match['FTHG'] > match['FTAG']:
                    home_wins += 1
                    result = f"{home_team} WIN"
                elif match['FTAG'] > match['FTHG']:
                    away_wins += 1
                    result = f"{away_team} WIN"
                else:
                    draws += 1
                    result = "DRAW"
                print(f"    {match['HomeTeam']} {match['FTHG']}-{match['FTAG']} {match['AwayTeam']} ({result})")
            else:
                home_goals += match['FTAG']
                away_goals += match['FTHG']
                if match['FTAG'] > match['FTHG']:
                    home_wins += 1
                    result = f"{home_team} WIN"
                elif match['FTHG'] > match['FTAG']:
                    away_wins += 1
                    result = f"{away_team} WIN"
                else:
                    draws += 1
                    result = "DRAW"
                print(f"    {match['AwayTeam']} {match['FTAG']}-{match['FTHG']} {match['HomeTeam']} ({result})")
        
        total_matches = len(h2h_matches)
        home_win_rate = home_wins / total_matches if total_matches > 0 else 0
        away_win_rate = away_wins / total_matches if total_matches > 0 else 0
        avg_goals_home = home_goals / total_matches if total_matches > 0 else 0
        avg_goals_away = away_goals / total_matches if total_matches > 0 else 0
        
        print(f"  H2H Summary: Home wins: {home_wins}, Away wins: {away_wins}, Draws: {draws}")
        
        return {
            'H2H_HomeWins': home_wins, 'H2H_AwayWins': away_wins, 'H2H_Draws': draws,
            'H2H_HomeGoals': home_goals, 'H2H_AwayGoals': away_goals, 'H2H_TotalMatches': total_matches,
            'H2H_HomeWinRate': home_win_rate, 'H2H_AwayWinRate': away_win_rate,
            'H2H_AvgGoals_Home': avg_goals_home, 'H2H_AvgGoals_Away': avg_goals_away
        }
    except Exception as e:
        print(f"Error calculating H2H stats: {e}")
        return {
            'H2H_HomeWins': 0, 'H2H_AwayWins': 0, 'H2H_Draws': 0,
            'H2H_HomeGoals': 0, 'H2H_AwayGoals': 0, 'H2H_TotalMatches': 0,
            'H2H_HomeWinRate': 0, 'H2H_AwayWinRate': 0,
            'H2H_AvgGoals_Home': 0, 'H2H_AvgGoals_Away': 0
        }

def calculate_realistic_goals(outcome, home_form, away_form, h2h_stats):
    """Calculate realistic goal scores based on outcome and statistics"""
    try:
        # Base goal expectations from historical data
        avg_home_goals = 1.5
        avg_away_goals = 1.2
        
        # Adjust based on team form
        home_goal_factor = min(2.0, 1.0 + (home_form['GoalsFor'] / max(1, home_form['GoalsAgainst'])) * 0.3)
        away_goal_factor = min(2.0, 1.0 + (away_form['GoalsFor'] / max(1, away_form['GoalsAgainst'])) * 0.3)
        
        if outcome == 'Home Win':
            # Home team should score more
            base_home_goals = avg_home_goals * home_goal_factor
            base_away_goals = avg_away_goals * (1.0 / away_goal_factor)
            
            home_goals = max(1, int(base_home_goals + 0.5))
            away_goals = max(0, int(base_away_goals - 0.3))
            
            # Ensure home goals > away goals
            if home_goals <= away_goals:
                home_goals = away_goals + 1
                
        elif outcome == 'Away Win':
            # Away team should score more
            base_home_goals = avg_home_goals * (1.0 / home_goal_factor)
            base_away_goals = avg_away_goals * away_goal_factor
            
            away_goals = max(1, int(base_away_goals + 0.5))
            home_goals = max(0, int(base_home_goals - 0.3))
            
            # Ensure away goals > home goals
            if away_goals <= home_goals:
                away_goals = home_goals + 1
                
        else:  # Draw
            # Both teams score similar goals
            base_goals = (avg_home_goals + avg_away_goals) / 2
            home_goals = away_goals = max(0, int(base_goals))
            
            # Avoid 0-0 draws too frequently
            if home_goals == 0 and away_goals == 0:
                home_goals = away_goals = 1
        
        # Ensure goals are realistic (not too high)
        home_goals = min(5, home_goals)
        away_goals = min(5, away_goals)
        
        return int(home_goals), int(away_goals)
        
    except Exception as e:
        print(f"Error calculating realistic goals: {e}")
        # Fallback to simple calculation
        if outcome == 'Home Win':
            return 2, 1
        elif outcome == 'Away Win':
            return 1, 2
        else:
            return 1, 1

def calculate_realistic_confidence(outcome, home_form, away_form, h2h_stats):
    """Calculate realistic confidence score"""
    try:
        base_confidence = 65  # Start with reasonable base
        
        # Adjust based on form difference
        form_diff = abs(home_form['Points'] - away_form['Points'])
        form_boost = min(15, form_diff * 2)
        base_confidence += form_boost
        
        # Adjust based on H2H dominance
        total_h2h_matches = h2h_stats['H2H_TotalMatches']
        if total_h2h_matches > 0:
            if outcome == 'Home Win' and h2h_stats['H2H_HomeWinRate'] > 0.6:
                base_confidence += 10
            elif outcome == 'Away Win' and h2h_stats['H2H_AwayWinRate'] > 0.6:
                base_confidence += 10
        
        # Ensure confidence is within reasonable bounds
        confidence = max(55, min(90, base_confidence))
        
        return round(confidence, 1)
        
    except Exception as e:
        print(f"Error calculating confidence: {e}")
        return 70.0

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Google AI Available: {'Yes' if GOOGLE_AI_AVAILABLE else 'No'}")
    print(f"Gemini API Key Set: {'Yes' if GEMINI_API_KEY else 'No'}")
    print(f"Model Initialized: {'Yes' if model else 'No'}")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)