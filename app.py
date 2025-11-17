import os
import json
import hashlib
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.predictor import predict_match_result
import json
import os
import pickle
import numpy as np
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Add Google Gemini API configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
genai = None
if api_key:
    import google.generativeai as genai_module
    genai = genai_module
    # Use getattr to avoid linter issues
    configure_func = getattr(genai_module, 'configure')
    configure_func(api_key=api_key)

# Initialize Flask app with a secret key for sessions
app = Flask(__name__)
app.secret_key = 'score_sight_secret_key_2025'

# Enable session debugging
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# API Configuration for football-data.org
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY') or 'e24819cf63134688b0cba8c8990137ac'
API_BASE_URL = 'https://api.football-data.org/v4'
API_HEADERS = {
    'X-Response-Control': 'minified',
    'X-Response-Format': 'json',
    'X-Auth-Token': API_KEY
}

# Load our trained models and encoders
try:
    import joblib
    match_winner_model = joblib.load('match_winner_model.pkl')
    fthg_model = joblib.load('fthg_model.pkl')
    ftag_model = joblib.load('ftag_model.pkl')
    home_team_encoder = joblib.load('home_team_encoder.pkl')
    away_team_encoder = joblib.load('away_team_encoder.pkl')
    print("Models and encoders loaded successfully!")
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    import traceback
    traceback.print_exc()
    # Continue with the app even if models fail to load
    match_winner_model = None
    fthg_model = None
    ftag_model = None
    home_team_encoder = None
    away_team_encoder = None
    models_loaded = False

# Import the RapidAPI client dynamically to avoid static import resolution errors
try:
    import importlib
    rapidapi_module = importlib.import_module('rapidapi_client')
    get_rapidapi_news = getattr(rapidapi_module, 'get_news', None)
    get_rapidapi_standings = getattr(rapidapi_module, 'get_standings', None)
    RAPIDAPI_AVAILABLE = bool(get_rapidapi_news or get_rapidapi_standings)
    if RAPIDAPI_AVAILABLE:
        print("RapidAPI client loaded successfully!")
    else:
        print("RapidAPI client loaded but required functions are missing.")
except Exception as e:
    print(f"RapidAPI client not available: {e}")
    get_rapidapi_news = None
    get_rapidapi_standings = None
    RAPIDAPI_AVAILABLE = False

# Map team names to their logo filenames
# This helps us display the correct team logos in the UI
team_logo_mapping = {
    'Arsenal': 'Arsenal-Logo.png',
    'Arsenal FC': 'Arsenal-Logo.png',
    'Aston Villa': 'Aston Villa.png',
    'Aston Villa FC': 'Aston Villa.png',
    'Birmingham': 'Birmingham.png',
    'Blackburn': 'Blackburn.png',
    'Blackpool': 'Blackpool.png',
    'Bolton': 'Bolton.png',
    'Bournemouth': 'Bournemouth.jpg',
    'AFC Bournemouth': 'Bournemouth.jpg',
    'Brighton': 'Brighton.webp',
    'Brighton & Hove Albion': 'Brighton.webp',
    'Brighton & Hove Albion FC': 'Brighton.webp',
    'Burnley': 'Burnley.png',
    'Burnley FC': 'Burnley.png',
    'Cardiff': 'Cardiff.jpg',
    'Chelsea': 'Chelsea.png',
    'Chelsea FC': 'Chelsea.png',
    'Crystal Palace': 'Crystal Palace.jpg',
    'Crystal Palace FC': 'Crystal Palace.jpg',
    'Everton': 'Everton.png',
    'Everton FC': 'Everton.png',
    'Fulham': 'Fulham.png',
    'Fulham FC': 'Fulham.png',
    'Hull': 'Hull.jpg',
    'Huddersfield': 'Hundersfield.png',
    'Huddersfield Town AFC': 'Hundersfield.png',
    'Leicester': 'Leicester.png',
    'Leicester City': 'Leicester.png',
    'Leicester City FC': 'Leicester.png',
    'Liverpool': 'Liverpool.png',
    'Liverpool FC': 'Liverpool.png',
    'Man City': 'Man City.jpg',
    'Manchester City': 'Man City.jpg',
    'Manchester City FC': 'Man City.jpg',
    'Man United': 'Man United.png',
    'Manchester United': 'Man United.png',
    'Manchester United FC': 'Man United.png',
    'Middlesbrough': 'Middlesbrough.png',
    'Newcastle': 'Newcastle United.png',
    'Newcastle United': 'Newcastle United.png',
    'Newcastle United FC': 'Newcastle United.png',
    'Norwich': 'Norwich.png',
    'Norwich City FC': 'Norwich.png',
    'QPR': 'QPR.png',
    'Queens Park Rangers FC': 'QPR.png',
    'Reading': 'Reading.png',
    'Sheffield United': 'Sheffield United.jpg',
    'Sheffield United FC': 'Sheffield United.jpg',
    'Southampton': 'SouthAmpton.jpeg',
    'Southampton FC': 'SouthAmpton.jpeg',
    'Stoke': 'Stock.png',
    'Stoke City FC': 'Stock.png',
    'Sunderland': 'Sunderland.png',
    'Sunderland AFC': 'Sunderland.png',
    'Swansea': 'Swansea.png',
    'Swansea City AFC': 'Swansea.png',
    'Tottenham': 'Tottenham.png',
    'Tottenham Hotspur': 'Tottenham.png',
    'Tottenham Hotspur FC': 'Tottenham.png',
    'Watford': 'Watford.png',
    'Watford FC': 'Watford.png',
    'West Brom': 'West Brom.jpg',
    'West Bromwich Albion FC': 'West Brom.jpg',
    'West Ham': 'West Ham.png',
    'West Ham United': 'West Ham.png',
    'West Ham United FC': 'West Ham.png',
    'Wigan': 'Wigan.png',
    'Wigan Athletic FC': 'Wigan.png',
    'Wolves': 'Wolves.png',
    'Wolverhampton Wanderers': 'Wolves.png',
    'Wolverhampton Wanderers FC': 'Wolves.png',
    # Add missing teams from sample data
    'Leeds United': 'Leeds United.png',
    'Leeds United FC': 'Leeds United.png',
    'Brentford': 'Brentford.png',
    'Brentford FC': 'Brentford.png',
    'Nottingham Forest': 'Nottingham Forest.png',
    'Nottingham Forest FC': 'Nottingham Forest.png',
    'Luton Town': 'Luton Town.png',
    'Luton Town FC': 'Luton Town.png'
}

def get_team_logo(team_name):
    """Get team logo filename with improved fuzzy matching"""
    # Direct match first
    if team_name in team_logo_mapping:
        return team_logo_mapping[team_name]
    
    # Try case-insensitive exact match
    for key, value in team_logo_mapping.items():
        if key.lower() == team_name.lower():
            return value
    
    # Try partial matching for common cases (more restrictive)
    for key, value in team_logo_mapping.items():
        # Check if the mapping key is contained in the team name or vice versa
        # But be more careful to avoid false positives
        if (key.lower() in team_name.lower() and len(key) > 3) or \
           (team_name.lower() in key.lower() and len(team_name) > 3):
            return value
    
    # Return a generic default logo instead of Arsenal logo
    return 'score_sight_logo2.png'

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a password against its hash"""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def convert_utc_to_ist(utc_datetime_str):
    """Convert UTC datetime string to IST datetime string"""
    try:
        # Parse the UTC datetime string
        utc_dt = datetime.strptime(utc_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
        
        # Set timezone to UTC
        utc_dt = pytz.utc.localize(utc_dt)
        
        # Convert to IST (UTC+5:30)
        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_dt = utc_dt.astimezone(ist_tz)
        
        # Return formatted IST datetime string with timezone info
        return ist_dt.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception as e:
        print(f"Error converting timezone: {e}")
        # Return original string with IST label if conversion fails
        return f"{utc_datetime_str} IST"

def load_users():
    """Load users from JSON file with improved error handling"""
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
        return users
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_users(users):
    """Save users to JSON file with improved error handling"""
    try:
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def authenticate_user(username, password):
    """Check if username and password match our records"""
    users = load_users()
    if username in users:
        return verify_password(users[username], password)
    return False

def register_user(username, email, password):
    """Register a new user if username is not already taken"""
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

def fetch_live_matches():
    """Fetch live matches from football-data.org API including competition info"""
    try:
        print("Fetching live matches from API...")
        url = "https://api.football-data.org/v4/matches"
        headers = {
            'X-Response-Control': 'minified',
            'X-Auth-Token': API_KEY
        }
        
        # Get today's date for filtering
        today = datetime.now().strftime('%Y-%m-%d')
        params = {
            'dateFrom': today,
            'dateTo': today,
            'status': 'IN_PLAY,LIVE,PAUSED'
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Live matches API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Live matches data keys: {data.keys()}")
            
            matches = []
            if 'matches' in data:
                # Filter for important competitions including World Cup Qualifiers
                important_competitions = [
                    '2021',  # Premier League
                    '2014',  # La Liga
                    '2002',  # Bundesliga
                    '2019',  # Serie A
                    '2015',  # Ligue 1
                    '2007',  # WC Qualification UEFA
                    '2006',  # WC Qualification CAF
                    '2147',  # WC Qualification AFC
                    '2082',  # WC Qualification CONMEBOL
                    '2155',  # WC Qualification CONCACAF
                    '2103',  # WC Qualification OFC
                    '2000',  # FIFA World Cup
                    '2018',  # European Championship
                    '2001',  # UEFA Champions League
                    '2146',  # UEFA Europa League
                    '2154',  # UEFA Conference League
                    '2024',  # Argentina Liga Profesional
                    '2013',  # Brazil Serie A
                    '2145',  # MLS
                    '2080',  # Copa America
                    '2152'   # Copa Libertadores
                ]
                
                filtered_matches = []
                for match in data['matches']:
                    competition_id = str(match.get('competition', {}).get('id', ''))
                    if competition_id in important_competitions:
                        filtered_matches.append(match)
                
                for match in filtered_matches:
                    utc_date_str = match.get('utcDate', '')
                    # Convert UTC to IST
                    formatted_date = convert_utc_to_ist(utc_date_str)
                    
                    home_team_name = match.get('homeTeam', {}).get('name', 'Unknown')
                    away_team_name = match.get('awayTeam', {}).get('name', 'Unknown')
                    competition_name = match.get('competition', {}).get('name', 'Unknown Competition')
                    
                    matches.append({
                        'homeTeam': home_team_name,
                        'awayTeam': away_team_name,
                        'score': f"{match.get('score', {}).get('fullTime', {}).get('home', 0)} - {match.get('score', {}).get('fullTime', {}).get('away', 0)}",
                        'status': match.get('status', 'Unknown'),
                        'minute': match.get('minute', 'N/A'),
                        'date': formatted_date,
                        'competition': competition_name
                    })
            
            print(f"Processed live matches count: {len(matches)}")
            return matches
        else:
            print(f"Error fetching live matches: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception in fetch_live_matches: {e}")
        return []

def fetch_upcoming_matches():
    """Fetch upcoming matches from football-data.org API including World Cup Qualifiers"""
    try:
        print("Fetching upcoming matches from API...")
        url = "https://api.football-data.org/v4/matches"
        headers = {
            'X-Response-Control': 'minified',
            'X-Auth-Token': API_KEY
        }
        
        # Get today's date for filtering
        today = datetime.now().strftime('%Y-%m-%d')
        params = {
            'dateFrom': today,
            'dateTo': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),  # Extend to 7 days
            'status': 'SCHEDULED'
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Upcoming matches API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Upcoming matches data keys: {data.keys()}")
            print(f"Sample matches data: {data.get('matches', [])[:2] if data.get('matches') else []}")
            
            matches = []
            if 'matches' in data:
                # Filter for important competitions including World Cup Qualifiers
                important_competitions = [
                    '2021',  # Premier League
                    '2014',  # La Liga
                    '2002',  # Bundesliga
                    '2019',  # Serie A
                    '2015',  # Ligue 1
                    '2007',  # WC Qualification UEFA
                    '2006',  # WC Qualification CAF
                    '2147',  # WC Qualification AFC
                    '2082',  # WC Qualification CONMEBOL
                    '2155',  # WC Qualification CONCACAF
                    '2103',  # WC Qualification OFC
                    '2000',  # FIFA World Cup
                    '2018',  # European Championship
                    '2001',  # UEFA Champions League
                    '2146',  # UEFA Europa League
                    '2154',  # UEFA Conference League
                    '2024',  # Argentina Liga Profesional
                    '2013',  # Brazil Serie A
                    '2145',  # MLS
                    '2080',  # Copa America
                    '2152'   # Copa Libertadores
                ]
                
                filtered_matches = []
                for match in data['matches']:
                    competition_id = str(match.get('competition', {}).get('id', ''))
                    if competition_id in important_competitions:
                        filtered_matches.append(match)
                
                # Process filtered matches
                for match in filtered_matches[:15]:  # Increase limit to 15 matches
                    utc_date_str = match.get('utcDate', '')
                    # Convert UTC to IST
                    formatted_date = convert_utc_to_ist(utc_date_str)
                    
                    home_team_name = match.get('homeTeam', {}).get('name', 'Unknown')
                    away_team_name = match.get('awayTeam', {}).get('name', 'Unknown')
                    competition_name = match.get('competition', {}).get('name', 'Unknown Competition')
                    
                    print(f"Processing match: {home_team_name} vs {away_team_name} in {competition_name}")
                    print(f"Home team logo key: {get_team_logo(home_team_name)}")
                    print(f"Away team logo key: {get_team_logo(away_team_name)}")
                    
                    matches.append({
                        'homeTeam': home_team_name,
                        'awayTeam': away_team_name,
                        'date': formatted_date,
                        'status': match.get('status', 'SCHEDULED'),
                        'competition': competition_name
                    })
            
            print(f"Processed upcoming matches count: {len(matches)}")
            print(f"Upcoming matches: {matches}")
            return matches
        else:
            print(f"Error fetching upcoming matches: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception in fetch_upcoming_matches: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_epl_standings():
    """Fetch EPL standings from football-data.org API"""
    try:
        # Try RapidAPI first if available
        if RAPIDAPI_AVAILABLE and get_rapidapi_standings is not None:
            print("Fetching EPL standings from RapidAPI...")
            rapidapi_standings = get_rapidapi_standings()
            if rapidapi_standings and 'standings' in rapidapi_standings:
                standings = []
                for i, team in enumerate(rapidapi_standings['standings']):
                    # Use actual form data if available, otherwise generate sample data
                    form_data = team.get('form')
                    if not form_data:
                        import random
                        form_results = ['W', 'D', 'L']
                        form_data = ','.join(random.choices(form_results, k=5))
                    
                    standings.append({
                        'position': team.get('position', i+1),
                        'team': team.get('team', 'Unknown'),
                        'team_logo': team.get('logo', ''),
                        'played': team.get('played', 0),
                        'won': team.get('won', 0),
                        'drawn': team.get('drawn', 0),
                        'lost': team.get('lost', 0),
                        'goals_for': team.get('goals_for', 0),
                        'goals_against': team.get('goals_against', 0),
                        'goal_difference': team.get('goal_difference', 0),
                        'points': team.get('points', 0),
                        'form': form_data.split(',') if form_data else []
                    })
                print(f"RapidAPI standings fetched successfully, count: {len(standings)}")
                return standings
        
        # Fallback to football-data.org API
        print("Fetching EPL standings from API...")
        url = "https://api.football-data.org/v4/competitions/PL/standings"
        headers = {
            'X-Response-Control': 'minified',
            'X-Auth-Token': API_KEY
        }
        
        response = requests.get(url, headers=headers)
        print(f"EPL standings API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"EPL standings data keys: {data.keys()}")
            
            standings = []
            if 'standings' in data and len(data['standings']) > 0:
                table_data = data['standings'][0].get('table', [])
                print(f"Table data count: {len(table_data)}")
                
                for team in table_data:
                    form_data = team.get('form')
                    print(f"Team {team.get('team', {}).get('name', 'Unknown')} form data: {form_data}")
                    
                    # Process form data correctly - it should already be in the right format
                    # If form data is None or empty, generate sample data
                    if not form_data:
                        # Generate sample form data (W=Win, D=Draw, L=Loss)
                        import random
                        form_results = ['W', 'D', 'L']
                        form_data = ','.join(random.choices(form_results, k=5))
                        print(f"Using sample form data for {team.get('team', {}).get('name', 'Unknown')}: {form_data}")
                    
                    standings.append({
                        'position': team.get('position', 0),
                        'team': team.get('team', {}).get('name', 'Unknown'),
                        'team_logo': team.get('team', {}).get('crest', ''),
                        'played': team.get('playedGames', 0),
                        'won': team.get('won', 0),
                        'drawn': team.get('draw', 0),
                        'lost': team.get('lost', 0),
                        'goals_for': team.get('goalsFor', 0),
                        'goals_against': team.get('goalsAgainst', 0),
                        'goal_difference': team.get('goalDifference', 0),
                        'points': team.get('points', 0),
                        'form': form_data.split(',') if isinstance(form_data, str) else (form_data if isinstance(form_data, list) else [])
                    })
            
            print(f"Processed EPL standings: {standings}")
            return standings
        else:
            print(f"Error fetching EPL standings: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception in fetch_epl_standings: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_epl_news():
    """Fetch EPL news from NewsAPI"""
    try:
        # Try RapidAPI first if available
        if RAPIDAPI_AVAILABLE and get_rapidapi_news is not None:
            print("Fetching EPL news from RapidAPI...")
            rapidapi_news = get_rapidapi_news()
            if rapidapi_news and 'news' in rapidapi_news:
                news_data = []
                for article in rapidapi_news['news'][:5]:  # Limit to 5 articles
                    news_data.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'publishedAt': article.get('publishedAt', '')
                    })
                print(f"RapidAPI news fetched successfully, count: {len(news_data)}")
                return news_data
        
        # Fallback to NewsAPI
        print("Fetching EPL news from NewsAPI...")
        NEWS_API_KEY = os.getenv('NEWS_API_KEY')
        if not NEWS_API_KEY:
            print("News API key not found, returning sample data")
            # Return sample news data when API key is not available
            return [
                {
                    'title': 'Erling Haaland Sets New Premier League Scoring Record',
                    'description': 'Manchester City striker Erling Haaland has broken the Premier League record for most goals scored in a single season, surpassing the previous mark with his 34th goal of the campaign.',
                    'url': 'https://www.example.com/haaland-record',
                    'publishedAt': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                {
                    'title': 'Arsenal Secures Champions League Qualification After Dramatic Win',
                    'description': 'Arsenal secured their return to the Champions League after a thrilling 3-2 victory over Tottenham in the North London Derby, finishing the season in second place.',
                    'url': 'https://www.example.com/arsenal-champions-league',
                    'publishedAt': (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                {
                    'title': 'Liverpool Appoints New Sporting Director',
                    'description': 'Liverpool FC has announced the appointment of a new sporting director to oversee transfer operations and work closely with manager Jurgen Klopp on squad building for the upcoming season.',
                    'url': 'https://www.example.com/liverpool-sporting-director',
                    'publishedAt': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                {
                    'title': 'Chelsea Completes Record-Breaking Transfer Deal',
                    'description': 'Chelsea has broken their club transfer record to sign a talented midfielder from a top European club for a reported fee of £110 million, signaling their ambition for the future.',
                    'url': 'https://www.example.com/chelsea-transfer',
                    'publishedAt': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                {
                    'title': 'Manchester United Unveils New Stadium Expansion Plans',
                    'description': 'Manchester United has revealed ambitious plans to expand Old Trafford with the addition of a new South Stand, which would increase the stadium capacity to over 80,000 seats.',
                    'url': 'https://www.example.com/man-utd-stadium',
                    'publishedAt': (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            ]
            
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'Premier League OR EPL OR "Manchester United" OR "Liverpool" OR "Arsenal" OR "Chelsea" OR "Manchester City" OR "Tottenham"',
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 5
        }
        headers = {'Authorization': f'Bearer {NEWS_API_KEY}'}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            news_data = []
            
            for article in articles:
                news_data.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'publishedAt': article.get('publishedAt', '')
                })
            
            print(f"EPL news fetched successfully, count: {len(news_data)}")
            return news_data
        else:
            print(f"Error fetching news: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception in fetch_epl_news: {e}")
        # Return sample data on error
        return [
            {
                'title': 'Erling Haaland Sets New Premier League Scoring Record',
                'description': 'Manchester City striker Erling Haaland has broken the Premier League record for most goals scored in a single season, surpassing the previous mark with his 34th goal of the campaign.',
                'url': 'https://www.example.com/haaland-record',
                'publishedAt': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                'title': 'Arsenal Secures Champions League Qualification After Dramatic Win',
                'description': 'Arsenal secured their return to the Champions League after a thrilling 3-2 victory over Tottenham in the North London Derby, finishing the season in second place.',
                'url': 'https://www.example.com/arsenal-champions-league',
                'publishedAt': (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                'title': 'Liverpool Appoints New Sporting Director',
                'description': 'Liverpool FC has announced the appointment of a new sporting director to oversee transfer operations and work closely with manager Jurgen Klopp on squad building for the upcoming season.',
                'url': 'https://www.example.com/liverpool-sporting-director',
                'publishedAt': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                'title': 'Chelsea Completes Record-Breaking Transfer Deal',
                'description': 'Chelsea has broken their club transfer record to sign a talented midfielder from a top European club for a reported fee of £110 million, signaling their ambition for the future.',
                'url': 'https://www.example.com/chelsea-transfer',
                'publishedAt': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                'title': 'Manchester United Unveils New Stadium Expansion Plans',
                'description': 'Manchester United has revealed ambitious plans to expand Old Trafford with the addition of a new South Stand, which would increase the stadium capacity to over 80,000 seats.',
                'url': 'https://www.example.com/man-utd-stadium',
                'publishedAt': (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ]

def fetch_previous_matches():
    """
    Fetch previous matches from football-data.org API including World Cup Qualifiers
    Returns a list of previous matches or sample data if API call fails or returns no data
    """
    try:
        print("Fetching previous matches from API...")
        url = "https://api.football-data.org/v4/matches"
        headers = {
            'X-Response-Control': 'minified',
            'X-Auth-Token': API_KEY
        }
        
        # Get date range for filtering (last 7 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        params = {
            'dateFrom': start_date,
            'dateTo': end_date,
            'status': 'FINISHED'
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Previous matches API response status: {response.status_code}")
        
        # Handle rate limiting (429) gracefully
        if response.status_code == 429:
            print("Rate limited by API, returning sample data")
            return get_sample_previous_matches()
            
        response.raise_for_status()
        data = response.json()
        print(f"Previous matches data keys: {data.keys()}")
        
        matches = []
        if 'matches' in data:
            # Filter for important competitions including World Cup Qualifiers
            important_competitions = [
                '2021',  # Premier League
                '2014',  # La Liga
                '2002',  # Bundesliga
                '2019',  # Serie A
                '2015',  # Ligue 1
                '2007',  # WC Qualification UEFA
                '2006',  # WC Qualification CAF
                '2147',  # WC Qualification AFC
                '2082',  # WC Qualification CONMEBOL
                '2155',  # WC Qualification CONCACAF
                '2103',  # WC Qualification OFC
                '2000',  # FIFA World Cup
                '2018',  # European Championship
                '2001',  # UEFA Champions League
                '2146',  # UEFA Europa League
                '2154',  # UEFA Conference League
                '2024',  # Argentina Liga Profesional
                '2013',  # Brazil Serie A
                '2145',  # MLS
                '2080',  # Copa America
                '2152'   # Copa Libertadores
            ]
            
            filtered_matches = []
            for match in data['matches']:
                competition_id = str(match.get('competition', {}).get('id', ''))
                if competition_id in important_competitions:
                    filtered_matches.append(match)
            
            # Get last 10 finished matches (or sample data if none available)
            api_matches = filtered_matches
            if not api_matches:
                print("No matches returned from API, returning sample data")
                return get_sample_previous_matches()
            
            # Get last 10 finished matches
            for match in api_matches[-10:]:
                # Get match statistics if available
                score_data = match.get('score', {})
                full_time = score_data.get('fullTime', {})
                half_time = score_data.get('halfTime', {})
                
                utc_date_str = match.get('utcDate', '')
                # Convert UTC to IST
                formatted_date = convert_utc_to_ist(utc_date_str)
                
                home_team_name = match.get('homeTeam', {}).get('name', 'Home Team')
                away_team_name = match.get('awayTeam', {}).get('name', 'Away Team')
                competition_name = match.get('competition', {}).get('name', 'Unknown Competition')
                
                matches.append({
                    "id": match.get('id'),
                    "date": formatted_date,
                    "homeTeam": home_team_name,
                    "awayTeam": away_team_name,
                    "home_score": full_time.get('home', 0),
                    "away_score": full_time.get('away', 0),
                    "league": competition_name,
                    "matchday": match.get('matchday', 'N/A'),
                    "home_team_crest": match.get('homeTeam', {}).get('crest', ''),
                    "away_team_crest": match.get('awayTeam', {}).get('crest', ''),
                    "highlights_url": f"https://www.hotstar.com/in/sports/football/match-highlights/{match.get('id', 'latest')}",
                    "stats": {
                        "home_shots": 'N/A',  # API doesn't provide detailed stats in this endpoint
                        "away_shots": 'N/A',
                        "home_shots_on_target": 'N/A',
                        "away_shots_on_target": 'N/A',
                        "home_corners": 'N/A',
                        "away_corners": 'N/A',
                        "home_fouls": 'N/A',
                        "away_fouls": 'N/A',
                        "home_yellow_cards": 'N/A',
                        "away_yellow_cards": 'N/A',
                        "home_red_cards": 'N/A',
                        "away_red_cards": 'N/A'
                    }
                })
        print(f"Processed previous matches count: {len(matches)}")
        return matches
    except Exception as e:
        print(f"Error fetching previous matches: {e}")
        # Return sample data with stats if API fails
        return get_sample_previous_matches()

def get_sample_previous_matches():
    """Return sample previous matches data"""
    return [
        {
            "id": 1,
            "date": "2025-11-01T15:00:00Z",
            "homeTeam": "Arsenal FC",
            "awayTeam": "Manchester City FC",
            "home_score": 2,
            "away_score": 1,
            "league": "Premier League",
            "matchday": 12,
            "home_team_crest": "https://crests.football-data.org/57.png",
            "away_team_crest": "https://crests.football-data.org/65.png",
            "highlights_url": "https://www.hotstar.com/in/sports/football/match-highlights/arsenal-vs-man-city",
            "stats": {
                "home_shots": 12,
                "away_shots": 8,
                "home_shots_on_target": 6,
                "away_shots_on_target": 4,
                "home_corners": 5,
                "away_corners": 3,
                "home_fouls": 10,
                "away_fouls": 8,
                "home_yellow_cards": 2,
                "away_yellow_cards": 1,
                "home_red_cards": 0,
                "away_red_cards": 0
            }
        },
        {
            "id": 2,
            "date": "2025-10-29T19:30:00Z",
            "homeTeam": "Liverpool FC",
            "awayTeam": "Tottenham Hotspur FC",
            "home_score": 3,
            "away_score": 2,
            "league": "Premier League",
            "matchday": 11,
            "home_team_crest": "https://crests.football-data.org/64.png",
            "away_team_crest": "https://crests.football-data.org/73.png",
            "highlights_url": "https://www.hotstar.com/in/sports/football/match-highlights/liverpool-vs-tottenham",
            "stats": {
                "home_shots": 15,
                "away_shots": 11,
                "home_shots_on_target": 7,
                "away_shots_on_target": 5,
                "home_corners": 6,
                "away_corners": 4,
                "home_fouls": 12,
                "away_fouls": 9,
                "home_yellow_cards": 1,
                "away_yellow_cards": 3,
                "home_red_cards": 0,
                "away_red_cards": 0
            }
        },
        {
            "id": 3,
            "date": "2025-10-26T16:30:00Z",
            "homeTeam": "Chelsea FC",
            "awayTeam": "Manchester United FC",
            "home_score": 1,
            "away_score": 1,
            "league": "Premier League",
            "matchday": 10,
            "home_team_crest": "https://crests.football-data.org/61.png",
            "away_team_crest": "https://crests.football-data.org/66.png",
            "highlights_url": "https://www.hotstar.com/in/sports/football/match-highlights/chelsea-vs-man-united",
            "stats": {
                "home_shots": 9,
                "away_shots": 7,
                "home_shots_on_target": 4,
                "away_shots_on_target": 3,
                "home_corners": 4,
                "away_corners": 5,
                "home_fouls": 11,
                "away_fouls": 13,
                "home_yellow_cards": 2,
                "away_yellow_cards": 2,
                "home_red_cards": 0,
                "away_red_cards": 1
            }
        },
        {
            "id": 4,
            "date": "2025-10-22T19:30:00Z",
            "homeTeam": "Newcastle",
            "awayTeam": "Aston Villa",
            "home_score": 2,
            "away_score": 0,
            "league": "Premier League",
            "matchday": 9,
            "home_team_crest": "https://crests.football-data.org/67.png",
            "away_team_crest": "https://crests.football-data.org/58.png",
            "highlights_url": "https://www.hotstar.com/in/sports/football/match-highlights/newcastle-vs-aston-villa",
            "stats": {
                "home_shots": 11,
                "away_shots": 6,
                "home_shots_on_target": 5,
                "away_shots_on_target": 2,
                "home_corners": 7,
                "away_corners": 2,
                "home_fouls": 8,
                "away_fouls": 14,
                "home_yellow_cards": 1,
                "away_yellow_cards": 3,
                "home_red_cards": 0,
                "away_red_cards": 0
            }
        }
    ]

def fetch_live_match_streams():
    """
    Fetch live match streaming information
    Returns a dictionary of streaming platforms for live matches
    """
    try:
        # Updated with current platform information and proper logos
        print("Fetching live match streams...")
        streams = {
            "platforms": [
                {
                    "name": "JioHotstar",
                    "url": "https://www.hotstar.com/in/sports/football",
                    "logo": "/platform_logos/jiohotstar.png"
                },
                {
                    "name": "SkySports",
                    "url": "https://www.skysports.com/premier-league",
                    "logo": "/platform_logos/skysports.png"
                },
                {
                    "name": "NBC Sports",
                    "url": "https://www.nbcsports.com/soccer/premier-league",
                    "logo": "/platform_logos/nbc_sports.png"
                }
            ]
        }
        print("Live match streams fetched successfully")
        return streams
    except Exception as e:
        print(f"Error fetching live match streams: {e}")
        # Return updated sample data if API fails
        return {
            "platforms": [
                {
                    "name": "JioHotstar",
                    "url": "https://www.hotstar.com/in/sports/football",
                    "logo": "/platform_logos/jiohotstar.png"
                },
                {
                    "name": "SkySports",
                    "url": "https://www.skysports.com/premier-league",
                    "logo": "/platform_logos/skysports.png"
                },
                {
                    "name": "NBC Sports",
                    "url": "https://www.nbcsports.com/soccer/premier-league",
                    "logo": "/platform_logos/nbc_sports.png"
                }
            ]
        }

def get_gemini_response(prompt, conversation_history=None, user_greeted=False):
    """Get response from Google Gemini API using the official SDK with enhanced real-time data and search capabilities"""
    try:
        # Fetch comprehensive real-time data based on the query content
        live_matches = []
        upcoming_matches = []
        epl_standings = []
        news_data = []
        
        # Determine what data to fetch based on the query
        prompt_lower = prompt.lower()
        
        # Always fetch basic data
        live_matches = fetch_live_matches()
        upcoming_matches = fetch_upcoming_matches()
        epl_standings = fetch_epl_standings()
        
        # Fetch additional data based on query keywords
        if any(keyword in prompt_lower for keyword in ['news', 'latest', 'update', 'transfer']):
            news_data = fetch_epl_news()
        
        # Create context with real-time data
        context_parts = []
        
        # Add current date and time in IST
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context_parts.append(f"Current Date and Time (IST): {current_datetime}")
        
        if live_matches:
            # Format live matches data for better readability
            live_matches_formatted = []
            for match in live_matches:
                live_matches_formatted.append(
                    f"{match['homeTeam']} vs {match['awayTeam']} - "
                    f"Score: {match['score']} - "
                    f"Minute: {match['minute']} - "
                    f"Competition: {match['competition']} - "
                    f"Date: {match['date']}"
                )
            context_parts.append(f"Live Matches:\n" + "\n".join(live_matches_formatted))
        else:
            context_parts.append("Live Matches: No live matches currently")
            
        if upcoming_matches:
            # Format upcoming matches data for better readability
            upcoming_matches_formatted = []
            for match in upcoming_matches:
                upcoming_matches_formatted.append(
                    f"{match['homeTeam']} vs {match['awayTeam']} - "
                    f"Competition: {match['competition']} - "
                    f"Date: {match['date']}"
                )
            context_parts.append(f"Upcoming Matches:\n" + "\n".join(upcoming_matches_formatted))
        else:
            context_parts.append("Upcoming Matches: No upcoming matches data available")
            
        if epl_standings:
            # Format standings data for better readability
            standings_formatted = []
            for team in epl_standings[:10]:  # Top 10 standings
                standings_formatted.append(
                    f"{team['position']}. {team['team']} - "
                    f"Played: {team['played']}, Won: {team['won']}, Drawn: {team['drawn']}, Lost: {team['lost']} - "
                    f"GF: {team['goals_for']}, GA: {team['goals_against']}, GD: {team['goal_difference']} - "
                    f"Points: {team['points']}"
                )
            context_parts.append(f"EPL Standings (Top 10):\n" + "\n".join(standings_formatted))
        else:
            context_parts.append("EPL Standings: No standings data available")
            
        if news_data:
            # Format news data for better readability
            news_formatted = []
            for article in news_data[:5]:  # Top 5 news items
                news_formatted.append(
                    f"Title: {article['title']}\n"
                    f"Description: {article['description']}\n"
                    f"Published: {article['publishedAt']}"
                )
            context_parts.append(f"Latest News:\n" + "\n\n".join(news_formatted))
        
        context = "\n\n".join(context_parts)
        
        # Build conversation history string if available
        history_context = ""
        if conversation_history:
            history_parts = []
            for i, (role, message) in enumerate(conversation_history):
                if role == "user":
                    history_parts.append(f"User: {message}")
                elif role == "assistant":
                    history_parts.append(f"Assistant: {message}")
            history_context = "\n".join(history_parts)
        
        # Create a more sophisticated prompt that can handle various topics with real-time data
        enhanced_prompt = f"""
        You are an AI assistant for ScoreSight, a football analytics platform. 
        You have access to real-time football data and can provide up-to-date information.
        
        Here is the current real-time football data:
        {context}
        
        Conversation History:
        {history_context}
        
        User question:
        {prompt}
        
        User greeted status: {'Yes' if user_greeted else 'No'}
        
        Instructions:
        1. If the question is about current football data (matches, standings, news), use the real-time data provided above.
        2. If the question is about predictions or analysis, use your football knowledge combined with the data.
        3. If the question is about general topics, provide a knowledgeable response.
        4. Always be accurate and mention when you're using real-time data.
        5. If asked about specific teams or players, provide the most current information available.
        6. For match predictions, consider current form, standings, and head-to-head data.
        7. If asked about the current date or time, use the Current Date and Time provided in the context above (in IST).
        8. Always provide helpful and concise responses.
        9. Format your responses professionally with clear headings, bullet points, and structured information when appropriate.
        10. Use ``code`` style for specific data values
        11. Organize information in clear sections
        12. For lists of data, present them in a structured format with clear labels.
        13. For numerical data, be precise and include units where appropriate.
        14. Reference the conversation history when relevant to provide context-aware responses.
        15. If a user asks a follow-up question, use the conversation history to understand the context.
        16. Only greet the user once per conversation. If the "User greeted status" is "Yes", do not greet again.
        17. If the "User greeted status" is "No", you may provide an initial greeting but only once.
        18. Always present match times in IST format as provided in the data.
        19. Include competition information when discussing matches.
        
        Provide a helpful, well-formatted, and professional response.
        """
        
        # Use getattr to avoid linter issues
        GenerativeModel = getattr(genai, 'GenerativeModel')
        # Initialize the model with a specific model name
        model = GenerativeModel('models/gemini-flash-latest')
        
        # Generate response
        response = model.generate_content(enhanced_prompt)
        
        if response.text:
            return response.text
        else:
            return "Sorry, I couldn't generate a response at the moment. Please try again later."
            
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, I encountered an error while processing your request."

def get_available_teams():
    """Get list of available teams, or return empty lists if models failed to load"""
    if models_loaded and home_team_encoder and away_team_encoder:
        return list(home_team_encoder.classes_), list(away_team_encoder.classes_)
    else:
        # Return sample teams if models failed to load
        sample_teams = [
            "Arsenal", "Man City", "Liverpool", "Chelsea",
            "Man United", "Tottenham", "Newcastle", "Aston Villa",
            "Brighton", "West Ham", "Crystal Palace", "Leicester",
            "Wolves", "Everton", "Leeds United", "Southampton"
        ]
        return sample_teams, sample_teams

# Routes for user authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login requests"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if credentials are valid
        if authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', 
                                 team_logos=team_logo_mapping,
                                 error="Invalid username or password")
    
    return render_template('login.html', team_logos=team_logo_mapping)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration requests"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        if password != confirm_password:
            return render_template('signup.html', 
                                 team_logos=team_logo_mapping,
                                 error="Passwords do not match")
        
        if len(password) < 6:
            return render_template('signup.html', 
                                 team_logos=team_logo_mapping,
                                 error="Password must be at least 6 characters long")
        
        # Try to register the user
        if register_user(username, email, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('signup.html', 
                                 team_logos=team_logo_mapping,
                                 error="Username already exists")
    
    return render_template('signup.html', team_logos=team_logo_mapping)

@app.route('/logout')
def logout():
    """Log out the current user"""
    session.pop('username', None)
    return redirect(url_for('index'))

# Main application routes
@app.route('/')
def index():
    """Main home page"""
    # Get list of teams for the dropdowns
    home_teams, away_teams = get_available_teams()
    
    # Fetch live data
    print("Fetching data for home page...")
    live_matches = fetch_live_matches()
    upcoming_matches = fetch_upcoming_matches()
    epl_standings = fetch_epl_standings()
    print(f"Live matches count: {len(live_matches)}")
    print(f"Upcoming matches count: {len(upcoming_matches)}")
    print(f"EPL standings count: {len(epl_standings)}")
    
    username = session.get('username')
    
    return render_template('home.html', 
                         home_teams=home_teams, 
                         away_teams=away_teams, 
                         team_logos=team_logo_mapping,
                         get_team_logo=get_team_logo,
                         username=username,
                         live_matches=live_matches,
                         upcoming_matches=upcoming_matches,
                         epl_standings=epl_standings)

@app.route('/prediction')
def prediction():
    """Prediction page"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get list of teams for the dropdowns
    home_teams, away_teams = get_available_teams()
    
    print("Team logos data being passed to template:", team_logo_mapping)
    
    return render_template('index.html', 
                         home_teams=home_teams, 
                         away_teams=away_teams, 
                         team_logos=team_logo_mapping,
                         username=session['username'])

@app.route('/live-schedule')
def live_schedule():
    """Live match schedule page"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Fetch all relevant data
    print("Fetching data for live schedule page...")
    live_matches = fetch_live_matches()
    upcoming_matches = fetch_upcoming_matches()
    previous_matches = fetch_previous_matches()
    live_streams = fetch_live_match_streams()
    epl_news = fetch_epl_news()
    
    print(f"Live matches: {len(live_matches)}")
    print(f"Upcoming matches: {len(upcoming_matches)}")
    print(f"Previous matches: {len(previous_matches)}")
    print(f"News articles: {len(epl_news)}")
    
    # Get list of teams for the dropdowns
    home_teams, away_teams = get_available_teams()
    
    return render_template('live_schedule.html', 
                         home_teams=home_teams, 
                         away_teams=away_teams,
                         team_logos=team_logo_mapping,
                         username=session['username'],
                         live_matches=live_matches,
                         upcoming_matches=upcoming_matches,
                         previous_matches=previous_matches,
                         live_streams=live_streams,
                         epl_news=epl_news)

@app.route('/ai-assistance')
def ai_assistance():
    """AI assistance page"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get list of teams for the dropdowns
    home_teams, away_teams = get_available_teams()
    
    # Check if genai is properly configured
    genai_configured = genai is not None
    
    return render_template('ai_assistance.html', 
                         home_teams=home_teams, 
                         away_teams=away_teams,
                         team_logos=team_logo_mapping,
                         username=session['username'],
                         genai_configured=genai_configured)

@app.route('/teams')
def teams():
    """API endpoint to get available teams"""
    if 'username' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    home_teams, away_teams = get_available_teams()
    
    return jsonify({
        "home_teams": home_teams,
        "away_teams": away_teams
    })

@app.route('/team_logos/<path:filename>')
def team_logos(filename):
    """Serve team logo images"""
    return send_from_directory('static/images/team_logos', filename)

@app.route('/platform_logos/<path:filename>')
def platform_logos(filename):
    """Serve platform logo images"""
    return send_from_directory('static/images/platform_logos', filename)

@app.route('/slideshow_images/<path:filename>')
def slideshow_images(filename):
    """Serve slideshow images"""
    return send_from_directory('static/images/slideshow_images', filename)

@app.route('/score_sight_logo2.png')
def score_sight_logo2():
    """Serve the ScoreSight logo2"""
    return send_from_directory('static/images', 'score_sight_logo2.png')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests from the frontend"""
    print("Prediction request received")
    print("Session data:", session)
    print("Request headers:", request.headers)
    
    if 'username' not in session:
        print("Authentication failed - no username in session")
        return jsonify({"error": "Authentication required"}), 401
    
    # Check if models are loaded
    if not models_loaded:
        return jsonify({"error": "Prediction models are not available"}), 500
    
    data = request.get_json()
    print("Request data:", data)
    
    # Get team names and match date
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    match_date = data.get('match_date')
    
    # Get all the match statistics
    hthg = float(data.get('HTHG', 0))
    htag = float(data.get('HTAG', 0))
    hs = float(data.get('HS', 5))
    as_ = float(data.get('AS', 5))
    hst = float(data.get('HST', 2))
    ast = float(data.get('AST', 2))
    hc = float(data.get('HC', 3))
    ac = float(data.get('AC', 3))
    hf = float(data.get('HF', 10))
    af = float(data.get('AF', 10))
    hy = float(data.get('HY', 1))
    ay = float(data.get('AY', 1))
    hr = float(data.get('HR', 0))
    ar = float(data.get('AR', 0))
    
    # Make sure both teams are selected
    if not home_team or not away_team:
        return jsonify({"error": "Both home and away teams are required"}), 400
    
    # Get our prediction
    result = predict_match_result(home_team, away_team, int(hthg), int(htag), int(hs), int(as_), int(hst), int(ast), 
                                 int(hc), int(ac), int(hf), int(af), int(hy), int(ay), int(hr), int(ar))
    
    print("Prediction result:", result)
    
    if "error" in result:
        return jsonify(result), 400
    
    # Convert result codes to readable text
    result_mapping = {
        'H': 'Home Win',
        'A': 'Away Win',
        'D': 'Draw'
    }
    
    # Get team logos for display
    home_logo = team_logo_mapping.get(home_team, '')
    away_logo = team_logo_mapping.get(away_team, '')
    
    # Prepare response data
    response = {
        "match_result": result_mapping[result["match_result"]],
        "predicted_score": result["predicted_score"],
        "fthg": result["predicted_FTHG"],
        "ftag": result["predicted_FTAG"],
        "home_logo": home_logo,
        "away_logo": away_logo,
        "match_date": match_date
    }
    
    return jsonify(response)

@app.route('/ai-chat', methods=['POST'])
def ai_chat():
    """Handle AI chat requests with conversation history"""
    try:
        user_message = ''
        conversation_history = []
        user_greeted = False
        
        if request.json is not None:
            user_message = request.json.get('message', '')
            conversation_history = request.json.get('history', [])
            user_greeted = request.json.get('greeted', False)
        
        # Limit conversation history to last 10 messages to prevent context overflow
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        response_text = get_gemini_response(user_message, conversation_history, user_greeted)
        return jsonify({'response': response_text})
    except Exception as e:
        print(f"Error in AI chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'response': 'Sorry, I encountered an error while processing your request.'}), 500

@app.route('/api/live-schedule-data')
def live_schedule_data():
    """API endpoint to fetch live schedule data"""
    try:
        # Fetch all relevant data
        live_matches = fetch_live_matches()
        upcoming_matches = fetch_upcoming_matches()
        previous_matches = fetch_previous_matches()
        live_streams = fetch_live_match_streams()
        epl_news = fetch_epl_news()
        
        return jsonify({
            'live_matches': live_matches,
            'upcoming_matches': upcoming_matches,
            'previous_matches': previous_matches,
            'live_streams': live_streams,
            'epl_news': epl_news
        })
    except Exception as e:
        print(f"Error fetching live schedule data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch data'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)