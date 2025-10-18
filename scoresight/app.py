import requests

# Your API configuration
API_TOKEN = "b839a17637ca4abc953080c5f3761314"
HEADERS = {"X-Auth-Token": API_TOKEN}
BASE_URL = "https://api.football-data.org/v4/"

def fetch_premier_league_fixtures():
    """Fetch Premier League fixtures for the 2025/26 season"""
    url = f"{BASE_URL}competitions/PL/matches?season=2025"
    
    try:
        print("🔄 Fetching Premier League fixtures...")
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            matches = data['matches']
            print(f"✅ Successfully retrieved {len(matches)} matches!")
            return matches
        else:
            print(f"❌ Error: API request failed with status {response.status_code}")
            print(f"Message: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

def display_fixtures(matches, limit=10):
    """Display fixtures in a nice format"""
    if not matches:
        print("No matches to display.")
        return
    
    print(f"\n📅 UPCOMING PREMIER LEAGUE FIXTURES (First {limit} matches)")
    print("=" * 60)
    
    for i, match in enumerate(matches[:limit], 1):
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        match_date = match['utcDate'][:10]  # Get just YYYY-MM-DD
        
        print(f"{i:2d}. {home_team:25} vs {away_team:25} | {match_date}")

# Main execution
if __name__ == "__main__":
    fixtures = fetch_premier_league_fixtures()
    if fixtures:
        display_fixtures(fixtures)