import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from config import config

class ActivityDatabase:
    """Database manager for activity tracking."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    app_name TEXT NOT NULL,
                    window_title TEXT,
                    duration INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS app_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    window_title TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    total_time INTEGER DEFAULT 0,
                    app_breakdown TEXT,  -- JSON string
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Enhanced activity tracking table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS enhanced_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    app_name TEXT NOT NULL,
                    window_title TEXT,
                    duration INTEGER DEFAULT 0,
                    url TEXT,
                    file_path TEXT,
                    category TEXT,
                    productivity_score REAL,
                    activity_intensity REAL,
                    is_idle BOOLEAN DEFAULT 0,
                    cpu_percent REAL,
                    memory_percent REAL,
                    idle_time REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_activities_app_name ON activities(app_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON app_sessions(start_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_app_name ON app_sessions(app_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_enhanced_timestamp ON enhanced_activities(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_enhanced_app_name ON enhanced_activities(app_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_enhanced_category ON enhanced_activities(category)')
    
    def record_activity(self, app_name: str, window_title: str = None, duration: int = 0):
        """Record a single activity entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO activities (timestamp, app_name, window_title, duration)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now(), app_name, window_title, duration))
    
    def record_enhanced_activity(self, activity_data: Dict):
        """Record enhanced activity data with additional context."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO enhanced_activities (
                    timestamp, app_name, window_title, duration, url, file_path,
                    category, productivity_score, activity_intensity, is_idle,
                    cpu_percent, memory_percent, idle_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity_data['timestamp'],
                activity_data['app_name'],
                activity_data['window_title'],
                activity_data['duration'],
                activity_data.get('url'),
                activity_data.get('file_path'),
                activity_data.get('category'),
                activity_data.get('productivity_score'),
                activity_data.get('activity_intensity'),
                activity_data.get('is_idle'),
                activity_data.get('cpu_percent'),
                activity_data.get('memory_percent'),
                activity_data.get('idle_time')
            ))
    
    def start_session(self, app_name: str, window_title: str = None) -> int:
        """Start a new session and return session ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO app_sessions (app_name, window_title, start_time)
                VALUES (?, ?, ?)
            ''', (app_name, window_title, datetime.now()))
            return cursor.lastrowid
    
    def end_session(self, session_id: int):
        """End a session and calculate duration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                UPDATE app_sessions 
                SET end_time = ?, duration = CAST((julianday(?) - julianday(start_time)) * 86400 AS INTEGER)
                WHERE id = ?
            ''', (datetime.now(), datetime.now(), session_id))
    
    def get_app_stats(self, days: int = 7) -> List[Dict]:
        """Get application usage statistics for the last N days."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT app_name, 
                       SUM(duration) as total_duration,
                       COUNT(*) as session_count,
                       AVG(duration) as avg_duration
                FROM app_sessions 
                WHERE start_time >= ? AND end_time IS NOT NULL
                GROUP BY app_name
                ORDER BY total_duration DESC
            ''', (start_date,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'app_name': row[0],
                    'total_duration': row[1],
                    'session_count': row[2],
                    'avg_duration': row[3]
                })
            return results
    
    def get_daily_stats(self, date: str = None) -> Dict:
        """Get daily statistics for a specific date."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        start_time = datetime.strptime(date, '%Y-%m-%d')
        end_time = start_time + timedelta(days=1)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get total time
            cursor = conn.execute('''
                SELECT SUM(duration) as total_time
                FROM app_sessions 
                WHERE start_time >= ? AND start_time < ? AND end_time IS NOT NULL
            ''', (start_time, end_time))
            
            total_time = cursor.fetchone()[0] or 0
            
            # Get app breakdown
            cursor = conn.execute('''
                SELECT app_name, SUM(duration) as duration
                FROM app_sessions 
                WHERE start_time >= ? AND start_time < ? AND end_time IS NOT NULL
                GROUP BY app_name
                ORDER BY duration DESC
            ''', (start_time, end_time))
            
            app_breakdown = [{'app_name': row[0], 'duration': row[1]} for row in cursor.fetchall()]
            
            return {
                'date': date,
                'total_time': total_time,
                'app_breakdown': app_breakdown
            }
    
    def get_weekly_stats(self) -> List[Dict]:
        """Get weekly statistics."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            stats = self.get_daily_stats(date_str)
            daily_stats.append(stats)
            current_date += timedelta(days=1)
        
        return daily_stats
    
    def get_top_apps(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get top applications by usage time."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT app_name, 
                       SUM(duration) as total_duration,
                       COUNT(*) as session_count
                FROM app_sessions 
                WHERE start_time >= ? AND end_time IS NOT NULL
                GROUP BY app_name
                ORDER BY total_duration DESC
                LIMIT ?
            ''', (start_date, limit))
            
            return [{'app_name': row[0], 'total_duration': row[1], 'session_count': row[2]} 
                   for row in cursor.fetchall()]
    
    def get_window_titles(self, app_name: str, days: int = 7) -> List[Dict]:
        """Get window titles for a specific app."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT window_title, 
                       SUM(duration) as total_duration,
                       COUNT(*) as session_count
                FROM app_sessions 
                WHERE app_name = ? AND start_time >= ? AND end_time IS NOT NULL
                GROUP BY window_title
                ORDER BY total_duration DESC
            ''', (app_name, start_date))
            
            return [{'window_title': row[0], 'total_duration': row[1], 'session_count': row[2]} 
                   for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to prevent database bloat."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM activities WHERE timestamp < ?', (cutoff_date,))
            conn.execute('DELETE FROM app_sessions WHERE start_time < ?', (cutoff_date,))
            conn.execute('DELETE FROM daily_summaries WHERE date < ?', (cutoff_date.strftime('%Y-%m-%d'),))
    
    def reset_all_data(self):
        """Reset all data by clearing all tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM activities')
            conn.execute('DELETE FROM app_sessions')
            conn.execute('DELETE FROM daily_summaries')
            conn.commit()
    
    def export_data(self, start_date: str, end_date: str) -> Dict:
        """Export data for a date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM app_sessions 
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time
            ''', (start_date, end_date))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'app_name': row[1],
                    'window_title': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'duration': row[5]
                })
            
            return {'sessions': sessions}
    
    def get_enhanced_stats(self, days: int = 7) -> Dict:
        """Get enhanced statistics including productivity and activity patterns."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get productivity stats
            cursor = conn.execute('''
                SELECT AVG(productivity_score) as avg_productivity,
                       AVG(activity_intensity) as avg_intensity,
                       SUM(CASE WHEN is_idle = 0 THEN duration ELSE 0 END) as active_time,
                       SUM(CASE WHEN is_idle = 1 THEN duration ELSE 0 END) as idle_time
                FROM enhanced_activities 
                WHERE timestamp >= ?
            ''', (start_date,))
            
            productivity_data = cursor.fetchone()
            
            # Get category breakdown
            cursor = conn.execute('''
                SELECT category, 
                       SUM(duration) as total_duration,
                       AVG(productivity_score) as avg_productivity,
                       COUNT(*) as activity_count
                FROM enhanced_activities 
                WHERE timestamp >= ? AND category IS NOT NULL
                GROUP BY category
                ORDER BY total_duration DESC
            ''', (start_date,))
            
            category_breakdown = []
            for row in cursor.fetchall():
                category_breakdown.append({
                    'category': row[0],
                    'total_duration': row[1],
                    'avg_productivity': row[2],
                    'activity_count': row[3]
                })
            
            # Get system resource usage patterns
            cursor = conn.execute('''
                SELECT app_name,
                       AVG(cpu_percent) as avg_cpu,
                       AVG(memory_percent) as avg_memory,
                       SUM(duration) as total_duration
                FROM enhanced_activities 
                WHERE timestamp >= ? AND cpu_percent IS NOT NULL
                GROUP BY app_name
                ORDER BY total_duration DESC
                LIMIT 10
            ''', (start_date,))
            
            resource_usage = []
            for row in cursor.fetchall():
                resource_usage.append({
                    'app_name': row[0],
                    'avg_cpu': row[1],
                    'avg_memory': row[2],
                    'total_duration': row[3]
                })
            
            return {
                'productivity_stats': {
                    'avg_productivity': productivity_data[0] or 0,
                    'avg_intensity': productivity_data[1] or 0,
                    'active_time': productivity_data[2] or 0,
                    'idle_time': productivity_data[3] or 0
                },
                'category_breakdown': category_breakdown,
                'resource_usage': resource_usage
            }
    
    def get_browser_activity(self, days: int = 7) -> List[Dict]:
        """Get browser activity with URLs."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT url, window_title, 
                       SUM(duration) as total_duration,
                       COUNT(*) as visit_count,
                       AVG(activity_intensity) as avg_intensity
                FROM enhanced_activities 
                WHERE timestamp >= ? AND url IS NOT NULL
                GROUP BY url
                ORDER BY total_duration DESC
                LIMIT 20
            ''', (start_date,))
            
            return [{'url': row[0], 'title': row[1], 'duration': row[2], 
                    'visits': row[3], 'intensity': row[4]} for row in cursor.fetchall()]
    
    def get_productivity_trends(self, days: int = 30) -> List[Dict]:
        """Get productivity trends over time."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT DATE(timestamp) as date,
                       AVG(productivity_score) as avg_productivity,
                       AVG(activity_intensity) as avg_intensity,
                       SUM(duration) as total_duration,
                       SUM(CASE WHEN is_idle = 0 THEN duration ELSE 0 END) as active_duration
                FROM enhanced_activities 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (start_date,))
            
            return [{'date': row[0], 'productivity': row[1], 'intensity': row[2], 
                    'total_duration': row[3], 'active_duration': row[4]} 
                   for row in cursor.fetchall()]

# Global database instance
db = ActivityDatabase() 