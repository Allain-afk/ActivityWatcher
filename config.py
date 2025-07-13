import os
import json
from pathlib import Path

class Config:
    """Configuration class for ActivityWatcher application."""
    
    def __init__(self):
        self.app_name = "LocalActivityWatcher"
        self.version = "1.0.4"
        
        # Data directory
        self.data_dir = Path.home() / ".local_activity_watcher"
        self.data_dir.mkdir(exist_ok=True)
        
        # Database file32
        self.db_file = self.data_dir / "activity.db"
        
        # Config file
        self.config_file = self.data_dir / "config.json"
        
        # Default settings
        self.default_settings = {
            "tracking_interval": 5,  # seconds
            "window_title_tracking": True,
            "app_tracking": True,
            "auto_start": True,
            "web_port": 5000,
            "dark_mode": False,
            "tracking_enabled": True
        }
        
        # Load or create config
        self.settings = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in self.default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_settings.copy()
    
    def save_config(self):
        """Save current settings to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get setting value."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set setting value and save."""
        self.settings[key] = value
        self.save_config()

# Global config instance
config = Config() 