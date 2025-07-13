# ActivityWatcher v1.0.4 Release Notes

## 🎉 What's New

- **Fixed System Tray GUI Issues**: All windows (Settings, About, View Statistics) now work properly and are fully interactive
- **Improved Project Structure**: Clean separation with `src/` for main code and `tests/` for test files
- **Enhanced Documentation**: Comprehensive README with project structure diagram
- **Better Window Management**: Improved threading and focus handling for GUI components
- **Professional Package Structure**: Proper Python package organization with `__init__.py` files

## 🚀 Features

- **Privacy-First**: 100% local data storage - no cloud, no external servers
- **Cross-Platform**: Windows, macOS, and Linux support
- **System Tray Operation**: Runs silently in background with right-click menu
- **Web Dashboard**: Beautiful local web interface at `http://localhost:5000`
- **Real-Time Tracking**: Monitor applications and window titles
- **Detailed Reports**: Daily, weekly, and monthly statistics
- **Easy Building**: Single command to create standalone executable

## 📦 Download & Installation

### Quick Start
1. Download `ActivityWatcher-v1.0.4-Windows.zip`
2. Extract the zip file
3. Run `LocalActivityWatcher.exe`
4. Optional: Run `install.bat` as administrator for system integration

### What's Included
- `LocalActivityWatcher.exe` - Main application (12.7 MB)
- `install.bat` - Installation script
- `uninstall.bat` - Uninstallation script  
- `README.txt` - Usage instructions

## 🔧 System Requirements

- **Windows**: Windows 10/11 (tested)
- **Memory**: ~50 MB RAM usage
- **Storage**: ~13 MB disk space
- **Network**: None required (completely offline)

## 🐛 Bug Fixes

- Fixed system tray GUI windows not responding to user interaction
- Resolved window focus issues in Settings and About dialogs
- Fixed import path issues in restructured codebase
- Improved error handling for GUI operations

## 🔒 Privacy & Security

- ✅ **100% Local**: All data stays on your machine
- ✅ **No Network**: No external connections
- ✅ **No Telemetry**: No data collection or analytics
- ✅ **Open Source**: Full transparency
- ✅ **Minimal Permissions**: Only requires window access

## 📊 Data Storage

All data is stored locally in `~/.local_activity_watcher/`:
- Configuration settings
- Activity database (SQLite)
- Application logs

## 🔄 Auto-Start Setup

Copy `LocalActivityWatcher.exe` to your Windows startup folder:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```

## 🛠️ For Developers

- **Source Code**: Available in the repository
- **Build**: Run `python build.py` 
- **Tests**: Run `python -m pytest tests/`
- **Structure**: Clean `src/` and `tests/` organization

## 🙏 Support

- **Issues**: Report on GitHub Issues
- **Documentation**: See README.md
- **Contributing**: Fork and submit PRs

---

**Full Changelog**: [View on GitHub](https://github.com/Allain-afk/ActivityWatcher/compare/v1.0.3...v1.0.4) 