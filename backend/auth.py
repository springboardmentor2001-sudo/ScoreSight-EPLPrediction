from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

router = APIRouter()
security = HTTPBearer()

# SIMPLIFIED Pydantic Models - Remove complex validation for now
class SignupRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    token: str
    created_at: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None

# Utility Functions (keep the same)
def load_users() -> List[Dict[str, Any]]:
    """Load users from JSON file with error handling"""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        try:
            os.rename(USERS_FILE, USERS_FILE + '.backup')
        except:
            pass
        return []
    except Exception as e:
        print(f"Error loading users: {e}")
        return []

def save_users(users: List[Dict[str, Any]]) -> bool:
    """Save users to JSON file with error handling"""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = uuid.uuid4().hex
    digest = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${digest}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        if not hashed or '$' not in hashed:
            return False
        salt, digest = hashed.split('$', 1)
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest() == digest
    except Exception:
        return False

def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Find user by email (case-insensitive)"""
    users = load_users()
    for u in users:
        if u.get('email', '').lower() == email.lower():
            return u
    return None

def find_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    """Find user by authentication token"""
    if not token:
        return None
    users = load_users()
    for u in users:
        if u.get('token') == token:
            return u
    return None

def create_token() -> str:
    """Create a new authentication token"""
    return uuid.uuid4().hex

def sanitize_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive data from user object"""
    return {
        'id': user.get('id'),
        'email': user.get('email'),
        'firstName': user.get('firstName', ''),
        'lastName': user.get('lastName', ''),
        'token': user.get('token'),
        'created_at': user.get('created_at')
    }

# API Routes
@router.post('/api/auth/signup', response_model=AuthResponse)
async def signup(payload: SignupRequest):
    """User registration endpoint"""
    try:
        print(f"🔐 Signup attempt for: {payload.email}")
        
        # Check if user already exists
        existing = find_user_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists'
            )

        users = load_users()
        
        # Create new user
        user_id = uuid.uuid4().hex
        hashed_password = hash_password(payload.password)
        token = create_token()
        
        user_data = {
            'id': user_id,
            'email': payload.email.lower(),
            'password': hashed_password,
            'firstName': payload.firstName or '',
            'lastName': payload.lastName or '',
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'token': token,
            'is_active': True
        }
        
        users.append(user_data)
        
        if not save_users(users):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to save user data'
            )

        # Return sanitized user data
        sanitized_user = sanitize_user_data(user_data)
        print(f"✅ User created: {payload.email}")
        
        return AuthResponse(
            success=True,
            message='User registered successfully',
            user=UserResponse(**sanitized_user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error during registration'
        )

@router.post('/api/auth/login', response_model=AuthResponse)
async def login(payload: LoginRequest):
    """User login endpoint"""
    try:
        print(f"🔐 Login attempt for: {payload.email}")
        
        user = find_user_by_email(payload.email)
        if not user:
            print(f"❌ User not found: {payload.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password'
            )

        if not user.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Account is deactivated'
            )

        if not verify_password(payload.password, user.get('password', '')):
            print(f"❌ Invalid password for: {payload.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password'
            )

        # Generate new token and update last login
        new_token = create_token()
        users = load_users()
        
        for u in users:
            if u.get('id') == user.get('id'):
                u['token'] = new_token
                u['last_login'] = datetime.utcnow().isoformat()
                break
        
        if not save_users(users):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to update user session'
            )

        # Update user object with new token
        user['token'] = new_token
        sanitized_user = sanitize_user_data(user)
        print(f"✅ Login successful: {payload.email}")
        
        return AuthResponse(
            success=True,
            message='Login successful',
            user=UserResponse(**sanitized_user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error during login'
        )

# Keep other endpoints the same...
@router.get('/api/auth/me', response_model=UserResponse)
async def get_current_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile (protected route)"""
    try:
        token = credentials.credentials
        user = find_user_by_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        sanitized_user = sanitize_user_data(user)
        return UserResponse(**sanitized_user)
    except Exception as e:
        print(f"Get user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to retrieve user profile'
        )

@router.get('/api/auth/check')
async def check_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Check if user is authenticated"""
    try:
        token = credentials.credentials
        user = find_user_by_token(token)
        if user:
            sanitized_user = sanitize_user_data(user)
            return {
                "authenticated": True,
                "user": UserResponse(**sanitized_user)
            }
        else:
            return {
                "authenticated": False,
                "user": None
            }
    except Exception:
        return {
            "authenticated": False,
            "user": None
        }

@router.get('/api/auth/health')
async def auth_health():
    """Health check for authentication service"""
    try:
        users = load_users()
        return {
            "status": "healthy",
            "users_count": len(users),
            "storage_file": USERS_FILE,
            "file_exists": os.path.exists(USERS_FILE)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unhealthy: {str(e)}"
        )