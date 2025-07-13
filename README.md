# Local Activity Watcher

<div align="center">
<img src="docs/project-structure.svg" alt="Project Structure" width="800"/>
</div>

A privacy-focused Python desktop application that tracks screen time usage across applications locally. All data stays on your machine - no cloud sync, no external servers, complete privacy.

## 🎯 Features

- **🔐 Privacy-First**: All data stays on your local machine
- **🌐 Cross-Platform**: Windows, macOS, Linux support
- **📱 System Tray**: Silent background operation
- **📊 Web Dashboard**: Beautiful local web interface
- **📋 Detailed Reports**: Daily, weekly, monthly summaries
- **🎮 Application Tracking**: Monitor time spent in different applications
- **🪟 Window Tracking**: Track specific windows and documents
- **⏸️ Pause/Resume**: Control tracking from system tray
- **📈 Statistics**: Real-time and historical data analysis

## 🏗️ Project Structure

```
ActivityWatcher/
├── src/                          # 🐍 Main application code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Application entry point
│   ├── system_tray.py           # System tray functionality
│   ├── window_tracker.py        # Window tracking system
│   ├── web_dashboard.py         # Web dashboard interface
│   ├── database.py              # Database management
│   ├── config.py                # Configuration management
│   ├── reports.py               # Report generation
│   └── templates/               # Web templates
│       └── dashboard.html       # Dashboard template
├── tests/                        # 🧪 Test files
│   ├── test_api.py              # API tests
│   ├── test_application.py      # Application tests
│   ├── test_tracking.py         # Tracking tests
│   └── ...                      # More test files
├── docs/                         # 📚 Documentation
│   └── project-structure.svg    # Project structure diagram
├── run.py                       # 🚀 Application launcher
├── build.py                     # 🔨 Build executable
├── requirements.txt             # 📦 Dependencies
├── README.md                    # 📖 This file
└── LICENSE                      # ⚖️ License file
```

## 📥 Installation

### Prerequisites

- **Python 3.7+** is required
- **pip** package manager

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Allain-afk/ActivityWatcher.git
   cd ActivityWatcher
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

### Platform-Specific Dependencies

The application automatically detects your platform and uses appropriate libraries:

- **Windows**: `pywin32` (for window tracking)
- **macOS**: `pyobjc` (for window tracking)
- **Linux**: `python-xlib` (for window tracking)

## 🚀 Usage

### System Tray Mode (Recommended)

```bash
python run.py
```

- Application runs silently in system tray
- Right-click tray icon for menu options:
  - **Pause/Resume Tracking**: Control monitoring
  - **Open Dashboard**: View statistics in browser
  - **View Statistics**: Quick stats popup
  - **Settings**: Configure application
  - **About**: Application information

### Command Line Interface

```bash
# Show help
python run.py --help

# Test window tracking
python run.py test

# Show quick statistics
python run.py stats

# Generate reports
python run.py report --type daily
python run.py report --type weekly
python run.py report --type monthly

# Start web dashboard only
python run.py web

# Run without system tray
python run.py --no-tray

# Enable debug mode
python run.py --debug
```

### Web Dashboard

Access the dashboard at `http://localhost:5000` (default port).

**Features:**
- 📊 Real-time tracking status
- 📈 Today's screen time summary
- 🏆 Top applications by usage
- 📅 Weekly/monthly overviews
- ⏯️ Interactive pause/resume controls
- 🎨 Beautiful, responsive interface

## ⚙️ Configuration

### Configuration File

Settings are stored in `~/.local_activity_watcher/config.json`:

```json
{
  "tracking_interval": 5,
  "window_title_tracking": true,
  "app_tracking": true,
  "auto_start": true,
  "web_port": 5000,
  "dark_mode": false,
  "tracking_enabled": true
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `tracking_interval` | Seconds between tracking updates | 5 |
| `window_title_tracking` | Track window titles | true |
| `app_tracking` | Track application usage | true |
| `auto_start` | Start with system | true |
| `web_port` | Web dashboard port | 5000 |
| `dark_mode` | Dark mode interface | false |
| `tracking_enabled` | Enable tracking | true |

## 🗂️ Data Storage

### File Locations

- **Configuration**: `~/.local_activity_watcher/config.json`
- **Database**: `~/.local_activity_watcher/activity.db`
- **Logs**: `~/.local_activity_watcher/activity_watcher.log`

### Database Schema

The application uses SQLite with the following main tables:

- **activities**: Raw activity data
- **applications**: Application metadata
- **daily_summaries**: Daily usage summaries
- **sessions**: Tracking sessions

## 🔧 How It Works

### Architecture Overview

1. **Window Tracker** (`window_tracker.py`):
   - Monitors active windows using platform-specific APIs
   - Captures application name and window title
   - Runs in background thread with configurable interval

2. **Database Manager** (`database.py`):
   - Stores activity data in local SQLite database
   - Provides queries for statistics and reports
   - Handles data aggregation and cleanup

3. **System Tray** (`system_tray.py`):
   - Provides user interface through system tray icon
   - Handles pause/resume functionality
   - Shows real-time session information

4. **Web Dashboard** (`web_dashboard.py`):
   - Flask-based web interface
   - Serves statistics and reports
   - Provides interactive controls

5. **Reports Generator** (`reports.py`):
   - Creates daily, weekly, monthly reports
   - Calculates usage statistics
   - Formats data for display

### Data Flow

```
Window Tracker → Database → Reports Generator
       ↓              ↓           ↓
System Tray ← Web Dashboard ← Statistics
```

## 🔨 Building Executable

### Create Standalone Executable

```bash
python build.py
```

This creates:
- **Executable**: `dist/LocalActivityWatcher.exe`
- **Installer**: `dist/install.bat`
- **Uninstaller**: `dist/uninstall.bat`
- **README**: `dist/README.txt`

### Build Configuration

The build process uses PyInstaller with optimized settings:
- Single-file executable
- Icon embedded
- All dependencies included
- Platform-specific optimizations

## 🔒 Privacy & Security

### Privacy Features

- ✅ **100% Local**: No data leaves your machine
- ✅ **No Network**: No external connections
- ✅ **No Cloud**: No cloud synchronization
- ✅ **No Telemetry**: No analytics or tracking
- ✅ **Open Source**: Transparent code
- ✅ **User Control**: Complete data ownership

### Security Measures

- Local SQLite database with no external access
- Configuration files stored in user directory
- No remote code execution
- Minimal system permissions required

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Test Structure

- **tests/test_api.py**: API endpoint tests
- **tests/test_application.py**: Application functionality tests
- **tests/test_tracking.py**: Window tracking tests
- **tests/simple_tests.py**: Basic functionality tests

## 🔄 Auto-Start Setup

### Windows
```bash
# Copy to startup folder
copy "dist\LocalActivityWatcher.exe" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"

# Or use Task Scheduler
schtasks /create /tn "ActivityWatcher" /tr "path\to\executable" /sc onlogon
```

### macOS
```bash
# Create plist file in ~/Library/LaunchAgents/
# See macOS documentation for launchctl
```

### Linux
```bash
# Create .desktop file in ~/.config/autostart/
# See Linux documentation for autostart
```

## 🛠️ Development

### Project Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/Allain-afk/ActivityWatcher.git
   cd ActivityWatcher
   pip install -r requirements.txt
   ```

2. **Run in development mode**:
   ```bash
   python run.py --debug
   ```

### Code Structure

- **src/**: Main application code
- **tests/**: Test files
- **docs/**: Documentation
- **build.py**: Build configuration
- **run.py**: Development runner

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 API Reference

### Web Dashboard Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard homepage |
| `/api/stats/today` | GET | Today's statistics |
| `/api/stats/weekly` | GET | Weekly statistics |
| `/api/apps/top` | GET | Top applications |
| `/api/tracking/status` | GET | Tracking status |
| `/api/tracking/toggle` | POST | Toggle tracking |
| `/api/config` | GET/POST | Configuration |

## 🐛 Troubleshooting

### Common Issues

1. **Application won't start**:
   - Check Python version (3.7+ required)
   - Verify dependencies: `pip install -r requirements.txt`
   - Check logs: `~/.local_activity_watcher/activity_watcher.log`

2. **No window tracking**:
   - Ensure platform dependencies are installed
   - Check permissions (especially macOS)
   - Verify X11 on Linux (not Wayland)

3. **Web dashboard not loading**:
   - Check if port 5000 is available
   - Try different port: `python run.py --port 8080`
   - Check firewall settings

4. **System tray not visible**:
   - Ensure system tray is enabled
   - Check if running in headless environment
   - Try: `python run.py --no-tray`

## 📄 License

This project is open source under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by [ActivityWatch](https://github.com/ActivityWatch/activitywatch)
- Built with Python, Flask, and SQLite
- Uses platform-specific libraries for window tracking
- System tray functionality powered by pystray

---

<div align="center">
Made with ❤️ by <a href="https://github.com/Allain-afk">Allain Legaspi</a>
</div> 