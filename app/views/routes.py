def fetch_previous_matches():
    """Fetch previous matches - using football-data.org API with fallback to sample data"""
    try:
        from app.api.football_data_client import FootballDataClient
        from datetime import datetime, timedelta
        import calendar
        import requests
        
        # Check if API key is configured
        client = FootballDataClient()
        if not client.api_key or client.api_key == 'your_api_key_here':
            print("Football-data.org API key not configured, returning sample data")
            # Return more sample previous matches data with proper stats structure
            sample_matches = [
                {
                    'date': '2025-11-07T20:00:00Z',
                    'homeTeam': 'Arsenal',
                    'awayTeam': 'Liverpool',
                    'home_score': 2,
                    'away_score': 1,
                    'status': 'FINISHED',
                    'matchday': 12,
                    'league': 'Premier League',
                    'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                    'stats': {
                        'home_shots': 12,
                        'away_shots': 8,
                        'home_shots_on_target': 5,
                        'away_shots_on_target': 3,
                        'home_corners': 6,
                        'away_corners': 4,
                        'home_fouls': 10,
                        'away_fouls': 8,
                        'home_yellow_cards': 2,
                        'away_yellow_cards': 1,
                        'home_red_cards': 0,
                        'away_red_cards': 0
                    }
                },
                {
                    'date': '2025-11-06T17:30:00Z',
                    'homeTeam': 'Man City',
                    'awayTeam': 'Chelsea',
                    'home_score': 3,
                    'away_score': 0,
                    'status': 'FINISHED',
                    'matchday': 12,
                    'league': 'Premier League',
                    'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                    'stats': {
                        'home_shots': 15,
                        'away_shots': 6,
                        'home_shots_on_target': 8,
                        'away_shots_on_target': 2,
                        'home_corners': 7,
                        'away_corners': 3,
                        'home_fouls': 8,
                        'away_fouls': 12,
                        'home_yellow_cards': 1,
                        'away_yellow_cards': 2,
                        'home_red_cards': 0,
                        'away_red_cards': 0
                    }
                },
                {
                    'date': '2025-11-05T15:00:00Z',
                    'homeTeam': 'Tottenham',
                    'awayTeam': 'Man United',
                    'home_score': 1,
                    'away_score': 2,
                    'status': 'FINISHED',
                    'matchday': 11,
                    'league': 'Premier League',
                    'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                    'stats': {
                        'home_shots': 10,
                        'away_shots': 11,
                        'home_shots_on_target': 4,
                        'away_shots_on_target': 5,
                        'home_corners': 5,
                        'away_corners': 6,
                        'home_fouls': 11,
                        'away_fouls': 9,
                        'home_yellow_cards': 2,
                        'away_yellow_cards': 3,
                        'home_red_cards': 0,
                        'away_red_cards': 1
                    }
                },
                {
                    'date': '2025-11-04T19:45:00Z',
                    'homeTeam': 'Newcastle',
                    'awayTeam': 'Brighton',
                    'home_score': 2,
                    'away_score': 2,
                    'status': 'FINISHED',
                    'matchday': 11,
                    'league': 'Premier League',
                    'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                    'stats': {
                        'home_shots': 9,
                        'away_shots': 9,
                        'home_shots_on_target': 4,
                        'away_shots_on_target': 4,
                        'home_corners': 4,
                        'away_corners': 5,
                        'home_fouls': 12,
                        'away_fouls': 10,
                        'home_yellow_cards': 3,
                        'away_yellow_cards': 2,
                        'home_red_cards': 0,
                        'away_red_cards': 0
                    }
                },
                {
                    'date': '2025-11-03T20:00:00Z',
                    'homeTeam': 'West Ham',
                    'awayTeam': 'Aston Villa',
                    'home_score': 0,
                    'away_score': 1,
                    'status': 'FINISHED',
                    'matchday': 11,
                    'league': 'Premier League',
                    'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                    'stats': {
                        'home_shots': 7,
                        'away_shots': 10,
                        'home_shots_on_target': 2,
                        'away_shots_on_target': 5,
                        'home_corners': 3,
                        'away_corners': 6,
                        'home_fouls': 14,
                        'away_fouls': 8,
                        'home_yellow_cards': 4,
                        'away_yellow_cards': 1,
                        'home_red_cards': 1,
                        'away_red_cards': 0
                    }
                },
                {
                    'date': '2025-11-02T16:30:00Z',
                    'homeTeam': 'Liverpool',
                    'awayTeam': 'Brentford',
                    'home_score': 3,
                    'away_score': 1,
                    'status': 'FINISHED',
                    'matchday': 10,
                    'league': 'Premier League',
                    'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                    'stats': {
                        'home_shots': 14,
                        'away_shots': 7,
                        'home_shots_on_target': 7,
                        'away_shots_on_target': 3,
                        'home_corners': 8,
                        'away_corners': 2,
                        'home_fouls': 9,
                        'away_fouls': 11,
                        'home_yellow_cards': 1,
                        'away_yellow_cards': 2,
                        'home_red_cards': 0,
                        'away_red_cards': 0
                    }
                }
            ]
            return sample_matches
        
        # Get current date and calculate date range for this month
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = now.replace(day=calendar.monthrange(now.year, now.month)[1], hour=23, minute=59, second=59, microsecond=999999)
        
        # Format dates for API
        date_from = start_of_month.strftime('%Y-%m-%d')
        date_to = end_of_month.strftime('%Y-%m-%d')
        
        # Get previous matches (FINISHED status) for this month
        # Using the matches endpoint with date filters
        import requests
        url = f"{client.base_url}/matches"
        params = {
            'competitions': 'PL',  # Premier League
            'status': 'FINISHED',
            'dateFrom': date_from,
            'dateTo': date_to
        }
        
        response = requests.get(url, headers=client.headers, params=params)
        data = response.json() if response.status_code == 200 else None
        
        if data and isinstance(data, dict):
            matches = []
            # Extract matches from the data
            if 'matches' in data and isinstance(data['matches'], list):
                # Sort matches by date (newest first)
                sorted_matches = sorted(data['matches'], key=lambda x: x.get('utcDate', ''), reverse=True)
                
                for match in sorted_matches[:20]:  # Increase limit to 20 matches for better coverage
                    # Extract team information
                    home_team = match.get('homeTeam', {}).get('name', 'Home Team')
                    away_team = match.get('awayTeam', {}).get('name', 'Away Team')
                    
                    # Get scores
                    score = match.get('score', {})
                    home_score = score.get('fullTime', {}).get('home', 0) or 0
                    away_score = score.get('fullTime', {}).get('away', 0) or 0
                    
                    # Get match details
                    matchday = match.get('matchday', 'N/A')
                    league = 'Premier League'
                    match_date = match.get('utcDate', '')
                    
                    # Format the match data to match our expected structure
                    formatted_match = {
                        'date': match_date,
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'home_score': home_score,
                        'away_score': away_score,
                        'status': match.get('status', 'FINISHED'),
                        'matchday': matchday,
                        'league': league,
                        'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',  # Add highlights URL
                        'stats': {
                            'home_shots': 10,  # Sample data - would need real API data
                            'away_shots': 8,   # Sample data - would need real API data
                            'home_shots_on_target': 5,  # Sample data - would need real API data
                            'away_shots_on_target': 3,  # Sample data - would need real API data
                            'home_corners': 6,  # Sample data - would need real API data
                            'away_corners': 4,   # Sample data - would need real API data
                            'home_fouls': 10,   # Sample data - would need real API data
                            'away_fouls': 8,    # Sample data - would need real API data
                            'home_yellow_cards': 2,  # Sample data - would need real API data
                            'away_yellow_cards': 1,  # Sample data - would need real API data
                            'home_red_cards': 0,     # Sample data - would need real API data
                            'away_red_cards': 0      # Sample data - would need real API data
                        }
                    }
                    matches.append(formatted_match)
            return matches
        
        return []
    except Exception as e:
        print(f"Exception in fetch_previous_matches: {e}")
        import traceback
        traceback.print_exc()
        # Return more sample data in case of error
        sample_matches = [
            {
                'date': '2025-11-07T20:00:00Z',
                'homeTeam': 'Arsenal',
                'awayTeam': 'Liverpool',
                'home_score': 2,
                'away_score': 1,
                'status': 'FINISHED',
                'matchday': 12,
                'league': 'Premier League',
                'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                'stats': {
                    'home_shots': 12,
                    'away_shots': 8,
                    'home_shots_on_target': 5,
                    'away_shots_on_target': 3,
                    'home_corners': 6,
                    'away_corners': 4,
                    'home_fouls': 10,
                    'away_fouls': 8,
                    'home_yellow_cards': 2,
                    'away_yellow_cards': 1,
                    'home_red_cards': 0,
                    'away_red_cards': 0
                }
            },
            {
                'date': '2025-11-06T17:30:00Z',
                'homeTeam': 'Man City',
                'awayTeam': 'Chelsea',
                'home_score': 3,
                'away_score': 0,
                'status': 'FINISHED',
                'matchday': 12,
                'league': 'Premier League',
                'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                'stats': {
                    'home_shots': 15,
                    'away_shots': 6,
                    'home_shots_on_target': 8,
                    'away_shots_on_target': 2,
                    'home_corners': 7,
                    'away_corners': 3,
                    'home_fouls': 8,
                    'away_fouls': 12,
                    'home_yellow_cards': 1,
                    'away_yellow_cards': 2,
                    'home_red_cards': 0,
                    'away_red_cards': 0
                }
            },
            {
                'date': '2025-11-05T15:00:00Z',
                'homeTeam': 'Tottenham',
                'awayTeam': 'Man United',
                'home_score': 1,
                'away_score': 2,
                'status': 'FINISHED',
                'matchday': 11,
                'league': 'Premier League',
                'highlights_url': 'https://www.jiocinema.com/sports/epl-highlights',
                'stats': {
                    'home_shots': 10,
                    'away_shots': 11,
                    'home_shots_on_target': 4,
                    'away_shots_on_target': 5,
                    'home_corners': 5,
                    'away_corners': 6,
                    'home_fouls': 11,
                    'away_fouls': 9,
                    'home_yellow_cards': 2,
                    'away_yellow_cards': 3,
                    'home_red_cards': 0,
                    'away_red_cards': 1
                }
            }
        ]
        return sample_matches