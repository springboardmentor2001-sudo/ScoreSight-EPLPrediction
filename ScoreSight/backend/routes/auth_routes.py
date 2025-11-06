from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token # type: ignore
from datetime import timedelta
import re

# Import from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import db, User

def init_auth_routes(app):
    
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @app.route('/api/signup', methods=['POST'])
    def signup():
        try:
            data = request.json
            
            # Validate required fields
            if not all(k in data for k in ['username', 'email', 'password']):
                return jsonify({'error': 'Missing required fields'}), 400
            
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if user already exists
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already registered'}), 409
            
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already taken'}), 409
            
            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email']
            )
            new_user.set_password(data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(
                identity=new_user.id,
                expires_delta=timedelta(days=7)
            )
            
            return jsonify({
                'access_token': access_token,
                'user': new_user.to_dict(),
                'message': 'Registration successful'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.json
            
            if not all(k in data for k in ['email', 'password']):
                return jsonify({'error': 'Email and password required'}), 400
            
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Create access token
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(days=7)
            )
            
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict(),
                'message': 'Login successful'
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({'user': user.to_dict()}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500