#!/usr/bin/env python3
"""
Local Activity Watcher - Main Application Entry Point

A privacy-focused desktop application that tracks screen time usage
across applications locally without sending any data externally.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import modules with fallback handling
try:
    # Try direct imports (when run from src directory or through run.py)
    from config import config
    from database import db
    from window_tracker import activity_tracker
    from web_dashboard import create_app
    from reports import report_generator
    
    # Try to import system tray, but don't fail if display is not available
    try:
        from system_tray import SystemTrayApp
        SYSTEM_TRAY_AVAILABLE = True
    except Exception as e:
        SystemTrayApp = None
        SYSTEM_TRAY_AVAILABLE = False
        print(f"System tray not available: {e}")
        
except ImportError as e:
    # If that fails, try relative imports
    try:
        from .config import config
        from .database import db
        from .window_tracker import activity_tracker
        from .web_dashboard import create_app
        from .reports import report_generator
        
        try:
            from .system_tray import SystemTrayApp
            SYSTEM_TRAY_AVAILABLE = True
        except Exception as e:
            SystemTrayApp = None
            SYSTEM_TRAY_AVAILABLE = False
            print(f"System tray not available: {e}")
    except ImportError:
        print(f"Failed to import modules: {e}")
        print("Make sure you're running from the correct directory or use run.py")
        sys.exit(1)

def setup_logging():
    """Setup application logging."""
    log_level = logging.DEBUG if config.get('debug', False) else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.data_dir / 'activity_watcher.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import pystray
    except ImportError:
        missing_deps.append('pystray')
    except Exception as e:
        # pystray is available but can't initialize (e.g., no display)
        print(f"Warning: pystray available but not functional: {e}")
    
    try:
        import flask
    except ImportError:
        missing_deps.append('flask')
    
    try:
        import psutil
    except ImportError:
        missing_deps.append('psutil')
    
    # Check platform-specific dependencies
    import platform
    system = platform.system()
    
    if system == "Windows":
        try:
            import win32gui
        except ImportError:
            missing_deps.append('pywin32')
    elif system == "Darwin":
        try:
            from Cocoa import NSWorkspace
        except ImportError:
            missing_deps.append('pyobjc')
    elif system == "Linux":
        try:
            from Xlib import display
        except ImportError:
            missing_deps.append('python-xlib')
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    return True

def run_cli_mode(args):
    """Run in CLI mode for debugging or reporting."""
    logger = logging.getLogger(__name__)
    
    if args.command == 'test':
        logger.info("Testing window tracking...")
        current_window = activity_tracker.get_current_window()
        if current_window:
            app_name, window_title = current_window
            print(f"Current window: {app_name} - {window_title}")
        else:
            print("No active window detected")
    
    elif args.command == 'report':
        logger.info("Generating report...")
        report_type = args.type or 'daily'
        try:
            report_json = report_generator.export_report(report_type, **vars(args))
            print(report_json)
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            print(f"Error: {e}")
    
    elif args.command == 'stats':
        logger.info("Showing statistics...")
        try:
            today_stats = db.get_daily_stats()
            total_time = today_stats.get('total_time', 0)
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            print(f"Today's screen time: {hours}h {minutes}m")
            
            top_apps = db.get_top_apps(days=1, limit=5)
            print("\nTop applications today:")
            for i, app in enumerate(top_apps, 1):
                app_hours = app['total_duration'] // 3600
                app_minutes = (app['total_duration'] % 3600) // 60
                print(f"{i}. {app['app_name']}: {app_hours}h {app_minutes}m")
            
            # Show enhanced stats if available
            if config.get('enhanced_tracking', True):
                try:
                    enhanced_stats = db.get_enhanced_stats(days=1)
                    productivity_stats = enhanced_stats.get('productivity_stats', {})
                    
                    print(f"\nEnhanced Statistics:")
                    print(f"Average Productivity Score: {productivity_stats.get('avg_productivity', 0):.2f}")
                    print(f"Average Activity Intensity: {productivity_stats.get('avg_intensity', 0):.2f}")
                    
                    active_time = productivity_stats.get('active_time', 0)
                    idle_time = productivity_stats.get('idle_time', 0)
                    if active_time > 0 or idle_time > 0:
                        total_tracked = active_time + idle_time
                        idle_percentage = (idle_time / total_tracked) * 100 if total_tracked > 0 else 0
                        print(f"Idle Time: {idle_percentage:.1f}%")
                    
                    category_breakdown = enhanced_stats.get('category_breakdown', [])
                    if category_breakdown:
                        print(f"\nActivity Categories:")
                        for cat in category_breakdown[:5]:
                            cat_hours = cat['total_duration'] // 3600
                            cat_minutes = (cat['total_duration'] % 3600) // 60
                            print(f"  {cat['category']}: {cat_hours}h {cat_minutes}m")
                    
                except Exception as e:
                    logger.debug(f"Enhanced stats not available: {e}")
                    
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            print(f"Error: {e}")
    
    elif args.command == 'cleanup':
        logger.info("Cleaning up old data...")
        try:
            days_to_keep = args.days or 90
            db.cleanup_old_data(days_to_keep)
            print(f"Cleaned up data older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            print(f"Error: {e}")
    
    elif args.command == 'enhanced':
        logger.info("Showing enhanced statistics...")
        try:
            days = args.days or 7
            enhanced_stats = db.get_enhanced_stats(days=days)
            
            print(f"Enhanced Statistics (Last {days} days)")
            print("=" * 50)
            
            # Productivity stats
            productivity_stats = enhanced_stats.get('productivity_stats', {})
            print(f"Average Productivity Score: {productivity_stats.get('avg_productivity', 0):.2f}")
            print(f"Average Activity Intensity: {productivity_stats.get('avg_intensity', 0):.2f}")
            
            active_time = productivity_stats.get('active_time', 0)
            idle_time = productivity_stats.get('idle_time', 0)
            if active_time > 0 or idle_time > 0:
                total_tracked = active_time + idle_time
                idle_percentage = (idle_time / total_tracked) * 100 if total_tracked > 0 else 0
                active_hours = active_time // 3600
                active_minutes = (active_time % 3600) // 60
                print(f"Active Time: {active_hours}h {active_minutes}m")
                print(f"Idle Time: {idle_percentage:.1f}%")
            
            # Category breakdown
            category_breakdown = enhanced_stats.get('category_breakdown', [])
            if category_breakdown:
                print(f"\nActivity Categories:")
                for cat in category_breakdown:
                    cat_hours = cat['total_duration'] // 3600
                    cat_minutes = (cat['total_duration'] % 3600) // 60
                    print(f"  {cat['category']:15}: {cat_hours}h {cat_minutes}m (avg productivity: {cat['avg_productivity']:.2f})")
            
            # Resource usage
            resource_usage = enhanced_stats.get('resource_usage', [])
            if resource_usage:
                print(f"\nTop Resource Usage:")
                for res in resource_usage[:5]:
                    res_hours = res['total_duration'] // 3600
                    res_minutes = (res['total_duration'] % 3600) // 60
                    print(f"  {res['app_name']:15}: {res_hours}h {res_minutes}m (CPU: {res['avg_cpu']:.1f}%, RAM: {res['avg_memory']:.1f}%)")
            
            # Browser activity
            if args.show_browser:
                browser_activity = db.get_browser_activity(days=days)
                if browser_activity:
                    print(f"\nBrowser Activity:")
                    for activity in browser_activity[:10]:
                        duration_minutes = activity['duration'] // 60
                        print(f"  {activity['url'][:50]}... ({duration_minutes}m)")
            
            # Productivity trends
            if args.show_trends:
                trends = db.get_productivity_trends(days=days)
                if trends:
                    print(f"\nProductivity Trends:")
                    for trend in trends:
                        print(f"  {trend['date']}: {trend['productivity']:.2f} (intensity: {trend['intensity']:.2f})")
            
        except Exception as e:
            logger.error(f"Error showing enhanced stats: {e}")
            print(f"Error: {e}")
    
    elif args.command == 'web':
        logger.info("Starting web dashboard...")
        try:
            app = create_app()
            port = config.get('web_port', 5000)
            print(f"Starting web dashboard on http://localhost:{port}")
            app.run(host='127.0.0.1', port=port, debug=args.debug)
        except Exception as e:
            logger.error(f"Error starting web dashboard: {e}")
            print(f"Error: {e}")

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='Local Activity Watcher')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config-dir', help='Custom config directory')
    parser.add_argument('--no-tray', action='store_true', help='Disable system tray')
    
    # CLI commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test window tracking')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('--type', choices=['daily', 'weekly', 'monthly', 'app'], 
                              default='daily', help='Report type')
    report_parser.add_argument('--date', help='Date for daily report (YYYY-MM-DD)')
    report_parser.add_argument('--app-name', help='Application name for app report')
    report_parser.add_argument('--days', type=int, default=7, help='Number of days for report')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show quick statistics')
    
    # Enhanced stats command
    enhanced_parser = subparsers.add_parser('enhanced', help='Show enhanced statistics and productivity metrics')
    enhanced_parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
    enhanced_parser.add_argument('--show-browser', action='store_true', help='Show browser activity')
    enhanced_parser.add_argument('--show-trends', action='store_true', help='Show productivity trends')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, default=90, 
                               help='Keep data for this many days')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web dashboard only')
    web_parser.add_argument('--port', type=int, help='Port for web dashboard')
    
    args = parser.parse_args()
    
    # Setup configuration
    if args.config_dir:
        config.data_dir = Path(args.config_dir)
        config.data_dir.mkdir(exist_ok=True)
        config.db_file = config.data_dir / "activity.db"
        config.config_file = config.data_dir / "config.json"
    
    if args.debug:
        config.set('debug', True)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Local Activity Watcher v{config.version}")
    logger.info(f"Data directory: {config.data_dir}")
    logger.info(f"Database file: {config.db_file}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database
    try:
        db.init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Handle CLI commands
    if args.command:
        run_cli_mode(args)
        return
    
    # Default: Run system tray application
    if args.no_tray:
        logger.info("System tray disabled, running tracking only")
        try:
            activity_tracker.start_tracking(config.get('tracking_interval', 5))
            logger.info("Activity tracking started")
            
            # Keep the application running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            activity_tracker.stop_tracking()
    else:
        if SYSTEM_TRAY_AVAILABLE:
            logger.info("Starting system tray application")
            try:
                app = SystemTrayApp()
                app.run()
            except Exception as e:
                logger.error(f"System tray application error: {e}")
                sys.exit(1)
        else:
            logger.warning("System tray not available, running tracking only")
            try:
                activity_tracker.start_tracking(config.get('tracking_interval', 5))
                logger.info("Activity tracking started")
                
                # Keep the application running
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                activity_tracker.stop_tracking()

if __name__ == "__main__":
    main() 