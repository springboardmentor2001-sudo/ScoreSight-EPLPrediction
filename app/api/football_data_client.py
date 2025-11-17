import requests
import os
from ..config import Config

class FootballDataClient:
    """Client for interacting with the football-data.org API"""
    
    def __init__(self):
        self.api_key = Config.FOOTBALL_DATA_API_KEY
        self.base_url = Config.FOOTBALL_DATA_API_BASE_URL
        self.headers = {
            'X-Response-Control': 'minified',
            'X-Response-Format': 'json',
            'X-Auth-Token': self.api_key
        }
    
    def get_standings(self, competition_id='PL'):
        """Get standings for a competition"""
        url = f"{self.base_url}/competitions/{competition_id}/standings"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None
    
    def get_matches(self, competition_id='2021', status=None):
        """Get matches for a competition"""
        url = f"{self.base_url}/matches"
        params = {'competitions': competition_id}
        if status:
            params['status'] = status
        response = requests.get(url, headers=self.headers, params=params)
        return response.json() if response.status_code == 200 else None
    
    def get_competition(self, competition_id='2021'):
        """Get competition details"""
        url = f"{self.base_url}/competitions/{competition_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None