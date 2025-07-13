#!/usr/bin/env python3
"""
Debug script to check database contents
"""

import sqlite3
from database import db
from datetime import datetime

def check_database():
    """Check database contents."""
    print("Checking database contents...")
    print(f"Database file: {db.db_path}")
    
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if database file exists and has tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables in database: {[t[0] for t in tables]}")
            
            # Check sessions count
            cursor.execute("SELECT COUNT(*) FROM app_sessions")
            session_count = cursor.fetchone()[0]
            print(f"Total sessions: {session_count}")
            
            # Check recent sessions
            cursor.execute("""
                SELECT app_name, window_title, start_time, end_time, duration 
                FROM app_sessions 
                ORDER BY start_time DESC LIMIT 5
            """)
            sessions = cursor.fetchall()
            
            print("\nRecent sessions:")
            if sessions:
                for session in sessions:
                    app_name, window_title, start_time, end_time, duration = session
                    print(f"  {app_name} - {window_title}")
                    print(f"    Start: {start_time}")
                    print(f"    End: {end_time}")
                    print(f"    Duration: {duration}s")
                    print()
            else:
                print("  No sessions found")
            
            # Check activities count
            cursor.execute("SELECT COUNT(*) FROM activities")
            activity_count = cursor.fetchone()[0]
            print(f"Total activities: {activity_count}")
            
            # Check recent activities
            cursor.execute("""
                SELECT app_name, window_title, timestamp, duration 
                FROM activities 
                ORDER BY timestamp DESC LIMIT 5
            """)
            activities = cursor.fetchall()
            
            print("\nRecent activities:")
            if activities:
                for activity in activities:
                    app_name, window_title, timestamp, duration = activity
                    print(f"  {app_name} - {window_title} - {timestamp} - {duration}s")
            else:
                print("  No activities found")
            
    except Exception as e:
        print(f"Error checking database: {e}")

def test_session_recording():
    """Test session recording manually."""
    print("\n" + "="*50)
    print("Testing session recording...")
    
    try:
        # Start a test session
        session_id = db.start_session("test_app.exe", "Test Window")
        print(f"Started session with ID: {session_id}")
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # End the session
        db.end_session(session_id)
        print("Ended session")
        
        # Check if it was recorded
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM app_sessions WHERE id = ?", (session_id,))
            session = cursor.fetchone()
            
            if session:
                print(f"Session recorded successfully: {session}")
                print(f"Duration: {session[5]}s")
            else:
                print("Session not found in database!")
                
    except Exception as e:
        print(f"Error testing session recording: {e}")

def check_tracking_status():
    """Check if tracking is actually running."""
    print("\n" + "="*50)
    print("Checking tracking status...")
    
    try:
        from window_tracker import activity_tracker
        
        print(f"Is tracking: {activity_tracker.is_tracking()}")
        print(f"Current session: {activity_tracker.current_session}")
        print(f"Last window info: {activity_tracker.last_window_info}")
        
        # Get current window
        current_window = activity_tracker.get_current_window()
        print(f"Current window: {current_window}")
        
    except Exception as e:
        print(f"Error checking tracking status: {e}")

if __name__ == "__main__":
    check_database()
    test_session_recording()
    check_tracking_status() 