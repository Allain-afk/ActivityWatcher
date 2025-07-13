# Local Activity Watcher

A privacy-focused Python desktop application that tracks screen time usage across applications locally. All data stays on your machine.

## Features

- Privacy-first: All data stays local
- Cross-platform: Windows, macOS, Linux
- System tray background operation
- Web dashboard for viewing reports
- Application and window tracking

## Installation

1. Install Python 3.7+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Usage

- **System Tray**: Right-click icon to pause/resume tracking or open dashboard
- **Web Dashboard**: Visit `http://localhost:5000` to view statistics
- **CLI**: `python main.py --help` for command options

## Configuration

Settings stored in `~/.local_activity_watcher/config.json`

## Building

Create executable: `python build.py` 