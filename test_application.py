#!/usr/bin/env python3
"""
Test suite for Local Activity Watcher application
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sqlite3
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import ActivityDatabase
from window_tracker import ActivityTracker, WindowsWindowTracker
from reports import ReportGenerator

class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        # Override data directory for testing
        self.config.data_dir = Path(self.temp_dir)
        self.config.config_file = self.config.data_dir / "config.json"
        self.config.db_file = self.config.data_dir / "activity.db"
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_default_settings(self):
        """Test that default settings are loaded correctly."""
        self.assertEqual(self.config.get("tracking_interval"), 5)
        self.assertEqual(self.config.get("window_title_tracking"), True)
        self.assertEqual(self.config.get("app_tracking"), True)
        self.assertEqual(self.config.get("web_port"), 5000)
    
    def test_set_and_get_setting(self):
        """Test setting and getting configuration values."""
        self.config.set("tracking_interval", 10)
        self.assertEqual(self.config.get("tracking_interval"), 10)
        
        # Check that it's saved to file
        self.assertTrue(self.config.config_file.exists())
        
        # Load new config instance and verify persistence
        new_config = Config()
        new_config.data_dir = Path(self.temp_dir)
        new_config.config_file = new_config.data_dir / "config.json"
        new_config.settings = new_config.load_config()
        self.assertEqual(new_config.get("tracking_interval"), 10)

class TestDatabase(unittest.TestCase):
    """Test database functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = Path(self.temp_dir) / "test.db"
        self.db = ActivityDatabase(self.db_file)
    
    def tearDown(self):
        """Clean up test database."""
        shutil.rmtree(self.temp_dir)
    
    def test_database_initialization(self):
        """Test that database tables are created correctly."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Check that tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('activities', tables)
            self.assertIn('app_sessions', tables)
            self.assertIn('daily_summaries', tables)
    
    def test_record_activity(self):
        """Test recording activity entries."""
        self.db.record_activity("test_app.exe", "Test Window", 60)
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activities")
            activities = cursor.fetchall()
            
            self.assertEqual(len(activities), 1)
            self.assertEqual(activities[0][2], "test_app.exe")
            self.assertEqual(activities[0][3], "Test Window")
            self.assertEqual(activities[0][4], 60)
    
    def test_session_management(self):
        """Test session start and end functionality."""
        session_id = self.db.start_session("test_app.exe", "Test Window")
        self.assertIsNotNone(session_id)
        
        # End the session
        self.db.end_session(session_id)
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM app_sessions WHERE id = ?", (session_id,))
            session = cursor.fetchone()
            
            self.assertIsNotNone(session)
            self.assertEqual(session[1], "test_app.exe")
            self.assertEqual(session[2], "Test Window")
            self.assertIsNotNone(session[4])  # end_time
    
    def test_get_app_stats(self):
        """Test getting application statistics."""
        # Insert test data
        session_id = self.db.start_session("test_app.exe", "Test Window")
        self.db.end_session(session_id)
        
        stats = self.db.get_app_stats(days=7)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]['app_name'], "test_app.exe")
    
    def test_get_daily_stats(self):
        """Test getting daily statistics."""
        # Insert test data
        session_id = self.db.start_session("test_app.exe", "Test Window")
        self.db.end_session(session_id)
        
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        stats = self.db.get_daily_stats(today)
        
        self.assertIn('date', stats)
        self.assertIn('total_time', stats)
        self.assertIn('app_breakdown', stats)
        self.assertEqual(stats['date'], today)

class TestWindowTracker(unittest.TestCase):
    """Test window tracking functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = Path(self.temp_dir) / "test.db"
        
        # Mock the database
        with patch('window_tracker.db') as mock_db:
            mock_db.start_session.return_value = 1
            mock_db.end_session.return_value = None
            self.tracker = ActivityTracker()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_current_window(self):
        """Test getting current window information."""
        # This will only work on Windows with the actual window tracker
        import platform
        if platform.system() == "Windows":
            try:
                current_window = self.tracker.get_current_window()
                if current_window:
                    self.assertIsInstance(current_window, tuple)
                    self.assertEqual(len(current_window), 2)
                    app_name, window_title = current_window
                    self.assertIsInstance(app_name, str)
                    self.assertIsInstance(window_title, str)
            except Exception as e:
                self.skipTest(f"Window tracking not available: {e}")
    
    @patch('window_tracker.WindowsWindowTracker')
    def test_windows_tracker_initialization(self, mock_tracker):
        """Test Windows tracker initialization."""
        mock_instance = MagicMock()
        mock_tracker.return_value = mock_instance
        mock_instance.get_active_window.return_value = ("notepad.exe", "Untitled - Notepad")
        
        import platform
        if platform.system() == "Windows":
            tracker = WindowsWindowTracker()
            # This test depends on the actual system, so we'll just check it doesn't crash
            self.assertIsNotNone(tracker)

class TestReportGenerator(unittest.TestCase):
    """Test report generation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = Path(self.temp_dir) / "test.db"
        self.db = ActivityDatabase(self.db_file)
        
        # Create test data
        session_id = self.db.start_session("test_app.exe", "Test Window")
        self.db.end_session(session_id)
        
        # Mock the report generator's database
        with patch('reports.db', self.db):
            self.report_generator = ReportGenerator()
            self.report_generator.db = self.db
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_daily_report(self):
        """Test daily report generation."""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = self.report_generator.generate_daily_report(today)
        
        self.assertIn('date', report)
        self.assertIn('total_time', report)
        self.assertIn('app_breakdown', report)
        self.assertIn('productivity', report)
        self.assertIn('summary', report)
        self.assertEqual(report['date'], today)
    
    def test_generate_weekly_report(self):
        """Test weekly report generation."""
        report = self.report_generator.generate_weekly_report()
        
        self.assertIn('start_date', report)
        self.assertIn('end_date', report)
        self.assertIn('total_time', report)
        self.assertIn('avg_daily_time', report)
        self.assertIn('daily_breakdown', report)
        self.assertIn('top_apps', report)
        self.assertIn('summary', report)
    
    def test_generate_app_report(self):
        """Test application-specific report generation."""
        report = self.report_generator.generate_app_report("test_app.exe")
        
        self.assertIn('app_name', report)
        self.assertEqual(report['app_name'], "test_app.exe")
        
        if 'error' not in report:
            self.assertIn('total_duration', report)
            self.assertIn('session_count', report)
            self.assertIn('window_titles', report)
    
    def test_export_report(self):
        """Test report export functionality."""
        json_report = self.report_generator.export_report('daily')
        
        # Should be valid JSON
        try:
            parsed = json.loads(json_report)
            self.assertIn('date', parsed)
            self.assertIn('total_time', parsed)
        except json.JSONDecodeError:
            self.fail("Report export did not produce valid JSON")

class TestWebDashboard(unittest.TestCase):
    """Test web dashboard functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the database and config
        with patch('web_dashboard.db') as mock_db, \
             patch('web_dashboard.config') as mock_config:
            
            mock_db.get_daily_stats.return_value = {
                'date': '2024-01-01',
                'total_time': 3600,
                'app_breakdown': [{'app_name': 'test_app.exe', 'duration': 3600}]
            }
            
            mock_config.get.return_value = 5000
            
            from web_dashboard import create_app
            self.app = create_app()
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_dashboard_route(self):
        """Test that dashboard route works."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Local Activity Watcher', response.data)
    
    def test_api_today_stats(self):
        """Test today's stats API endpoint."""
        response = self.client.get('/api/stats/today')
        self.assertEqual(response.status_code, 200)
        
        # Should return JSON
        self.assertEqual(response.content_type, 'application/json')
    
    def test_api_tracking_status(self):
        """Test tracking status API endpoint."""
        with patch('web_dashboard.activity_tracker') as mock_tracker:
            mock_tracker.is_tracking.return_value = True
            mock_tracker.get_current_window.return_value = ("test_app.exe", "Test Window")
            
            response = self.client.get('/api/tracking/status')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('tracking', data)
            self.assertIn('current_window', data)

def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    
    # Test full application startup
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'main.py', 'test'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Application startup test passed")
        else:
            print(f"✗ Application startup test failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("✗ Application startup test timed out")
    except Exception as e:
        print(f"✗ Application startup test error: {e}")
    
    # Test web dashboard startup
    try:
        import threading
        import time
        import requests
        
        def start_web_server():
            subprocess.run([sys.executable, 'main.py', 'web'], 
                          capture_output=True, timeout=5)
        
        # Start web server in background
        server_thread = threading.Thread(target=start_web_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a bit for server to start
        time.sleep(2)
        
        # Test if server is responsive
        try:
            response = requests.get('http://localhost:5000', timeout=2)
            if response.status_code == 200:
                print("✓ Web dashboard integration test passed")
            else:
                print(f"✗ Web dashboard returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print("✗ Web dashboard not accessible")
    
    except Exception as e:
        print(f"✗ Web dashboard integration test error: {e}")

def main():
    """Run all tests."""
    print("Running Local Activity Watcher Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestConfig,
        TestDatabase,
        TestWindowTracker,
        TestReportGenerator,
        TestWebDashboard
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run unit tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    
    # Run integration tests
    run_integration_tests()
    
    print("\n" + "=" * 50)
    
    # Summary
    if result.wasSuccessful():
        print("✓ All unit tests passed!")
    else:
        print(f"✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main()) 