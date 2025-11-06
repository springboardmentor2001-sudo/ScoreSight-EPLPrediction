from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import os
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)

# Enhanced CORS configuration
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": True
    }
})

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

print("=" * 60)
print("ScoreSight EPL Predictor API - Starting Up")
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

# Load historical data
historical_data = load_historical_data()

# =============================================================================
# PREDICTION ENDPOINTS
# =============================================================================

@app.route('/predict-ai-fixed', methods=['POST', 'OPTIONS'])
@cross_origin()
def predict_ai_fixed():
    """Improved AI prediction with realistic goal calculation"""
    try:
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
@cross_origin()
def chat():
    """Chat endpoint using Gemini AI"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation', [])

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        print(f"Chat request: {user_message}")

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

        # Generate response
        response = model.generate_content(prompt)

        if response.text:
            return jsonify({
                'response': response.text,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'response': "I apologize, but I couldn't generate a response. Please try again.",
                'timestamp': datetime.now().isoformat()
            }), 500

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            'response': "I'm experiencing technical difficulties. Please try again later.",
            'error': str(e)
        }), 500

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.route('/test', methods=['GET'])
@cross_origin()
def test_connection():
    """Test endpoint to check if server is working"""
    return jsonify({
        'message': 'Flask server is running!',
        'status': 'success',
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/chat-test', methods=['GET'])
@cross_origin()
def test_chat():
    """Test endpoint for chat functionality"""
    return jsonify({
        'message': 'Chat endpoint is working!',
        'endpoints': {
            '/chat': 'POST - Send chat messages',
            '/predict-ai-fixed': 'POST - Get match predictions'
        }
    })

@app.route('/')
@cross_origin()
def home():
    return jsonify({
        'message': 'ScoreSight EPL Predictor API with Gemini Chat',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            '/test': 'GET - Test connection',
            '/chat-test': 'GET - Test chat connection',
            '/predict-ai-fixed': 'POST - AI prediction with team names',
            '/chat': 'POST - Chat with Gemini AI assistant'
        }
    })

if __name__ == '__main__':
    print("Starting Flask server with Gemini AI...")
    print(f"Gemini API configured: {'Yes' if GEMINI_API_KEY != 'your-gemini-api-key-here' else 'No - using placeholder'}")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)