import sys
import time
import platform
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from threading import Thread, Event
from abc import ABC, abstractmethod

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowTracker(ABC):
    """Abstract base class for window tracking."""
    
    @abstractmethod
    def get_active_window(self) -> Optional[Tuple[str, str]]:
        """Get the active window information.
        
        Returns:
            Tuple of (app_name, window_title) or None if unable to get info
        """
        pass

class WindowsWindowTracker(WindowTracker):
    """Windows-specific window tracker using pywin32."""
    
    def __init__(self):
        try:
            import win32gui
            import win32process
            import psutil
            self.win32gui = win32gui
            self.win32process = win32process
            self.psutil = psutil
            self.available = True
        except ImportError:
            logger.error("pywin32 or psutil not available for Windows")
            self.available = False
    
    def get_active_window(self) -> Optional[Tuple[str, str]]:
        """Get active window on Windows."""
        if not self.available:
            return None
        
        try:
            # Get the foreground window
            hwnd = self.win32gui.GetForegroundWindow()
            if hwnd == 0:
                return None
            
            # Get window title
            window_title = self.win32gui.GetWindowText(hwnd)
            if not window_title:
                return None
            
            # Get process ID
            _, pid = self.win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = self.psutil.Process(pid)
                app_name = process.name()
            except (self.psutil.NoSuchProcess, self.psutil.AccessDenied):
                app_name = "Unknown"
            
            return (app_name, window_title)
        
        except Exception as e:
            logger.error(f"Error getting active window on Windows: {e}")
            return None

class MacOSWindowTracker(WindowTracker):
    """macOS-specific window tracker using pyobjc."""
    
    def __init__(self):
        try:
            from Cocoa import NSWorkspace
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            self.NSWorkspace = NSWorkspace
            self.CGWindowListCopyWindowInfo = CGWindowListCopyWindowInfo
            self.kCGWindowListOptionOnScreenOnly = kCGWindowListOptionOnScreenOnly
            self.kCGNullWindowID = kCGNullWindowID
            self.available = True
        except ImportError:
            logger.error("pyobjc not available for macOS")
            self.available = False
    
    def get_active_window(self) -> Optional[Tuple[str, str]]:
        """Get active window on macOS."""
        if not self.available:
            return None
        
        try:
            # Get the active application
            workspace = self.NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            
            if not active_app:
                return None
            
            app_name = active_app.get('NSApplicationName', 'Unknown')
            
            # Get window information
            window_list = self.CGWindowListCopyWindowInfo(
                self.kCGWindowListOptionOnScreenOnly, 
                self.kCGNullWindowID
            )
            
            # Find the frontmost window
            for window in window_list:
                if window.get('kCGWindowLayer', 0) == 0:  # Normal window layer
                    owner_name = window.get('kCGWindowOwnerName', '')
                    window_title = window.get('kCGWindowName', '')
                    
                    if owner_name == app_name and window_title:
                        return (app_name, window_title)
            
            return (app_name, "Unknown Window")
        
        except Exception as e:
            logger.error(f"Error getting active window on macOS: {e}")
            return None

class LinuxWindowTracker(WindowTracker):
    """Linux-specific window tracker using python-xlib."""
    
    def __init__(self):
        try:
            from Xlib import display
            from Xlib.error import XError
            self.display = display
            self.XError = XError
            self.available = True
        except ImportError:
            logger.error("python-xlib not available for Linux")
            self.available = False
    
    def get_active_window(self) -> Optional[Tuple[str, str]]:
        """Get active window on Linux."""
        if not self.available:
            return None
        
        try:
            # Connect to X server
            d = self.display.Display()
            
            # Get the root window
            root = d.screen().root
            
            # Get the currently focused window
            focus = d.get_input_focus()
            if focus.focus:
                window = focus.focus
                
                # Get window properties
                window_title = self._get_window_title(window)
                app_name = self._get_app_name(window)
                
                return (app_name, window_title)
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting active window on Linux: {e}")
            return None
    
    def _get_window_title(self, window) -> str:
        """Get window title from X window."""
        try:
            # Try different properties for window title
            for prop in ['_NET_WM_NAME', 'WM_NAME']:
                try:
                    atom = window.display.intern_atom(prop)
                    title = window.get_full_property(atom, 0)
                    if title and title.value:
                        return title.value.decode('utf-8', errors='ignore')
                except:
                    continue
            return "Unknown Window"
        except:
            return "Unknown Window"
    
    def _get_app_name(self, window) -> str:
        """Get application name from X window."""
        try:
            # Try to get WM_CLASS
            wm_class = window.get_wm_class()
            if wm_class:
                return wm_class[1] if len(wm_class) > 1 else wm_class[0]
            
            # Try to get process name
            try:
                atom = window.display.intern_atom('_NET_WM_PID')
                pid_prop = window.get_full_property(atom, 0)
                if pid_prop:
                    pid = pid_prop.value[0]
                    try:
                        import psutil
                        process = psutil.Process(pid)
                        return process.name()
                    except:
                        pass
            except:
                pass
            
            return "Unknown App"
        except:
            return "Unknown App"

class ActivityTracker:
    """Main activity tracker that monitors active windows."""
    
    def __init__(self):
        self.tracker = self._get_platform_tracker()
        self.current_session = None
        self.last_window_info = None
        self.tracking_enabled = True
        self.stop_event = Event()
        self.thread = None
        self.session_start_time = None
        
        # Import database here to avoid circular imports
        from database import db
        self.db = db
    
    def _get_platform_tracker(self) -> WindowTracker:
        """Get the appropriate tracker for the current platform."""
        system = platform.system()
        
        if system == "Windows":
            return WindowsWindowTracker()
        elif system == "Darwin":
            return MacOSWindowTracker()
        elif system == "Linux":
            return LinuxWindowTracker()
        else:
            logger.error(f"Unsupported platform: {system}")
            return None
    
    def start_tracking(self, interval: int = 5):
        """Start tracking activity in a separate thread."""
        if self.thread and self.thread.is_alive():
            logger.warning("Tracking already running")
            return
        
        self.stop_event.clear()
        self.session_start_time = datetime.now()
        self.thread = Thread(target=self._tracking_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
        logger.info("Activity tracking started")
    
    def stop_tracking(self):
        """Stop tracking activity."""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        # End current session if exists
        if self.current_session:
            self.db.end_session(self.current_session)
            self.current_session = None
        
        logger.info("Activity tracking stopped")
    
    def pause_tracking(self):
        """Pause tracking."""
        self.tracking_enabled = False
        logger.info("Activity tracking paused")
    
    def resume_tracking(self):
        """Resume tracking."""
        self.tracking_enabled = True
        self.session_start_time = datetime.now()
        logger.info("Activity tracking resumed")
    
    def _tracking_loop(self, interval: int):
        """Main tracking loop."""
        while not self.stop_event.is_set():
            try:
                if self.tracking_enabled and self.tracker:
                    self._check_window_change()
                
                # Wait for the specified interval
                if self.stop_event.wait(timeout=interval):
                    break
                    
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(interval)
    
    def _check_window_change(self):
        """Check if the active window has changed."""
        try:
            current_window = self.tracker.get_active_window()
            
            if current_window != self.last_window_info:
                # Window changed - end current session and start new one
                if self.current_session:
                    self.db.end_session(self.current_session)
                
                if current_window:
                    app_name, window_title = current_window
                    self.current_session = self.db.start_session(app_name, window_title)
                    logger.debug(f"New session started: {app_name} - {window_title}")
                else:
                    self.current_session = None
                
                self.last_window_info = current_window
        
        except Exception as e:
            logger.error(f"Error checking window change: {e}")
    
    def get_current_window(self) -> Optional[Tuple[str, str]]:
        """Get current active window information."""
        if self.tracker:
            return self.tracker.get_active_window()
        return None
    
    def is_tracking(self) -> bool:
        """Check if tracking is currently active."""
        return self.thread and self.thread.is_alive() and self.tracking_enabled

# Global activity tracker instance
activity_tracker = ActivityTracker() 