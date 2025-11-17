import http.client
import json
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to sys.path to handle relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Config instead of loading dotenv
from app.config import Config

# Use Config instead of environment variables directly
RAPIDAPI_KEY = Config.RAPIDAPI_KEY
RAPIDAPI_HOST = "english-premiere-league1.p.rapidapi.com"

def get_epl_data(endpoint: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch data from the English Premier League RapidAPI
    
    Args:
        endpoint (str): API endpoint to call (e.g., '/teams', '/standings')
        
    Returns:
        dict: JSON response from the API or None if error
    """
    try:
        conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': RAPIDAPI_HOST
        }
        
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        
        if res.status == 200:
            return json.loads(data.decode("utf-8"))
        else:
            print(f"API Error: Status {res.status}")
            return None
            
    except Exception as e:
        print(f"Error fetching data from RapidAPI: {e}")
        return None

def get_teams() -> Optional[Dict[Any, Any]]:
    """Get list of EPL teams"""
    # Try different possible endpoints
    endpoints = ["/teams", "/v1/teams", "/api/teams", "/epl/teams"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

def get_standings(year: Optional[str] = None) -> Optional[Dict[Any, Any]]:
    """Get current EPL standings"""
    if year is None:
        year = str(datetime.now().year)
    
    # Try different possible endpoints
    endpoints = [f"/standings?year={year}", "/table"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

def get_team_info(team_id: str) -> Optional[Dict[Any, Any]]:
    """Get detailed information for a specific team"""
    endpoints = [f"/teams/{team_id}", f"/v1/teams/{team_id}", f"/api/teams/{team_id}"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

def get_team_results(team_id: str) -> Optional[Dict[Any, Any]]:
    """Get recent results for a specific team"""
    endpoints = [f"/teams/{team_id}/results", f"/v1/teams/{team_id}/results"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

def get_team_performance(team_id: str) -> Optional[Dict[Any, Any]]:
    """Get performance statistics for a specific team"""
    endpoints = [f"/teams/{team_id}/performance", f"/v1/teams/{team_id}/performance"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

def get_scoring_stats() -> Optional[Dict[Any, Any]]:
    """Get scoring statistics"""
    endpoints = ["/stats/scoring", "/stats", "/v1/stats"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

def get_news() -> Optional[Dict[Any, Any]]:
    """Get latest EPL news"""
    return get_epl_data("/news")

def get_schedule(year: Optional[str] = None) -> Optional[Dict[Any, Any]]:
    """Get upcoming match schedule"""
    if year is None:
        year = str(datetime.now().year)
    
    endpoints = [f"/schedule?year={year}"]
    for endpoint in endpoints:
        result = get_epl_data(endpoint)
        if result:
            return result
    return None

# Test function to verify the API is working
def test_api():
    """Test the API connection and basic endpoints"""
    print("Testing RapidAPI connection...")
    
    # Test news endpoint
    news = get_news()
    if news:
        print("News endpoint: SUCCESS")
        print(f"News items: {len(news.get('news', [])) if isinstance(news, dict) else 'Unknown'}")
    else:
        print("News endpoint: FAILED")
    
    # Test standings endpoint
    standings = get_standings()
    if standings:
        print("Standings endpoint: SUCCESS")
        print(f"Teams in standings: {len(standings.get('standings', [])) if isinstance(standings, dict) else 'Unknown'}")
    else:
        print("Standings endpoint: FAILED")
    
    # Test schedule endpoint
    schedule = get_schedule()
    if schedule:
        print("Schedule endpoint: SUCCESS")
        print(f"Matches in schedule: {len(schedule.get('schedule', [])) if isinstance(schedule, dict) else 'Unknown'}")
    else:
        print("Schedule endpoint: FAILED")

if __name__ == "__main__":
    test_api()