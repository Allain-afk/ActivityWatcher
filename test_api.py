#!/usr/bin/env python3
"""
Test script to check web dashboard API endpoints
"""

import requests
import json
import time
import threading
import subprocess
import sys
import os

def start_web_server():
    """Start web server in background."""
    try:
        subprocess.run([sys.executable, 'main.py', 'web', '--port', '5002'], 
                      capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        pass  # Expected to timeout

def test_api_endpoints():
    """Test API endpoints."""
    base_url = "http://localhost:5002"
    
    # Start web server
    server_thread = threading.Thread(target=start_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    print("Starting web server...")
    time.sleep(3)
    
    # Test endpoints
    endpoints = [
        '/api/stats/today',
        '/api/stats/weekly',
        '/api/apps/top',
        '/api/tracking/status',
        '/api/config'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"  Data: {json.dumps(data, indent=2)}")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
    
    # Test the main dashboard page
    try:
        print(f"\nTesting main dashboard page...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print(f"✓ Dashboard page loads successfully")
            # Check if it contains key elements
            if 'Local Activity Watcher' in response.text:
                print("✓ Dashboard contains expected title")
            if 'today-time' in response.text:
                print("✓ Dashboard contains time display element")
        else:
            print(f"✗ Dashboard failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Dashboard request failed: {e}")

if __name__ == "__main__":
    test_api_endpoints() 