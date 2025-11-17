import json
import os
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model for ScoreSight application"""
    
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'username': self.username,
            'password_hash': self.password_hash
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        user = cls.__new__(cls)
        user.username = data['username']
        user.password_hash = data['password_hash']
        return user

class UserManager:
    """Manager for user operations"""
    
    USER_FILE = 'users.json'
    
    @staticmethod
    def load_users():
        """Load users from JSON file"""
        try:
            with open(UserManager.USER_FILE, 'r') as f:
                users_data = json.load(f)
                return {username: User.from_dict(data) for username, data in users_data.items()}
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    @staticmethod
    def save_users(users):
        """Save users to JSON file"""
        try:
            users_data = {username: user.to_dict() for username, user in users.items()}
            with open(UserManager.USER_FILE, 'w') as f:
                json.dump(users_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user"""
        users = UserManager.load_users()
        user = users.get(username)
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def register_user(username, password):
        """Register a new user"""
        users = UserManager.load_users()
        if username in users:
            return False
        user = User(username, password)
        users[username] = user
        return UserManager.save_users(users)