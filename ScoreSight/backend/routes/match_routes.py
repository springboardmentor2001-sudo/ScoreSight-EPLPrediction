from flask import jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta

def init_match_routes(app, historical_data):
    
    @app.route('/api/matches', methods=['GET'])
    @jwt_required()
    def get_upcoming_matches():
        try:
            # Generate mock upcoming matches
            teams = [
                'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
                'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Ipswich Town',
                'Leicester City', 'Liverpool', 'Manchester City', 'Manchester United',
                'Newcastle United', 'Nottingham Forest', 'Southampton', 'Tottenham',
                'West Ham', 'Wolverhampton'
            ]
            
            upcoming_matches = []
            base_date = datetime.now() + timedelta(days=1)
            
            for i in range(5):
                match_date = base_date + timedelta(days=i*2)
                home_team = teams[i % len(teams)]
                away_team = teams[(i + 5) % len(teams)]
                
                if home_team != away_team:
                    upcoming_matches.append({
                        'id': i + 1,
                        'date': match_date.strftime('%Y-%m-%d'),
                        'time': '15:00',
                        'home_team': home_team,
                        'away_team': away_team,
                        'venue': f"{home_team} Stadium",
                        'competition': 'Premier League'
                    })
            
            return jsonify({'matches': upcoming_matches}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500