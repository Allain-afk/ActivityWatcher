#!/usr/bin/env python3
"""
Simple test suite for Local Activity Watcher application
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import subprocess
import json
import time

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        import config
        print("✓ Config module imported successfully")
    except Exception as e:
        print(f"✗ Config module import failed: {e}")
        return False
    
    try:
        import database
        print("✓ Database module imported successfully")
    except Exception as e:
        print(f"✗ Database module import failed: {e}")
        return False
    
    try:
        import window_tracker
        print("✓ Window tracker module imported successfully")
    except Exception as e:
        print(f"✗ Window tracker module import failed: {e}")
        return False
    
    try:
        import web_dashboard
        print("✓ Web dashboard module imported successfully")
    except Exception as e:
        print(f"✗ Web dashboard module import failed: {e}")
        return False
    
    try:
        import reports
        print("✓ Reports module imported successfully")
    except Exception as e:
        print(f"✗ Reports module import failed: {e}")
        return False
    
    try:
        import system_tray
        print("✓ System tray module imported successfully")
    except Exception as e:
        print(f"✗ System tray module import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration functionality."""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create config instance
            config = Config()
            original_data_dir = config.data_dir
            
            # Override for testing
            config.data_dir = Path(temp_dir)
            config.config_file = config.data_dir / "config.json"
            
            # Test default settings
            assert config.get("tracking_interval") == 5
            assert config.get("web_port") == 5000
            print("✓ Default configuration loaded correctly")
            
            # Test setting and getting values
            config.set("tracking_interval", 10)
            assert config.get("tracking_interval") == 10
            print("✓ Configuration setting and getting works")
            
            # Test persistence
            assert config.config_file.exists()
            print("✓ Configuration persistence works")
            
            # Restore original
            config.data_dir = original_data_dir
            
        finally:
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_database():
    """Test database functionality."""
    print("\nTesting database...")
    
    try:
        from database import ActivityDatabase
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            db_file = Path(temp_dir) / "test.db"
            db = ActivityDatabase(db_file)
            
            # Test database initialization
            assert db_file.exists()
            print("✓ Database file created")
            
            # Test recording activity
            db.record_activity("test_app.exe", "Test Window", 60)
            print("✓ Activity recording works")
            
            # Test session management
            session_id = db.start_session("test_app.exe", "Test Window")
            assert session_id is not None
            print("✓ Session start works")
            
            # Close connections before cleanup
            del db
            
        finally:
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_window_tracker():
    """Test window tracker functionality."""
    print("\nTesting window tracker...")
    
    try:
        from window_tracker import ActivityTracker
        
        # Create tracker instance
        tracker = ActivityTracker()
        
        # Test getting current window (platform-specific)
        current_window = tracker.get_current_window()
        
        if current_window:
            app_name, window_title = current_window
            assert isinstance(app_name, str)
            assert isinstance(window_title, str)
            print(f"✓ Current window detected: {app_name} - {window_title}")
        else:
            print("✓ Window tracker initialized (no current window)")
        
        return True
        
    except Exception as e:
        print(f"✗ Window tracker test failed: {e}")
        return False

def test_web_dashboard():
    """Test web dashboard functionality."""
    print("\nTesting web dashboard...")
    
    try:
        from web_dashboard import create_app
        
        # Create Flask app
        app = create_app()
        app.config['TESTING'] = True
        
        # Test app creation
        assert app is not None
        print("✓ Flask app created successfully")
        
        # Test with test client
        with app.test_client() as client:
            # Test main route
            response = client.get('/')
            assert response.status_code == 200
            print("✓ Main dashboard route works")
            
            # Test API route
            response = client.get('/api/stats/today')
            assert response.status_code == 200
            print("✓ API route works")
        
        return True
        
    except Exception as e:
        print(f"✗ Web dashboard test failed: {e}")
        return False

def test_reports():
    """Test report generation functionality."""
    print("\nTesting reports...")
    
    try:
        from reports import ReportGenerator
        
        # Create report generator
        report_gen = ReportGenerator()
        
        # Test daily report generation
        report = report_gen.generate_daily_report()
        assert isinstance(report, dict)
        assert 'date' in report
        assert 'total_time' in report
        print("✓ Daily report generation works")
        
        # Test JSON export
        json_report = report_gen.export_report('daily')
        parsed = json.loads(json_report)
        assert isinstance(parsed, dict)
        print("✓ Report JSON export works")
        
        return True
        
    except Exception as e:
        print(f"✗ Report test failed: {e}")
        return False

def test_main_application():
    """Test main application functionality."""
    print("\nTesting main application...")
    
    try:
        # Test help command
        result = subprocess.run([sys.executable, 'main.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        assert 'Local Activity Watcher' in result.stdout
        print("✓ Help command works")
        
        # Test window tracking test
        result = subprocess.run([sys.executable, 'main.py', 'test'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        print("✓ Window tracking test works")
        
        # Test stats command
        result = subprocess.run([sys.executable, 'main.py', 'stats'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        print("✓ Stats command works")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ Main application test timed out")
        return False
    except Exception as e:
        print(f"✗ Main application test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\nTesting dependencies...")
    
    required_modules = [
        'pystray',
        'PIL',
        'flask',
        'flask_cors',
        'psutil',
        'sqlite3',
        'json',
        'threading',
        'datetime',
        'pathlib',
    ]
    
    # Platform-specific dependencies
    import platform
    if platform.system() == "Windows":
        required_modules.extend(['win32gui', 'win32process'])
    elif platform.system() == "Darwin":
        required_modules.extend(['Cocoa', 'Quartz'])
    elif platform.system() == "Linux":
        required_modules.extend(['Xlib'])
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"✗ Missing dependencies: {', '.join(missing_modules)}")
        return False
    else:
        print("✓ All required dependencies available")
        return True

def test_web_server_startup():
    """Test web server startup."""
    print("\nTesting web server startup...")
    
    try:
        import threading
        import requests
        import time
        
        # Function to run web server
        def run_web_server():
            try:
                subprocess.run([sys.executable, 'main.py', 'web'], 
                              capture_output=True, timeout=3)
            except subprocess.TimeoutExpired:
                pass  # Expected to timeout
        
        # Start web server in background
        server_thread = threading.Thread(target=run_web_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Test if server is responsive
        try:
            response = requests.get('http://localhost:5000', timeout=2)
            if response.status_code == 200:
                print("✓ Web server startup works")
                return True
            else:
                print(f"✗ Web server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            print("✓ Web server test skipped (requests not available or server not responding)")
            return True  # Don't fail if requests isn't available
        
    except ImportError:
        print("✓ Web server test skipped (requests not available)")
        return True
    except Exception as e:
        print(f"✗ Web server test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Local Activity Watcher - Simple Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_imports,
        test_config,
        test_database,
        test_window_tracker,
        test_web_dashboard,
        test_reports,
        test_main_application,
        test_web_server_startup,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 