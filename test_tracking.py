#!/usr/bin/env python3
"""
Test script to manually test tracking functionality
"""

import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from window_tracker import activity_tracker
from config import config

def test_manual_tracking():
    """Test tracking manually."""
    print("Testing manual tracking...")
    
    print(f"Initial tracking status: {activity_tracker.is_tracking()}")
    print(f"Initial thread: {activity_tracker.thread}")
    print(f"Initial tracking enabled: {activity_tracker.tracking_enabled}")
    
    # Test current window detection
    current_window = activity_tracker.get_current_window()
    print(f"Current window: {current_window}")
    
    # Start tracking
    print("\nStarting tracking...")
    try:
        activity_tracker.start_tracking(interval=3)
        print("Tracking started successfully")
    except Exception as e:
        print(f"Error starting tracking: {e}")
        return
    
    # Check status after starting
    print(f"After start - tracking status: {activity_tracker.is_tracking()}")
    print(f"After start - thread: {activity_tracker.thread}")
    print(f"After start - thread alive: {activity_tracker.thread.is_alive() if activity_tracker.thread else 'None'}")
    print(f"After start - tracking enabled: {activity_tracker.tracking_enabled}")
    
    # Monitor for a few seconds
    print("\nMonitoring for 10 seconds...")
    for i in range(10):
        print(f"  {i+1}/10 - Status: {activity_tracker.is_tracking()}, Current session: {activity_tracker.current_session}")
        time.sleep(1)
    
    # Check database for any new sessions
    print("\nChecking database for new sessions...")
    try:
        from database import db
        import sqlite3
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM app_sessions WHERE start_time > datetime('now', '-1 minute')")
            recent_sessions = cursor.fetchone()[0]
            print(f"Recent sessions (last minute): {recent_sessions}")
            
            if recent_sessions > 0:
                cursor.execute("""
                    SELECT app_name, window_title, start_time, end_time, duration 
                    FROM app_sessions 
                    WHERE start_time > datetime('now', '-1 minute')
                    ORDER BY start_time DESC
                """)
                sessions = cursor.fetchall()
                print("Recent sessions:")
                for session in sessions:
                    print(f"  {session[0]} - {session[1]} - {session[4]}s")
    except Exception as e:
        print(f"Error checking database: {e}")
    
    # Stop tracking
    print("\nStopping tracking...")
    activity_tracker.stop_tracking()
    print(f"After stop - tracking status: {activity_tracker.is_tracking()}")

def test_system_tray_integration():
    """Test system tray integration."""
    print("\n" + "="*50)
    print("Testing system tray integration...")
    
    try:
        from system_tray import SystemTrayApp
        
        # Create system tray app (but don't run it)
        print("Creating SystemTrayApp...")
        app = SystemTrayApp()
        
        print(f"System tray tracking enabled: {app.tracking_enabled}")
        print(f"Activity tracker status: {activity_tracker.is_tracking()}")
        
        # Check if tracking was started
        if activity_tracker.is_tracking():
            print("✓ Tracking was started by SystemTrayApp")
        else:
            print("✗ Tracking was NOT started by SystemTrayApp")
            
            # Try to start it manually
            print("Attempting to start tracking manually...")
            app.start_tracking()
            print(f"After manual start: {activity_tracker.is_tracking()}")
        
    except Exception as e:
        print(f"Error testing system tray integration: {e}")

if __name__ == "__main__":
    test_manual_tracking()
    test_system_tray_integration() 