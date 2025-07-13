#!/usr/bin/env python3
"""
Run script for Local Activity Watcher

This script starts the application from the src package.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from src.main import main

if __name__ == "__main__":
    main() 