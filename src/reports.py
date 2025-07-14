from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from database import db

class ReportGenerator:
    """Generate various reports from activity data."""
    
    def __init__(self):
        self.db = db
    
    def generate_daily_report(self, date: str = None) -> Dict:
        """Generate a comprehensive daily report."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get basic daily stats
        daily_stats = self.db.get_daily_stats(date)
        
        # Get hourly breakdown
        hourly_breakdown = self._get_hourly_breakdown(date)
        
        # Get productivity metrics
        productivity = self._calculate_productivity_metrics(date)
        
        return {
            'date': date,
            'total_time': daily_stats.get('total_time', 0),
            'app_breakdown': daily_stats.get('app_breakdown', []),
            'hourly_breakdown': hourly_breakdown,
            'productivity': productivity,
            'summary': self._generate_daily_summary(daily_stats)
        }
    
    def generate_weekly_report(self, end_date: str = None) -> Dict:
        """Generate a comprehensive weekly report."""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        start_datetime = end_datetime - timedelta(days=6)
        
        # Get weekly stats
        weekly_stats = self.db.get_weekly_stats()
        
        # Calculate totals and averages
        total_time = sum(day.get('total_time', 0) for day in weekly_stats)
        avg_daily_time = total_time / 7 if total_time > 0 else 0
        
        # Get top apps for the week
        top_apps = self.db.get_top_apps(days=7, limit=10)
        
        # Calculate trends
        trends = self._calculate_weekly_trends(weekly_stats)
        
        return {
            'start_date': start_datetime.strftime('%Y-%m-%d'),
            'end_date': end_date,
            'total_time': total_time,
            'avg_daily_time': avg_daily_time,
            'daily_breakdown': weekly_stats,
            'top_apps': top_apps,
            'trends': trends,
            'summary': self._generate_weekly_summary(weekly_stats, total_time)
        }
    
    def generate_monthly_report(self, month: str = None) -> Dict:
        """Generate a comprehensive monthly report."""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        year, month_num = map(int, month.split('-'))
        
        # Get all days in the month
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
        
        # Collect daily stats for the month
        daily_stats = []
        current_date = start_date
        total_time = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_stats = self.db.get_daily_stats(date_str)
            daily_stats.append(day_stats)
            total_time += day_stats.get('total_time', 0)
            current_date += timedelta(days=1)
        
        # Get top apps for the month
        days_in_month = (end_date - start_date).days + 1
        top_apps = self.db.get_top_apps(days=days_in_month, limit=15)
        
        # Calculate monthly trends
        monthly_trends = self._calculate_monthly_trends(daily_stats)
        
        return {
            'month': month,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_time': total_time,
            'avg_daily_time': total_time / days_in_month if total_time > 0 else 0,
            'daily_breakdown': daily_stats,
            'top_apps': top_apps,
            'trends': monthly_trends,
            'summary': self._generate_monthly_summary(daily_stats, total_time)
        }
    
    def generate_app_report(self, app_name: str, days: int = 7) -> Dict:
        """Generate a detailed report for a specific application."""
        # Get app usage statistics
        app_stats = self.db.get_app_stats(days)
        app_data = next((app for app in app_stats if app['app_name'] == app_name), None)
        
        if not app_data:
            return {
                'app_name': app_name,
                'error': 'No data found for this application'
            }
        
        # Get window titles for this app
        window_titles = self.db.get_window_titles(app_name, days)
        
        # Calculate usage patterns
        usage_patterns = self._calculate_app_usage_patterns(app_name, days)
        
        return {
            'app_name': app_name,
            'total_duration': app_data['total_duration'],
            'session_count': app_data['session_count'],
            'avg_session_duration': app_data['avg_duration'],
            'window_titles': window_titles,
            'usage_patterns': usage_patterns,
            'summary': self._generate_app_summary(app_data, window_titles)
        }
    
    def _get_hourly_breakdown(self, date: str) -> List[Dict]:
        """Get hourly breakdown of usage for a specific date."""
        # This would require more detailed database queries
        # For now, return a placeholder
        return [{'hour': i, 'usage': 0} for i in range(24)]
    
    def _calculate_productivity_metrics(self, date: str) -> Dict:
        """Calculate productivity metrics for a date."""
        daily_stats = self.db.get_daily_stats(date)
        apps = daily_stats.get('app_breakdown', [])
        
        # Define productivity categories (can be configured)
        productive_apps = ['code.exe', 'notepad.exe', 'word.exe', 'excel.exe', 'powerpoint.exe']
        neutral_apps = ['explorer.exe', 'file_manager']
        distracting_apps = ['chrome.exe', 'firefox.exe', 'games', 'steam.exe']
        
        productive_time = 0
        neutral_time = 0
        distracting_time = 0
        
        for app in apps:
            app_name = app['app_name'].lower()
            duration = app['duration']
            
            if any(prod_app in app_name for prod_app in productive_apps):
                productive_time += duration
            elif any(dist_app in app_name for dist_app in distracting_apps):
                distracting_time += duration
            else:
                neutral_time += duration
        
        total_time = productive_time + neutral_time + distracting_time
        
        return {
            'productive_time': productive_time,
            'neutral_time': neutral_time,
            'distracting_time': distracting_time,
            'productivity_score': (productive_time / total_time * 100) if total_time > 0 else 0
        }
    
    def _calculate_weekly_trends(self, weekly_stats: List[Dict]) -> Dict:
        """Calculate weekly trends."""
        if len(weekly_stats) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate average usage for first vs second half of week
        first_half = weekly_stats[:3]
        second_half = weekly_stats[4:]
        
        first_half_avg = sum(day.get('total_time', 0) for day in first_half) / len(first_half)
        second_half_avg = sum(day.get('total_time', 0) for day in second_half) / len(second_half)
        
        if second_half_avg > first_half_avg:
            trend = 'increasing'
        elif second_half_avg < first_half_avg:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'change_percentage': ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
        }
    
    def _calculate_monthly_trends(self, daily_stats: List[Dict]) -> Dict:
        """Calculate monthly trends."""
        if len(daily_stats) < 7:
            return {'trend': 'insufficient_data'}
        
        # Calculate weekly averages
        weekly_averages = []
        for i in range(0, len(daily_stats), 7):
            week_data = daily_stats[i:i+7]
            week_avg = sum(day.get('total_time', 0) for day in week_data) / len(week_data)
            weekly_averages.append(week_avg)
        
        # Determine trend
        if len(weekly_averages) >= 2:
            if weekly_averages[-1] > weekly_averages[0]:
                trend = 'increasing'
            elif weekly_averages[-1] < weekly_averages[0]:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'weekly_averages': weekly_averages
        }
    
    def _calculate_app_usage_patterns(self, app_name: str, days: int) -> Dict:
        """Calculate usage patterns for an app."""
        # This would require more detailed analysis
        # For now, return basic patterns
        return {
            'peak_hours': [9, 10, 11, 14, 15, 16],  # Common work hours
            'usage_frequency': 'daily',
            'session_pattern': 'regular'
        }
    
    def _generate_daily_summary(self, daily_stats: Dict) -> str:
        """Generate a human-readable daily summary."""
        total_time = daily_stats.get('total_time', 0)
        apps = daily_stats.get('app_breakdown', [])
        
        if total_time == 0:
            return "No activity recorded for this day."
        
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        
        top_app = apps[0]['app_name'] if apps else 'Unknown'
        
        return f"Total screen time: {hours}h {minutes}m. Most used app: {top_app}."
    
    def _generate_weekly_summary(self, weekly_stats: List[Dict], total_time: int) -> str:
        """Generate a human-readable weekly summary."""
        if total_time == 0:
            return "No activity recorded for this week."
        
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        avg_daily_hours = hours / 7
        
        return f"Total screen time: {hours}h {minutes}m. Average daily: {avg_daily_hours:.1f}h."
    
    def _generate_monthly_summary(self, daily_stats: List[Dict], total_time: int) -> str:
        """Generate a human-readable monthly summary."""
        if total_time == 0:
            return "No activity recorded for this month."
        
        hours = total_time // 3600
        days_with_activity = sum(1 for day in daily_stats if day.get('total_time', 0) > 0)
        
        return f"Total screen time: {hours}h across {days_with_activity} active days."
    
    def _generate_app_summary(self, app_data: Dict, window_titles: List[Dict]) -> str:
        """Generate a human-readable app summary."""
        total_duration = app_data['total_duration']
        session_count = app_data['session_count']
        
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        
        return f"Used for {hours}h {minutes}m across {session_count} sessions."
    
    def export_report(self, report_type: str, **kwargs) -> str:
        """Export a report to JSON format."""
        if report_type == 'daily':
            report = self.generate_daily_report(kwargs.get('date'))
        elif report_type == 'weekly':
            report = self.generate_weekly_report(kwargs.get('end_date'))
        elif report_type == 'monthly':
            report = self.generate_monthly_report(kwargs.get('month'))
        elif report_type == 'app':
            report = self.generate_app_report(kwargs.get('app_name'), kwargs.get('days', 7))
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        return json.dumps(report, indent=2, default=str)

# Global report generator instance
report_generator = ReportGenerator() 