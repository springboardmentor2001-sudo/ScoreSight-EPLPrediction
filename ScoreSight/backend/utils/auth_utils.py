from flask import jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta

def create_auth_response(user):
    """Create authentication response with token"""
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(days=7)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(),
        'message': 'Login successful'
    }), 200

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None