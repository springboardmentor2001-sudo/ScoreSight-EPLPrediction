import hashlib
import os
from datetime import datetime, timedelta

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a password against its hash"""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def get_team_logo(team_name, team_logo_mapping):
    """Get team logo filename with fuzzy matching"""
    # Direct match first
    if team_name in team_logo_mapping:
        return team_logo_mapping[team_name]
    
    # Try partial matching for common cases
    for key, value in team_logo_mapping.items():
        if key in team_name or team_name in key:
            return value
    
    # Return default if no match found
    return 'default.png'

def generate_sample_form_data():
    """Generate sample form data for teams"""
    import random
    form_results = ['W', 'D', 'L']
    return ','.join(random.choices(form_results, k=5))