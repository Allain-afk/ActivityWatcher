#!/usr/bin/env python3
"""
Quick API test
"""

import requests
import json

def test_api():
    """Test API endpoints."""
    base_url = "http://localhost:5002"
    
    try:
        # Test today stats
        print("Testing /api/stats/today...")
        response = requests.get(f"{base_url}/api/stats/today", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Total time: {data.get('total_time', 0)}s")
            print(f"  App breakdown: {len(data.get('app_breakdown', []))} apps")
            for app in data.get('app_breakdown', [])[:3]:
                print(f"    - {app['app_name']}: {app['duration']}s")
        else:
            print(f"✗ Failed: {response.status_code}")
            
        # Test tracking status
        print("\nTesting /api/tracking/status...")
        response = requests.get(f"{base_url}/api/tracking/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Tracking: {data.get('tracking', False)}")
            if data.get('current_window'):
                print(f"  Current window: {data['current_window']}")
        else:
            print(f"✗ Failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection failed: {e}")

if __name__ == "__main__":
    test_api() 