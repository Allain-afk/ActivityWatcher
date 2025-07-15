"""
Enhanced Activity Monitor

This module provides improved activity data gathering including:
- Idle time detection
- Activity intensity tracking
- Enhanced window information
- Better browser tracking
"""

import time
import psutil
import platform
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from threading import Thread, Event, Lock
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ActivityMonitor(ABC):
    """Abstract base class for activity monitoring."""
    
    @abstractmethod
    def get_idle_time(self) -> int:
        """Get idle time in seconds."""
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        pass
    
    @abstractmethod
    def get_keyboard_activity(self) -> bool:
        """Check if keyboard activity detected recently."""
        pass

class WindowsActivityMonitor(ActivityMonitor):
    """Windows-specific activity monitor."""
    
    def __init__(self):
        self.available = False
        try:
            import win32api
            import win32gui
            from ctypes import Structure, windll, c_uint, sizeof, byref
            
            class LASTINPUTINFO(Structure):
                _fields_ = [
                    ('cbSize', c_uint),
                    ('dwTime', c_uint),
                ]
            
            self.win32api = win32api
            self.win32gui = win32gui
            self.windll = windll
            self.LASTINPUTINFO = LASTINPUTINFO
            self.available = True
        except ImportError:
            logger.warning("Windows activity monitoring not available")
    
    def get_idle_time(self) -> int:
        """Get idle time in seconds on Windows."""
        if not self.available:
            return 0
        
        try:
            lastInputInfo = self.LASTINPUTINFO()
            lastInputInfo.cbSize = sizeof(lastInputInfo)
            self.windll.user32.GetLastInputInfo(byref(lastInputInfo))
            
            millis = self.win32api.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0
        except Exception as e:
            logger.error(f"Error getting idle time on Windows: {e}")
            return 0
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position on Windows."""
        if not self.available:
            return (0, 0)
        
        try:
            import win32gui
            return win32gui.GetCursorPos()
        except Exception as e:
            logger.error(f"Error getting mouse position on Windows: {e}")
            return (0, 0)
    
    def get_keyboard_activity(self) -> bool:
        """Check keyboard activity on Windows."""
        # This is a simplified implementation
        # In a real scenario, you might want to use hooks or check specific keys
        return self.get_idle_time() < 1.0

class LinuxActivityMonitor(ActivityMonitor):
    """Linux-specific activity monitor."""
    
    def __init__(self):
        self.available = False
        try:
            from Xlib import display
            from Xlib.ext import record
            self.display = display
            self.record = record
            self.disp = None
            self.available = True
        except ImportError:
            logger.warning("Linux activity monitoring not available")
    
    def get_idle_time(self) -> int:
        """Get idle time in seconds on Linux."""
        if not self.available:
            return 0
        
        try:
            # Try to get idle time from X11 screensaver extension
            import subprocess
            result = subprocess.run(['xprintidle'], capture_output=True, text=True)
            if result.returncode == 0:
                return int(result.stdout.strip()) / 1000.0
        except Exception:
            pass
        
        # Fallback: check /proc/stat for rough estimate
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                idle_time = int(line.split()[4])
                return idle_time / 100.0  # Convert to seconds
        except Exception as e:
            logger.error(f"Error getting idle time on Linux: {e}")
            return 0
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position on Linux."""
        if not self.available:
            return (0, 0)
        
        try:
            if not self.disp:
                self.disp = self.display.Display()
            
            root = self.disp.screen().root
            pointer = root.query_pointer()
            return (pointer.root_x, pointer.root_y)
        except Exception as e:
            logger.error(f"Error getting mouse position on Linux: {e}")
            return (0, 0)
    
    def get_keyboard_activity(self) -> bool:
        """Check keyboard activity on Linux."""
        # Simplified implementation
        return self.get_idle_time() < 1.0

class MacOSActivityMonitor(ActivityMonitor):
    """macOS-specific activity monitor."""
    
    def __init__(self):
        self.available = False
        try:
            import Quartz
            self.Quartz = Quartz
            self.available = True
        except ImportError:
            logger.warning("macOS activity monitoring not available")
    
    def get_idle_time(self) -> int:
        """Get idle time in seconds on macOS."""
        if not self.available:
            return 0
        
        try:
            return self.Quartz.CGEventSourceSecondsSinceLastEventType(
                self.Quartz.kCGEventSourceStateCombinedSessionState,
                self.Quartz.kCGAnyInputEventType
            )
        except Exception as e:
            logger.error(f"Error getting idle time on macOS: {e}")
            return 0
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position on macOS."""
        if not self.available:
            return (0, 0)
        
        try:
            pos = self.Quartz.NSEvent.mouseLocation()
            return (int(pos.x), int(pos.y))
        except Exception as e:
            logger.error(f"Error getting mouse position on macOS: {e}")
            return (0, 0)
    
    def get_keyboard_activity(self) -> bool:
        """Check keyboard activity on macOS."""
        return self.get_idle_time() < 1.0

class EnhancedActivityTracker:
    """Enhanced activity tracker with improved data gathering."""
    
    def __init__(self):
        self.activity_monitor = self._get_platform_monitor()
        self.last_mouse_pos = (0, 0)
        self.mouse_movements = 0
        self.keyboard_events = 0
        self.activity_intensity = 0.0
        self.idle_threshold = 60  # seconds
        self.tracking_data = []
        self.data_lock = Lock()
        
        # Import database
        try:
            from database import db
            self.db = db
        except ImportError:
            from .database import db
            self.db = db
    
    def _get_platform_monitor(self) -> ActivityMonitor:
        """Get the appropriate activity monitor for the current platform."""
        system = platform.system()
        
        if system == "Windows":
            return WindowsActivityMonitor()
        elif system == "Darwin":
            return MacOSActivityMonitor()
        elif system == "Linux":
            return LinuxActivityMonitor()
        else:
            logger.error(f"Unsupported platform: {system}")
            return None
    
    def get_enhanced_window_info(self, app_name: str, window_title: str) -> Dict:
        """Get enhanced window information with additional context."""
        enhanced_info = {
            'app_name': app_name,
            'window_title': window_title,
            'url': None,
            'file_path': None,
            'category': self._categorize_activity(app_name, window_title),
            'productivity_score': self._calculate_productivity_score(app_name, window_title)
        }
        
        # Extract URLs for browsers
        if self._is_browser(app_name):
            enhanced_info['url'] = self._extract_url_from_title(window_title)
        
        # Extract file paths for editors
        if self._is_editor(app_name):
            enhanced_info['file_path'] = self._extract_file_path(window_title)
        
        return enhanced_info
    
    def _is_browser(self, app_name: str) -> bool:
        """Check if the application is a web browser."""
        browsers = [
            'chrome', 'firefox', 'safari', 'edge', 'opera', 'brave',
            'chromium', 'vivaldi', 'chrome.exe', 'firefox.exe', 'msedge.exe'
        ]
        return any(browser in app_name.lower() for browser in browsers)
    
    def _is_editor(self, app_name: str) -> bool:
        """Check if the application is a code editor or text editor."""
        editors = [
            'code', 'atom', 'sublime', 'notepad', 'vim', 'emacs',
            'vscode', 'pycharm', 'intellij', 'eclipse', 'visualstudio'
        ]
        return any(editor in app_name.lower() for editor in editors)
    
    def _extract_url_from_title(self, window_title: str) -> Optional[str]:
        """Extract URL from browser window title."""
        # Simple heuristic - look for common URL patterns
        import re
        url_pattern = r'https?://[^\s\)]+|www\.[^\s\)]+'
        matches = re.findall(url_pattern, window_title)
        return matches[0] if matches else None
    
    def _extract_file_path(self, window_title: str) -> Optional[str]:
        """Extract file path from editor window title."""
        # Look for file path patterns
        import re
        # Match paths like /path/to/file.ext or C:\path\to\file.ext
        path_patterns = [
            r'[A-Za-z]:\\[^<>:"|?*\n]+',  # Windows paths
            r'/[^<>:"|?*\n]+',             # Unix paths
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, window_title)
            if matches:
                return matches[0]
        return None
    
    def _categorize_activity(self, app_name: str, window_title: str) -> str:
        """Categorize the activity based on app and window title."""
        app_lower = app_name.lower()
        title_lower = window_title.lower()
        
        # Work/Development
        if any(word in app_lower for word in ['code', 'ide', 'terminal', 'cmd', 'powershell']):
            return 'development'
        
        # Communication
        if any(word in app_lower for word in ['slack', 'teams', 'discord', 'zoom', 'skype']):
            return 'communication'
        
        # Entertainment
        if any(word in app_lower for word in ['spotify', 'netflix', 'youtube', 'steam', 'game']):
            return 'entertainment'
        
        # Productivity
        if any(word in app_lower for word in ['excel', 'word', 'powerpoint', 'notion', 'obsidian']):
            return 'productivity'
        
        # Web browsing needs more context
        if self._is_browser(app_name):
            if any(word in title_lower for word in ['github', 'stackoverflow', 'documentation']):
                return 'development'
            elif any(word in title_lower for word in ['youtube', 'netflix', 'twitch']):
                return 'entertainment'
            else:
                return 'web_browsing'
        
        return 'other'
    
    def _calculate_productivity_score(self, app_name: str, window_title: str) -> float:
        """Calculate a productivity score for the activity."""
        category = self._categorize_activity(app_name, window_title)
        
        productivity_scores = {
            'development': 0.9,
            'productivity': 0.8,
            'communication': 0.6,
            'web_browsing': 0.4,
            'entertainment': 0.1,
            'other': 0.5
        }
        
        return productivity_scores.get(category, 0.5)
    
    def get_activity_intensity(self) -> float:
        """Calculate current activity intensity based on mouse/keyboard activity."""
        if not self.activity_monitor:
            return 0.0
        
        # Get current mouse position
        current_pos = self.activity_monitor.get_mouse_position()
        
        # Calculate mouse movement
        if self.last_mouse_pos != current_pos:
            self.mouse_movements += 1
            self.last_mouse_pos = current_pos
        
        # Check keyboard activity
        if self.activity_monitor.get_keyboard_activity():
            self.keyboard_events += 1
        
        # Calculate intensity (normalized between 0 and 1)
        intensity = min(1.0, (self.mouse_movements + self.keyboard_events * 2) / 10.0)
        
        # Reset counters periodically
        if self.mouse_movements > 100 or self.keyboard_events > 50:
            self.mouse_movements = 0
            self.keyboard_events = 0
        
        return intensity
    
    def is_user_idle(self) -> bool:
        """Check if user is currently idle."""
        if not self.activity_monitor:
            return False
        
        idle_time = self.activity_monitor.get_idle_time()
        return idle_time > self.idle_threshold
    
    def get_system_usage(self, app_name: str) -> Dict:
        """Get system resource usage for an application."""
        try:
            # Find processes by name
            processes = [p for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
                        if app_name.lower() in p.info['name'].lower()]
            
            if not processes:
                return {'cpu_percent': 0, 'memory_percent': 0}
            
            # Sum up resources for all processes with this name
            total_cpu = sum(p.info['cpu_percent'] or 0 for p in processes)
            total_memory = sum(p.info['memory_percent'] or 0 for p in processes)
            
            return {
                'cpu_percent': total_cpu,
                'memory_percent': total_memory,
                'process_count': len(processes)
            }
        except Exception as e:
            logger.error(f"Error getting system usage: {e}")
            return {'cpu_percent': 0, 'memory_percent': 0}
    
    def record_enhanced_activity(self, app_name: str, window_title: str, duration: int = 0):
        """Record enhanced activity data."""
        enhanced_info = self.get_enhanced_window_info(app_name, window_title)
        system_usage = self.get_system_usage(app_name)
        
        activity_data = {
            'timestamp': datetime.now(),
            'app_name': app_name,
            'window_title': window_title,
            'duration': duration,
            'url': enhanced_info.get('url'),
            'file_path': enhanced_info.get('file_path'),
            'category': enhanced_info.get('category'),
            'productivity_score': enhanced_info.get('productivity_score'),
            'activity_intensity': self.get_activity_intensity(),
            'is_idle': self.is_user_idle(),
            'cpu_percent': system_usage.get('cpu_percent', 0),
            'memory_percent': system_usage.get('memory_percent', 0),
            'idle_time': self.activity_monitor.get_idle_time() if self.activity_monitor else 0
        }
        
        with self.data_lock:
            self.tracking_data.append(activity_data)
        
        # Store in database (extend the existing database schema)
        try:
            self.db.record_enhanced_activity(activity_data)
        except Exception as e:
            logger.error(f"Error recording enhanced activity: {e}")
            # Fallback to basic recording
            self.db.record_activity(app_name, window_title, duration)
    
    def get_productivity_stats(self, days: int = 7) -> Dict:
        """Get productivity statistics."""
        try:
            # This would require extending the database schema
            # For now, return basic stats
            return {
                'average_productivity': 0.5,
                'total_active_time': 0,
                'category_breakdown': {},
                'idle_time_percentage': 0
            }
        except Exception as e:
            logger.error(f"Error getting productivity stats: {e}")
            return {}

# Global enhanced activity tracker instance
enhanced_activity_tracker = EnhancedActivityTracker()