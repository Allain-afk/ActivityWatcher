from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime, timedelta
from config import config
from database import db
import os

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Configure Flask
    app.config['SECRET_KEY'] = 'local-activity-watcher-secret'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    @app.route('/')
    def index():
        """Main dashboard page."""
        return render_template('dashboard.html')
    
    @app.route('/api/stats/today')
    def get_today_stats():
        """Get today's statistics."""
        try:
            stats = db.get_daily_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats/weekly')
    def get_weekly_stats():
        """Get weekly statistics."""
        try:
            stats = db.get_weekly_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/apps/top')
    def get_top_apps():
        """Get top applications."""
        try:
            days = request.args.get('days', 7, type=int)
            limit = request.args.get('limit', 10, type=int)
            apps = db.get_top_apps(days=days, limit=limit)
            return jsonify(apps)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/apps/<app_name>/windows')
    def get_app_windows(app_name):
        """Get window titles for a specific app."""
        try:
            days = request.args.get('days', 7, type=int)
            windows = db.get_window_titles(app_name, days=days)
            return jsonify(windows)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats/range')
    def get_stats_range():
        """Get statistics for a date range."""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if not start_date or not end_date:
                return jsonify({'error': 'start_date and end_date are required'}), 400
            
            data = db.export_data(start_date, end_date)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config')
    def get_config():
        """Get current configuration."""
        return jsonify(config.settings)
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """Update configuration."""
        try:
            data = request.json
            for key, value in data.items():
                config.set(key, value)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tracking/status')
    def get_tracking_status():
        """Get tracking status."""
        from window_tracker import activity_tracker
        
        is_tracking = activity_tracker.is_tracking()
        current_window = activity_tracker.get_current_window()
        
        return jsonify({
            'tracking': is_tracking,
            'current_window': current_window
        })
    
    @app.route('/api/tracking/session-time')
    def get_session_time():
        """Get current session time."""
        from window_tracker import activity_tracker
        
        # Get session start time from activity tracker
        session_start = getattr(activity_tracker, 'session_start_time', None)
        
        if session_start and activity_tracker.is_tracking():
            from datetime import datetime
            current_time = datetime.now()
            session_duration = (current_time - session_start).total_seconds()
            
            hours = int(session_duration // 3600)
            minutes = int((session_duration % 3600) // 60)
            seconds = int(session_duration % 60)
            
            return jsonify({
                'session_duration': session_duration,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'formatted': f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            })
        else:
            return jsonify({
                'session_duration': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0,
                'formatted': "00:00:00"
            })
    
    @app.route('/api/tracking/toggle', methods=['POST'])
    def toggle_tracking():
        """Toggle tracking on/off."""
        try:
            from window_tracker import activity_tracker
            
            if activity_tracker.is_tracking():
                activity_tracker.pause_tracking()
                config.set('tracking_enabled', False)
                return jsonify({'tracking': False, 'message': 'Tracking paused'})
            else:
                activity_tracker.resume_tracking()
                config.set('tracking_enabled', True)
                return jsonify({'tracking': True, 'message': 'Tracking resumed'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/data/reset', methods=['POST'])
    def reset_data():
        """Reset all data."""
        try:
            db.reset_all_data()
            return jsonify({'success': True, 'message': 'All data has been reset successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/enhanced/stats')
    def get_enhanced_stats():
        """Get enhanced statistics including productivity and activity patterns."""
        try:
            days = request.args.get('days', 7, type=int)
            stats = db.get_enhanced_stats(days=days)
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/enhanced/browser-activity')
    def get_browser_activity():
        """Get browser activity with URLs."""
        try:
            days = request.args.get('days', 7, type=int)
            activity = db.get_browser_activity(days=days)
            return jsonify(activity)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/enhanced/productivity-trends')
    def get_productivity_trends():
        """Get productivity trends over time."""
        try:
            days = request.args.get('days', 30, type=int)
            trends = db.get_productivity_trends(days=days)
            return jsonify(trends)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/enhanced/activity-intensity')
    def get_activity_intensity():
        """Get current activity intensity."""
        try:
            from activity_monitor import enhanced_activity_tracker
            intensity = enhanced_activity_tracker.get_activity_intensity()
            is_idle = enhanced_activity_tracker.is_user_idle()
            return jsonify({
                'intensity': intensity,
                'is_idle': is_idle
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/session/current')
    def get_current_session():
        """Get current session information."""
        try:
            from window_tracker import activity_tracker
            session_stats = activity_tracker.get_session_stats()
            return jsonify(session_stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/session/focus')
    def get_focus_sessions():
        """Get recent focus sessions."""
        try:
            from window_tracker import activity_tracker
            days = request.args.get('days', 7, type=int)
            focus_sessions = activity_tracker.get_focus_sessions(days=days)
            
            # Convert datetime objects to strings for JSON serialization
            serialized_sessions = []
            for session in focus_sessions:
                serialized_sessions.append({
                    'start_time': session['start_time'].isoformat(),
                    'end_time': session['end_time'].isoformat(),
                    'duration': session['duration'],
                    'app_name': session['app_name'],
                    'window_title': session['window_title'],
                    'activity_count': session['activity_count'],
                    'idle_time': session['idle_time']
                })
            
            return jsonify(serialized_sessions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Create templates directory and HTML templates
    create_templates()
    
    return app

def create_templates():
    """Create the HTML templates for the dashboard."""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Create the main dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local Activity Watcher</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #e74c3c;
        }
        
        .status-indicator.active {
            background-color: #27ae60;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .stat-item:last-child {
            border-bottom: none;
        }
        
        .stat-value {
            font-weight: bold;
            color: #3498db;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        
        .btn-primary {
            background-color: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #2980b9;
        }
        
        .btn-success {
            background-color: #27ae60;
            color: white;
        }
        
        .btn-success:hover {
            background-color: #229954;
        }
        
        .btn-warning {
            background-color: #f39c12;
            color: white;
        }
        
        .btn-warning:hover {
            background-color: #e67e22;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
        }
        
        .error {
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .current-window {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }
        
        .time-display {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            padding: 20px;
        }
        
        .session-stats {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ecf0f1;
        }
        
        .intensity-bar {
            width: 100%;
            height: 20px;
            background-color: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .intensity-fill {
            height: 100%;
            background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Local Activity Watcher</h1>
            <div class="status">
                <div class="status-indicator" id="status-indicator"></div>
                <span id="status-text">Loading...</span>
            </div>
            <div class="current-window" id="current-window" style="display: none;"></div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Today's Usage</h2>
                <div class="time-display" id="today-time">Loading...</div>
                <div id="today-apps"></div>
            </div>
            
            <div class="card">
                <h2>Current Session</h2>
                <div id="current-session">Loading...</div>
                <div class="session-stats" id="session-stats"></div>
            </div>
            
            <div class="card">
                <h2>Productivity Metrics</h2>
                <div id="productivity-metrics">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Top Applications (7 days)</h2>
                <div id="top-apps">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Activity Intensity</h2>
                <div id="activity-intensity">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Weekly Overview</h2>
                <div id="weekly-stats">Loading...</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="toggleTracking()">Toggle Tracking</button>
            <button class="btn btn-success" onclick="refreshData()">Refresh Data</button>
            <button class="btn btn-warning" onclick="showSettings()">Settings</button>
        </div>
    </div>

    <script>
        let trackingStatus = false;
        
        function formatTime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            
            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }
        
        function updateStatus() {
            fetch('/api/tracking/status')
                .then(response => response.json())
                .then(data => {
                    trackingStatus = data.tracking;
                    const indicator = document.getElementById('status-indicator');
                    const statusText = document.getElementById('status-text');
                    const currentWindow = document.getElementById('current-window');
                    
                    if (data.tracking) {
                        indicator.classList.add('active');
                        statusText.textContent = 'Tracking Active';
                        
                        if (data.current_window) {
                            const [appName, windowTitle] = data.current_window;
                            currentWindow.innerHTML = `<strong>Current:</strong> ${appName} - ${windowTitle}`;
                            currentWindow.style.display = 'block';
                        }
                    } else {
                        indicator.classList.remove('active');
                        statusText.textContent = 'Tracking Paused';
                        currentWindow.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error updating status:', error);
                });
        }
        
        function loadTodayStats() {
            fetch('/api/stats/today')
                .then(response => response.json())
                .then(data => {
                    const timeDisplay = document.getElementById('today-time');
                    timeDisplay.textContent = formatTime(data.total_time || 0);
                    
                    const appsDiv = document.getElementById('today-apps');
                    if (data.app_breakdown && data.app_breakdown.length > 0) {
                        appsDiv.innerHTML = data.app_breakdown.slice(0, 5).map(app => 
                            `<div class="stat-item">
                                <span>${app.app_name}</span>
                                <span class="stat-value">${formatTime(app.duration)}</span>
                            </div>`
                        ).join('');
                    } else {
                        appsDiv.innerHTML = '<div class="loading">No data available</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading today stats:', error);
                    document.getElementById('today-time').textContent = 'Error';
                });
        }
        
        function loadTopApps() {
            fetch('/api/apps/top?days=7&limit=10')
                .then(response => response.json())
                .then(data => {
                    const appsDiv = document.getElementById('top-apps');
                    if (data.length > 0) {
                        appsDiv.innerHTML = data.map(app => 
                            `<div class="stat-item">
                                <span>${app.app_name}</span>
                                <span class="stat-value">${formatTime(app.total_duration)}</span>
                            </div>`
                        ).join('');
                    } else {
                        appsDiv.innerHTML = '<div class="loading">No data available</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading top apps:', error);
                });
        }
        
        function loadWeeklyStats() {
            fetch('/api/stats/weekly')
                .then(response => response.json())
                .then(data => {
                    const statsDiv = document.getElementById('weekly-stats');
                    if (data.length > 0) {
                        const totalWeekTime = data.reduce((sum, day) => sum + (day.total_time || 0), 0);
                        
                        statsDiv.innerHTML = `
                            <div class="stat-item">
                                <span>Total Week Time</span>
                                <span class="stat-value">${formatTime(totalWeekTime)}</span>
                            </div>
                            <div class="stat-item">
                                <span>Average Daily</span>
                                <span class="stat-value">${formatTime(Math.round(totalWeekTime / 7))}</span>
                            </div>
                        `;
                    } else {
                        statsDiv.innerHTML = '<div class="loading">No data available</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading weekly stats:', error);
                });
        }
        
        function loadCurrentSession() {
            fetch('/api/session/current')
                .then(response => response.json())
                .then(data => {
                    const sessionDiv = document.getElementById('current-session');
                    const statsDiv = document.getElementById('session-stats');
                    
                    if (data && data.app_name) {
                        sessionDiv.innerHTML = `
                            <div class="stat-item">
                                <span>Application</span>
                                <span class="stat-value">${data.app_name}</span>
                            </div>
                            <div class="stat-item">
                                <span>Duration</span>
                                <span class="stat-value">${formatTime(data.duration)}</span>
                            </div>
                        `;
                        
                        statsDiv.innerHTML = `
                            <div class="stat-item">
                                <span>Activity Count</span>
                                <span class="stat-value">${data.activity_count}</span>
                            </div>
                            <div class="stat-item">
                                <span>Focus Session</span>
                                <span class="stat-value">${data.is_focus_session ? 'Yes' : 'No'}</span>
                            </div>
                        `;
                    } else {
                        sessionDiv.innerHTML = '<div class="loading">No active session</div>';
                        statsDiv.innerHTML = '';
                    }
                })
                .catch(error => {
                    console.error('Error loading current session:', error);
                });
        }
        
        function loadProductivityMetrics() {
            fetch('/api/enhanced/stats?days=7')
                .then(response => response.json())
                .then(data => {
                    const metricsDiv = document.getElementById('productivity-metrics');
                    
                    if (data.productivity_stats) {
                        const stats = data.productivity_stats;
                        const activeTime = stats.active_time || 0;
                        const idleTime = stats.idle_time || 0;
                        const totalTime = activeTime + idleTime;
                        const idlePercentage = totalTime > 0 ? (idleTime / totalTime * 100).toFixed(1) : 0;
                        
                        metricsDiv.innerHTML = `
                            <div class="stat-item">
                                <span>Productivity Score</span>
                                <span class="stat-value">${(stats.avg_productivity * 100).toFixed(0)}%</span>
                            </div>
                            <div class="stat-item">
                                <span>Activity Intensity</span>
                                <span class="stat-value">${(stats.avg_intensity * 100).toFixed(0)}%</span>
                            </div>
                            <div class="stat-item">
                                <span>Active Time</span>
                                <span class="stat-value">${formatTime(activeTime)}</span>
                            </div>
                            <div class="stat-item">
                                <span>Idle Time</span>
                                <span class="stat-value">${idlePercentage}%</span>
                            </div>
                        `;
                    } else {
                        metricsDiv.innerHTML = '<div class="loading">No productivity data</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading productivity metrics:', error);
                });
        }
        
        function loadActivityIntensity() {
            fetch('/api/enhanced/activity-intensity')
                .then(response => response.json())
                .then(data => {
                    const intensityDiv = document.getElementById('activity-intensity');
                    
                    const intensityPercent = (data.intensity * 100).toFixed(0);
                    const statusText = data.is_idle ? 'Idle' : 'Active';
                    const statusColor = data.is_idle ? '#e74c3c' : '#27ae60';
                    
                    intensityDiv.innerHTML = `
                        <div class="stat-item">
                            <span>Current Intensity</span>
                            <span class="stat-value">${intensityPercent}%</span>
                        </div>
                        <div class="stat-item">
                            <span>Status</span>
                            <span class="stat-value" style="color: ${statusColor};">${statusText}</span>
                        </div>
                    `;
                })
                .catch(error => {
                    console.error('Error loading activity intensity:', error);
                });
        }
        
        function toggleTracking() {
            fetch('/api/tracking/toggle', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        updateStatus();
                        setTimeout(loadTodayStats, 1000); // Refresh stats after a delay
                    }
                })
                .catch(error => {
                    console.error('Error toggling tracking:', error);
                    alert('Error toggling tracking');
                });
        }
        
        function refreshData() {
            updateStatus();
            loadTodayStats();
            loadCurrentSession();
            loadProductivityMetrics();
            loadTopApps();
            loadActivityIntensity();
            loadWeeklyStats();
        }
        
        function showSettings() {
            alert('Settings functionality would be implemented here');
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000) 