#!/usr/bin/env python3
"""
Build script for Local Activity Watcher using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_spec_file():
    """Create PyInstaller spec file."""
    system = platform.system()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Platform-specific hidden imports
hidden_imports = [
    'pystray',
    'PIL',
    'flask',
    'flask_cors',
    'psutil',
    'apscheduler',
    'sqlite3',
    'json',
    'threading',
    'webbrowser',
    'datetime',
    'pathlib',
]

# Add platform-specific imports
import platform
if platform.system() == "Windows":
    hidden_imports.extend([
        'win32gui',
        'win32process',
        'win32api',
        'win32con',
        'pywintypes',
    ])
elif platform.system() == "Darwin":
    hidden_imports.extend([
        'Cocoa',
        'Quartz',
        'Foundation',
        'AppKit',
    ])
elif platform.system() == "Linux":
    hidden_imports.extend([
        'Xlib',
        'Xlib.display',
        'Xlib.error',
    ])

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/templates', 'templates'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LocalActivityWatcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if platform.system() == "Windows" else None,
)
'''
    
    with open('LocalActivityWatcher.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")

def create_icon():
    """Create a simple icon for the application."""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        img = Image.new('RGB', (256, 256), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple circle
        draw.ellipse([50, 50, 206, 206], fill='blue', outline='darkblue', width=4)
        
        # Add text
        draw.text((110, 120), "AW", fill='white', anchor='mm')
        
        # Save as ICO for Windows
        if platform.system() == "Windows":
            img.save('icon.ico', format='ICO')
            print("Created Windows icon")
        else:
            img.save('icon.png', format='PNG')
            print("Created application icon")
            
    except ImportError:
        print("PIL not available, skipping icon creation")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    
    try:
        # Use the spec file for building
        cmd = [sys.executable, '-m', 'PyInstaller', 'LocalActivityWatcher.spec', '--clean']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Build successful!")
            print("Executable location:", Path('dist') / 'LocalActivityWatcher')
        else:
            print("Build failed!")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"Build error: {e}")
        return False
    
    return True

def create_installer_script():
    """Create a simple installer script."""
    system = platform.system()
    
    if system == "Windows":
        # Create Windows batch installer
        batch_content = '''@echo off
echo Installing Local Activity Watcher...

REM Create application directory
if not exist "%APPDATA%\\LocalActivityWatcher" mkdir "%APPDATA%\\LocalActivityWatcher"

REM Copy executable
copy LocalActivityWatcher.exe "%APPDATA%\\LocalActivityWatcher\\"

REM Create desktop shortcut (optional)
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\Local Activity Watcher.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%APPDATA%\\LocalActivityWatcher\\LocalActivityWatcher.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Installation complete!
echo You can run the application from the desktop shortcut or from:
echo %APPDATA%\\LocalActivityWatcher\\LocalActivityWatcher.exe
pause
'''
        
        with open('dist/install.bat', 'w') as f:
            f.write(batch_content)
        
        print("Created Windows installer script")
    
    elif system == "Darwin":
        # Create macOS installer script
        script_content = '''#!/bin/bash
echo "Installing Local Activity Watcher..."

# Create application directory
mkdir -p "$HOME/Applications/LocalActivityWatcher"

# Copy executable
cp LocalActivityWatcher "$HOME/Applications/LocalActivityWatcher/"

# Make executable
chmod +x "$HOME/Applications/LocalActivityWatcher/LocalActivityWatcher"

# Create launch script
cat > "$HOME/Applications/LocalActivityWatcher/launch.sh" << 'EOF'
#!/bin/bash
cd "$HOME/Applications/LocalActivityWatcher"
./LocalActivityWatcher
EOF

chmod +x "$HOME/Applications/LocalActivityWatcher/launch.sh"

echo "Installation complete!"
echo "You can run the application from: $HOME/Applications/LocalActivityWatcher/LocalActivityWatcher"
'''
        
        with open('dist/install.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('dist/install.sh', 0o755)
        print("Created macOS installer script")
    
    else:  # Linux
        # Create Linux installer script
        script_content = '''#!/bin/bash
echo "Installing Local Activity Watcher..."

# Create application directory
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share/applications"

# Copy executable
cp LocalActivityWatcher "$HOME/.local/bin/"

# Make executable
chmod +x "$HOME/.local/bin/LocalActivityWatcher"

# Create desktop entry
cat > "$HOME/.local/share/applications/local-activity-watcher.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Local Activity Watcher
Comment=Privacy-focused activity tracker
Exec=$HOME/.local/bin/LocalActivityWatcher
Icon=preferences-system-privacy
Terminal=false
Categories=Utility;System;
EOF

echo "Installation complete!"
echo "You can run the application from the applications menu or command line:"
echo "$HOME/.local/bin/LocalActivityWatcher"
'''
        
        with open('dist/install.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('dist/install.sh', 0o755)
        print("Created Linux installer script")

def create_uninstaller_script():
    """Create an uninstaller script for each platform."""
    system = platform.system()
    
    if system == "Windows":
        # Create Windows batch uninstaller
        uninstall_content = '''@echo off
echo Local Activity Watcher Uninstaller
echo.
echo This will remove Local Activity Watcher from your system.
echo.
pause

echo Stopping any running instances...
taskkill /F /IM LocalActivityWatcher.exe 2>nul

echo Removing application files...
if exist "%APPDATA%\\LocalActivityWatcher" (
    rd /s /q "%APPDATA%\\LocalActivityWatcher"
    echo Application files removed.
) else (
    echo Application files not found.
)

echo Removing desktop shortcut...
if exist "%USERPROFILE%\\Desktop\\Local Activity Watcher.lnk" (
    del "%USERPROFILE%\\Desktop\\Local Activity Watcher.lnk"
    echo Desktop shortcut removed.
) else (
    echo Desktop shortcut not found.
)

echo Removing data directory...
if exist "%USERPROFILE%\\.local_activity_watcher" (
    choice /C YN /M "Do you want to remove all data (activity history, logs, etc.)? This cannot be undone"
    if errorlevel 2 goto :skip_data
    rd /s /q "%USERPROFILE%\\.local_activity_watcher"
    echo Data directory removed.
    goto :end
    :skip_data
    echo Data directory preserved.
) else (
    echo Data directory not found.
)

:end
echo.
echo Local Activity Watcher has been uninstalled.
echo Thank you for using Local Activity Watcher!
pause
'''
        
        with open('dist/uninstall.bat', 'w') as f:
            f.write(uninstall_content)
        
        print("Created Windows uninstaller script")
    
    elif system == "Darwin":
        # Create macOS uninstaller script
        uninstall_content = '''#!/bin/bash
echo "Local Activity Watcher Uninstaller"
echo "This will remove Local Activity Watcher from your system."
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo "Stopping any running instances..."
pkill -f LocalActivityWatcher 2>/dev/null

echo "Removing application files..."
if [ -d "$HOME/Applications/LocalActivityWatcher" ]; then
    rm -rf "$HOME/Applications/LocalActivityWatcher"
    echo "Application files removed."
else
    echo "Application files not found."
fi

echo "Removing data directory..."
if [ -d "$HOME/.local_activity_watcher" ]; then
    read -p "Do you want to remove all data (activity history, logs, etc.)? This cannot be undone. (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/.local_activity_watcher"
        echo "Data directory removed."
    else
        echo "Data directory preserved."
    fi
else
    echo "Data directory not found."
fi

echo
echo "Local Activity Watcher has been uninstalled."
echo "Thank you for using Local Activity Watcher!"
'''
        
        with open('dist/uninstall.sh', 'w') as f:
            f.write(uninstall_content)
        
        os.chmod('dist/uninstall.sh', 0o755)
        print("Created macOS uninstaller script")
    
    else:  # Linux
        # Create Linux uninstaller script
        uninstall_content = '''#!/bin/bash
echo "Local Activity Watcher Uninstaller"
echo "This will remove Local Activity Watcher from your system."
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo "Stopping any running instances..."
pkill -f LocalActivityWatcher 2>/dev/null

echo "Removing application files..."
if [ -f "$HOME/.local/bin/LocalActivityWatcher" ]; then
    rm -f "$HOME/.local/bin/LocalActivityWatcher"
    echo "Application executable removed."
else
    echo "Application executable not found."
fi

echo "Removing desktop entry..."
if [ -f "$HOME/.local/share/applications/local-activity-watcher.desktop" ]; then
    rm -f "$HOME/.local/share/applications/local-activity-watcher.desktop"
    echo "Desktop entry removed."
else
    echo "Desktop entry not found."
fi

echo "Removing data directory..."
if [ -d "$HOME/.local_activity_watcher" ]; then
    read -p "Do you want to remove all data (activity history, logs, etc.)? This cannot be undone. (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/.local_activity_watcher"
        echo "Data directory removed."
    else
        echo "Data directory preserved."
    fi
else
    echo "Data directory not found."
fi

echo
echo "Local Activity Watcher has been uninstalled."
echo "Thank you for using Local Activity Watcher!"
'''
        
        with open('dist/uninstall.sh', 'w') as f:
            f.write(uninstall_content)
        
        os.chmod('dist/uninstall.sh', 0o755)
        print("Created Linux uninstaller script")

def create_readme():
    """Create a README file for the built application."""
    readme_content = '''# Local Activity Watcher

A privacy-focused desktop application that tracks screen time usage across applications locally without sending any data externally.

## Installation

### Windows
1. Run `install.bat` as administrator
2. The application will be installed to `%APPDATA%\\LocalActivityWatcher`
3. A desktop shortcut will be created

### macOS
1. Run `./install.sh` in Terminal
2. The application will be installed to `~/Applications/LocalActivityWatcher`

### Linux
1. Run `./install.sh` in Terminal
2. The application will be installed to `~/.local/bin`
3. A desktop entry will be created

## Usage

### System Tray Mode (Default)
- Run the executable to start in system tray mode
- Right-click the tray icon to access controls
- Use "Pause/Resume Tracking" to control monitoring
- Use "Open Dashboard" to view statistics

### Command Line Interface
- `LocalActivityWatcher test` - Test window tracking
- `LocalActivityWatcher stats` - Show quick statistics
- `LocalActivityWatcher report --type daily` - Generate daily report
- `LocalActivityWatcher web` - Start web dashboard only
- `LocalActivityWatcher --help` - Show all options

### Web Dashboard
- Access at http://localhost:5000 (default port)
- View daily, weekly, and monthly statistics
- See top applications and time breakdowns
- Control tracking from the web interface

## Features

- **Privacy First**: All data stays on your local machine
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **System Tray**: Runs silently in the background
- **Web Dashboard**: Beautiful local web interface
- **Detailed Reports**: Daily, weekly, and monthly summaries
- **Application Tracking**: Monitor time spent in different apps
- **Window Title Tracking**: See specific windows/documents
- **Configurable**: Adjust tracking intervals and settings

## Data Storage

- Configuration: `~/.local_activity_watcher/config.json`
- Database: `~/.local_activity_watcher/activity.db`
- Logs: `~/.local_activity_watcher/activity_watcher.log`

## Privacy

This application:
- [✓] Stores all data locally on your machine
- [✓] Never sends data to external servers
- [✓] No cloud synchronization or analytics
- [✓] Open source and transparent
- [✓] You control your data completely

## Troubleshooting

1. **Application won't start**: Check the log file for errors
2. **No window tracking**: Ensure platform-specific dependencies are installed
3. **Web dashboard not loading**: Check if port 5000 is available
4. **Permission issues**: Run as administrator/root if needed

## Uninstallation

Simply delete the application directory and data folder:
- Windows: `%APPDATA%\\LocalActivityWatcher`
- macOS/Linux: `~/.local_activity_watcher`

For more information, visit the project repository.
'''
    
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created README file")

def main():
    """Main build function."""
    print("Building Local Activity Watcher...")
    print(f"Platform: {platform.system()}")
    
    # Clean previous builds
    clean_build()
    
    # Create icon
    create_icon()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        print("Build failed!")
        return 1
    
    # Create installer, uninstaller, and documentation
    create_installer_script()
    create_uninstaller_script()
    create_readme()
    
    print("\\nBuild complete!")
    print("Files created in 'dist/' directory:")
    print("- LocalActivityWatcher (executable)")
    print("- install script")
    print("- uninstall script")
    print("- README.txt")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 