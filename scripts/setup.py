#!/usr/bin/env python3
"""
Setup script for ScoreSight application
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/raw",
        "data/processed",
        "data/models",
        "static/css",
        "static/js",
        "static/images/team_logos",
        "static/images/slideshow_images",
        "static/images/platform_logos",
        "tests",
        "docs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Main setup function"""
    print("Setting up ScoreSight application...")
    
    # Change to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Install requirements
    print("Installing requirements...")
    if not install_requirements():
        print("Failed to install requirements. Please install manually.")
        return False
    
    # Setup directories
    print("Setting up directories...")
    setup_directories()
    
    print("Setup completed successfully!")
    return True

if __name__ == "__main__":
    main()