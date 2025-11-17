#!/usr/bin/env python3
"""
Deployment script for ScoreSight application
"""

import os
import sys
import subprocess
import shutil

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import sklearn
        import requests
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def check_models():
    """Check if all model files exist"""
    model_files = [
        "match_winner_model.pkl",
        "fthg_model.pkl",
        "ftag_model.pkl",
        "home_team_encoder.pkl",
        "away_team_encoder.pkl"
    ]
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models")
    
    for model_file in model_files:
        model_path = os.path.join(model_dir, model_file)
        if not os.path.exists(model_path):
            print(f"✗ Missing model file: {model_file}")
            return False
        print(f"✓ Found model file: {model_file}")
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    
    if not os.path.exists(env_path):
        print("✗ .env file not found")
        return False
    
    required_vars = ["GOOGLE_API_KEY", "FOOTBALL_DATA_API_KEY", "RAPIDAPI_KEY"]
    
    with open(env_path, "r") as f:
        env_content = f.read()
    
    for var in required_vars:
        if var not in env_content:
            print(f"✗ Missing environment variable: {var}")
            return False
        print(f"✓ Found environment variable: {var}")
    
    return True

def main():
    """Main deployment function"""
    print("Checking ScoreSight deployment requirements...")
    print("=" * 50)
    
    # Change to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("✗ Dependency check failed")
        return False
    
    # Check models
    print("\nChecking model files...")
    if not check_models():
        print("✗ Model check failed")
        return False
    
    # Check environment file
    print("\nChecking environment file...")
    if not check_env_file():
        print("✗ Environment file check failed")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All deployment checks passed!")
    print("You can now run the application with: python run.py")
    return True

if __name__ == "__main__":
    main()