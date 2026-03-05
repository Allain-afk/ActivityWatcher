# Enhanced Activity Tracking Features

This document describes the enhanced activity tracking features added to ActivityWatcher to provide better insights into user behavior and productivity.

## Overview

The enhanced activity tracking system provides:
- **Idle time detection** - Distinguishes between active and idle time
- **Activity intensity measurement** - Tracks mouse/keyboard activity levels
- **Smart categorization** - Automatically categorizes activities by type
- **Productivity scoring** - Calculates productivity metrics
- **Browser tracking** - Extracts URLs and website information
- **Resource monitoring** - Tracks CPU and memory usage
- **Focus session detection** - Identifies periods of concentrated work
- **Improved session management** - Better handling of application sessions

## Key Components

### 1. Enhanced Activity Monitor (`activity_monitor.py`)

The `EnhancedActivityTracker` class provides comprehensive activity monitoring:

```python
from activity_monitor import enhanced_activity_tracker

# Get activity intensity (0.0 to 1.0)
intensity = enhanced_activity_tracker.get_activity_intensity()

# Check if user is idle
is_idle = enhanced_activity_tracker.is_user_idle()

# Get enhanced window information
info = enhanced_activity_tracker.get_enhanced_window_info(app_name, window_title)
```

#### Features:
- **Cross-platform idle detection** (Windows, macOS, Linux)
- **Activity intensity calculation** based on mouse/keyboard activity
- **Smart activity categorization** (work, entertainment, communication, etc.)
- **Productivity scoring** (0.0 to 1.0 scale)
- **URL extraction** from browser windows
- **File path detection** from editor windows
- **System resource monitoring** (CPU, memory usage)

### 2. Improved Session Management

The window tracker now includes advanced session management:

```python
from window_tracker import activity_tracker

# Get current session statistics
session_stats = activity_tracker.get_session_stats()

# Get focus sessions (5+ minute concentrated work periods)
focus_sessions = activity_tracker.get_focus_sessions(days=7)
```

#### Features:
- **Minimum session duration** (30 seconds) to filter out brief switches
- **Focus session detection** (5+ minute periods) for productivity tracking
- **Idle session handling** - automatically ends sessions during idle periods
- **Session quality metrics** - tracks activity count and idle time per session

### 3. Enhanced Database Schema

New database table `enhanced_activities` stores detailed activity data:

```sql
CREATE TABLE enhanced_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    app_name TEXT NOT NULL,
    window_title TEXT,
    duration INTEGER DEFAULT 0,
    url TEXT,                    -- Extracted URL for browsers
    file_path TEXT,              -- File path for editors
    category TEXT,               -- Activity category
    productivity_score REAL,     -- Productivity score (0.0-1.0)
    activity_intensity REAL,     -- Activity intensity (0.0-1.0)
    is_idle BOOLEAN DEFAULT 0,   -- Whether user was idle
    cpu_percent REAL,            -- CPU usage
    memory_percent REAL,         -- Memory usage
    idle_time REAL,              -- Idle time in seconds
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4. New API Endpoints

Enhanced REST API endpoints for accessing detailed activity data:

```
GET /api/enhanced/stats?days=7
GET /api/enhanced/browser-activity?days=7
GET /api/enhanced/productivity-trends?days=30
GET /api/enhanced/activity-intensity
GET /api/session/current
GET /api/session/focus?days=7
```

### 5. Enhanced CLI Commands

New command-line interface for detailed analytics:

```bash
# Show enhanced statistics
python run.py enhanced --days 7

# Show browser activity and productivity trends
python run.py enhanced --days 7 --show-browser --show-trends

# Regular stats now include productivity metrics
python run.py stats
```

## Activity Categories

The system automatically categorizes activities into:

- **Development** - Code editors, IDEs, terminals, development websites
- **Communication** - Email, chat, video calls, messaging apps
- **Entertainment** - Games, music, video streaming, social media
- **Productivity** - Office apps, note-taking, project management
- **Web Browsing** - General web browsing activities
- **Other** - Uncategorized activities

## Productivity Scoring

Activities are scored on a 0.0 to 1.0 scale:

- **Development** (0.9) - Coding, technical documentation
- **Productivity** (0.8) - Office work, note-taking
- **Communication** (0.6) - Work-related communication
- **Web Browsing** (0.4) - General browsing
- **Entertainment** (0.1) - Games, streaming, social media

## Configuration Options

New configuration settings in `config.json`:

```json
{
  "enhanced_tracking": true,
  "idle_threshold": 60,
  "activity_sampling_rate": 5,
  "browser_url_tracking": true,
  "productivity_tracking": true,
  "resource_monitoring": true
}
```

## Usage Examples

### Basic Usage

```python
# Get today's enhanced statistics
stats = db.get_enhanced_stats(days=1)
print(f"Average productivity: {stats['productivity_stats']['avg_productivity']:.2f}")

# Get browser activity
browser_activity = db.get_browser_activity(days=7)
for activity in browser_activity:
    print(f"URL: {activity['url']}, Time: {activity['duration']}s")

# Get productivity trends
trends = db.get_productivity_trends(days=30)
for trend in trends:
    print(f"Date: {trend['date']}, Productivity: {trend['productivity']:.2f}")
```

### Web Dashboard Integration

The enhanced features are automatically integrated into the web dashboard at `http://localhost:5000`, showing:

- Current session information
- Productivity metrics
- Activity intensity
- Focus session tracking
- Enhanced statistics

### CLI Usage

```bash
# Show comprehensive enhanced statistics
python run.py enhanced --days 7 --show-browser --show-trends

# Example output:
Enhanced Statistics (Last 7 days)
==================================================
Average Productivity Score: 0.68
Average Activity Intensity: 0.15
Active Time: 6h 30m
Idle Time: 15.2%

Activity Categories:
  development    : 4h 20m (avg productivity: 0.87)
  communication  : 1h 45m (avg productivity: 0.60)
  entertainment  : 0h 25m (avg productivity: 0.10)

Browser Activity:
  https://github.com/user/repo... (45m)
  https://stackoverflow.com/questions... (22m)
```

## Performance Considerations

- Enhanced tracking adds minimal overhead (~1-2% CPU usage)
- Database queries are optimized with appropriate indexes
- Activity sampling rate is configurable (default: 5 seconds)
- Old data cleanup is automatic (90-day retention by default)

## Privacy and Security

- All data remains local - no cloud sync or external connections
- URLs and file paths are stored locally only
- Resource monitoring data is aggregated and anonymized
- User can disable specific tracking features via configuration

## Future Enhancements

Planned improvements include:
- Machine learning-based activity prediction
- Advanced focus time analytics
- Pomodoro technique integration
- Team productivity comparisons (opt-in)
- Export functionality for external analysis tools