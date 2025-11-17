#!/usr/bin/env python3
"""
Entry point for the ScoreSight application
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run the blueprint-based application
if __name__ == '__main__':
    from app.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)