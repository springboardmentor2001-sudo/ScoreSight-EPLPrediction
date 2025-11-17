import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for ScoreSight application"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY') or 'score_sight_secret_key_2025'
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    # API Endpoints
    FOOTBALL_DATA_API_BASE_URL = 'https://api.football-data.org/v4'
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Session settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Model paths
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'models')
    
    # Static files
    STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    # Templates
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')