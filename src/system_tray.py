import io
import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu
import logging

from .config import config
from .window_tracker import activity_tracker
from .database import db

logger = logging.getLogger(__name__)

class SystemTrayApp:
    """System tray application for controlling activity tracking."""
    
    def __init__(self):
        self.icon = None
        self.tracking_enabled = True
        self.web_server_thread = None
        self.web_server = None
        self.current_session_start = None
        self.current_session_time = 0
        self.last_update_time = None
        
        # Create tray icon
        self.create_icon()
        
        # Initialize tracking
        self.start_tracking()
        
        # Start session timer
        self.start_session_timer()
    
    def create_icon(self):
        """Create the system tray icon."""
        # Create a simple icon programmatically
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple circle
        draw.ellipse([10, 10, 54, 54], fill='blue', outline='darkblue', width=2)
        
        # Add text
        draw.text((20, 25), "AW", fill='white')
        
        return image
    
    def create_menu(self):
        """Create the context menu for the tray icon."""
        # Get current session time for display
        session_time_str = self.get_session_time_string()
        
        # Get today's total time
        today_total_str = self.get_today_total_time_string()
        
        return Menu(
            MenuItem(
                f"Session: {session_time_str}",
                self.show_status,
                default=True
            ),
            MenuItem(
                f"Today: {today_total_str}",
                self.show_status,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            MenuItem(
                "Pause Tracking" if self.tracking_enabled else "Resume Tracking",
                self.toggle_tracking
            ),
            pystray.Menu.SEPARATOR,
            MenuItem(
                "Open Dashboard",
                self.open_dashboard
            ),
            MenuItem(
                "View Statistics",
                self.show_stats
            ),
            pystray.Menu.SEPARATOR,
            MenuItem(
                "Settings",
                self.open_settings
            ),
            MenuItem(
                "About",
                self.show_about
            ),
            pystray.Menu.SEPARATOR,
            MenuItem(
                "Exit",
                self.quit_app
            )
        )
    
    def start_session_timer(self):
        """Start the session timer for real-time tracking."""
        self.current_session_start = datetime.now()
        self.last_update_time = datetime.now()
        self.update_session_timer()
    
    def update_session_timer(self):
        """Update the session timer and refresh menu."""
        if self.tracking_enabled and self.current_session_start:
            current_time = datetime.now()
            if self.last_update_time:
                time_diff = (current_time - self.last_update_time).total_seconds()
                self.current_session_time += time_diff
            self.last_update_time = current_time
            
            # Update menu every 10 seconds
            if hasattr(self, 'icon') and self.icon:
                self.icon.menu = self.create_menu()
        
        # Schedule next update
        threading.Timer(10.0, self.update_session_timer).start()
    
    def get_session_time_string(self):
        """Get formatted session time string."""
        if not self.tracking_enabled:
            return "Paused"
        
        total_seconds = int(self.current_session_time)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_today_total_time_string(self):
        """Get formatted today's total time string in HH:MM:SS format."""
        try:
            today_stats = db.get_daily_stats()
            total_seconds = today_stats.get('total_time', 0)
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except Exception as e:
            logger.error(f"Error getting today's total time: {e}")
            return "00:00:00"
    
    def start_tracking(self):
        """Start activity tracking."""
        if config.get('tracking_enabled', True):
            activity_tracker.start_tracking(config.get('tracking_interval', 5))
            self.tracking_enabled = True
            logger.info("Activity tracking started")
        else:
            self.tracking_enabled = False
            logger.info("Activity tracking disabled in config")
    
    def toggle_tracking(self, icon, item):
        """Toggle tracking on/off."""
        if self.tracking_enabled:
            activity_tracker.pause_tracking()
            self.tracking_enabled = False
            config.set('tracking_enabled', False)
            logger.info("Activity tracking paused")
        else:
            activity_tracker.resume_tracking()
            self.tracking_enabled = True
            config.set('tracking_enabled', True)
            self.current_session_start = datetime.now()
            self.last_update_time = datetime.now()
            logger.info("Activity tracking resumed")
        
        # Update menu
        icon.menu = self.create_menu()
    
    def show_status(self, icon, item):
        """Show current status."""
        current_window = activity_tracker.get_current_window()
        status = "Active" if self.tracking_enabled else "Paused"
        session_time = self.get_session_time_string()
        
        if current_window:
            app_name, window_title = current_window
            message = f"Status: {status}\nSession Time: {session_time}\nCurrent: {app_name}\nWindow: {window_title}"
        else:
            message = f"Status: {status}\nSession Time: {session_time}\nNo active window detected"
        
        # Show message box with proper window management
        self._show_message_dialog("Activity Tracker Status", message)
    
    def open_dashboard(self, icon, item):
        """Open the web dashboard."""
        self.start_web_server()
        webbrowser.open('http://localhost:5000')
    
    def show_stats(self, icon, item):
        """Show quick statistics."""
        try:
            # Get today's stats
            today_stats = db.get_daily_stats()
            total_time = today_stats.get('total_time', 0)
            
            # Get top apps
            top_apps = db.get_top_apps(days=1, limit=3)
            
            # Format time
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            # Current session time
            session_time = self.get_session_time_string()
            
            # Build message
            message = f"Today's Screen Time: {hours}h {minutes}m\n"
            message += f"Current Session: {session_time}\n\n"
            
            if top_apps:
                message += "Top Applications Today:\n"
                for i, app in enumerate(top_apps, 1):
                    app_hours = app['total_duration'] // 3600
                    app_minutes = (app['total_duration'] % 3600) // 60
                    message += f"{i}. {app['app_name']}: {app_hours}h {app_minutes}m\n"
            else:
                message += "No applications tracked today"
            
            # Show message box with proper window management
            self._show_message_dialog("Activity Statistics", message)
            
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            self._show_message_dialog("Error", f"Failed to load statistics: {e}", is_error=True)
    
    def open_settings(self, icon, item):
        """Open settings dialog."""
        try:
            # Create settings window in a separate thread
            def create_settings_window():
                root = tk.Tk()
                root.title("Settings")
                root.geometry("400x350")
                root.resizable(False, False)
                
                # Center the window
                root.update_idletasks()
                x = (root.winfo_screenwidth() // 2) - (400 // 2)
                y = (root.winfo_screenheight() // 2) - (350 // 2)
                root.geometry(f"400x350+{x}+{y}")
                
                # Make window stay on top
                root.attributes('-topmost', True)
                root.focus_force()
                
                # Create settings content
                title_label = tk.Label(root, text="Local Activity Watcher Settings", font=("Arial", 14, "bold"))
                title_label.pack(pady=10)
                
                # Tracking settings
                tracking_frame = tk.Frame(root)
                tracking_frame.pack(pady=10, padx=20, fill='x')
                
                tracking_label = tk.Label(tracking_frame, text="Tracking Settings", font=("Arial", 12, "bold"))
                tracking_label.pack(anchor='w')
                
                interval_frame = tk.Frame(tracking_frame)
                interval_frame.pack(fill='x', pady=5)
                
                tk.Label(interval_frame, text="Tracking Interval (seconds):").pack(side='left')
                interval_var = tk.StringVar(value=str(config.get('tracking_interval', 5)))
                interval_spinbox = tk.Spinbox(interval_frame, from_=1, to=60, textvariable=interval_var, width=10)
                interval_spinbox.pack(side='right')
                
                # Data management
                data_frame = tk.Frame(root)
                data_frame.pack(pady=20, padx=20, fill='x')
                
                data_label = tk.Label(data_frame, text="Data Management", font=("Arial", 12, "bold"))
                data_label.pack(anchor='w')
                
                # Reset data button
                reset_button = tk.Button(data_frame, text="Reset All Data", 
                                       command=lambda: self.reset_data_confirm(root),
                                       bg='#ff6b6b', fg='white', font=("Arial", 10, "bold"))
                reset_button.pack(pady=10)
                
                # Buttons
                button_frame = tk.Frame(root)
                button_frame.pack(pady=20)
                
                def save_settings():
                    try:
                        config.set('tracking_interval', int(interval_var.get()))
                        messagebox.showinfo("Settings", "Settings saved successfully!")
                        root.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save settings: {e}")
                
                def cancel_settings():
                    root.destroy()
                
                save_button = tk.Button(button_frame, text="Save", command=save_settings, 
                                      bg='#4CAF50', fg='white', padx=20)
                save_button.pack(side='left', padx=10)
                
                cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_settings, padx=20)
                cancel_button.pack(side='left', padx=10)
                
                # Handle window close event
                root.protocol("WM_DELETE_WINDOW", cancel_settings)
                
                # Start the GUI event loop
                root.mainloop()
            
            # Run settings window in a separate thread
            settings_thread = threading.Thread(target=create_settings_window, daemon=True)
            settings_thread.start()
            
        except Exception as e:
            logger.error(f"Error opening settings: {e}")
            self._show_message_dialog("Error", f"Failed to open settings: {e}", is_error=True)
    
    def reset_data_confirm(self, parent_window):
        """Confirm data reset with user."""
        # Make sure parent window is on top for the dialog
        parent_window.attributes('-topmost', True)
        parent_window.lift()
        
        result = messagebox.askyesno("Confirm Reset", 
                                   "Are you sure you want to reset all data?\n\nThis will permanently delete:\n• All activity history\n• All application sessions\n• All daily summaries\n\nThis action cannot be undone!",
                                   icon="warning",
                                   parent=parent_window)
        if result:
            try:
                db.reset_all_data()
                messagebox.showinfo("Success", "All data has been reset successfully!", parent=parent_window)
                
                # Reset current session data
                self.current_session_time = 0
                self.current_session_start = datetime.now()
                self.last_update_time = datetime.now()
                
                # Update menu
                if hasattr(self, 'icon') and self.icon:
                    self.icon.menu = self.create_menu()
                    
            except Exception as e:
                logger.error(f"Error resetting data: {e}")
                messagebox.showerror("Error", f"Failed to reset data: {e}", parent=parent_window)
    
    def show_about(self, icon, item):
        """Show about dialog with developer information."""
        about_text = f"""Local Activity Watcher v{config.version}

A privacy-focused activity tracker that monitors your computer usage locally without sending any data to external servers.

Developer: Allain-afk
GitHub: https://github.com/Allain-afk

Features:
• Real-time activity tracking
• Beautiful web dashboard
• Privacy-first design
• Cross-platform support

Data Location: {config.db_file}

All data stays on your local machine - no cloud sync or external servers."""
        
        # Show message box with developer info
        self._show_message_dialog("About Local Activity Watcher", about_text)
    
    def _show_message_dialog(self, title, message, is_error=False):
        """Show a message dialog with proper window management."""
        def show_dialog():
            try:
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                root.attributes('-topmost', True)  # Keep dialog on top
                root.lift()  # Bring to front
                root.focus_force()
                
                if is_error:
                    messagebox.showerror(title, message)
                else:
                    messagebox.showinfo(title, message)
                    
                root.destroy()
            except Exception as e:
                logger.error(f"Error showing message dialog: {e}")
        
        # Run dialog in a separate thread to avoid blocking
        dialog_thread = threading.Thread(target=show_dialog, daemon=True)
        dialog_thread.start()
    
    def start_web_server(self):
        """Start the web server for the dashboard."""
        if self.web_server_thread and self.web_server_thread.is_alive():
            return  # Already running
        
        try:
            def run_server():
                try:
                    from .web_dashboard import create_app
                except ImportError:
                    from web_dashboard import create_app
                app = create_app()
                app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
            
            self.web_server_thread = threading.Thread(target=run_server, daemon=True)
            self.web_server_thread.start()
            logger.info("Web server started on http://localhost:5000")
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
    
    def quit_app(self, icon, item):
        """Quit the application."""
        logger.info("Shutting down Activity Tracker...")
        
        # Stop tracking
        if self.tracking_enabled:
            activity_tracker.stop_tracking()
        
        # Stop the icon
        icon.stop()
        
        # Exit the application
        sys.exit(0)
    
    def run(self):
        """Run the system tray application."""
        try:
            # Create and run the icon
            self.icon = pystray.Icon(
                "ActivityTracker",
                self.create_icon(),
                "Local Activity Watcher",
                self.create_menu()
            )
            
            logger.info("System tray application started")
            self.icon.run()
            
        except Exception as e:
            logger.error(f"System tray error: {e}")
            raise

def main():
    """Main function for testing."""
    app = SystemTrayApp()
    app.run()

if __name__ == "__main__":
    main() 