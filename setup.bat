@echo off
REM FileBrowser Monitor - Quick Start Script for Windows

echo.
echo ======================================
echo FileBrowser Monitor - Setup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python found: 
python --version

REM Install dependencies
echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create config if it doesn't exist
if not exist config.json (
    echo.
    echo [3/4] Creating configuration file...
    python -c "from monitor import create_config_template; create_config_template('config.json')"
    echo.
    echo Configuration file created: config.json
    echo.
    echo IMPORTANT: Edit config.json with your settings:
    echo   - FileBrowser URL, username, password
    echo   - Discord webhook URL
    echo.
    echo Then run this script again to set up the scheduled task.
    pause
    exit /b 0
) else (
    echo [3/4] Configuration file found: config.json
)

REM Test the configuration
echo.
echo [4/4] Testing configuration...
python monitor.py --once
if errorlevel 1 (
    echo.
    echo ERROR: Configuration test failed
    echo Please check your config.json and make sure:
    echo   - FileBrowser is running and accessible
    echo   - Credentials are correct
    echo   - Discord webhook URL is valid
    pause
    exit /b 1
)

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo The monitor is configured and working.
echo.
echo Choose your next steps:
echo.
echo Option 1: Run manually each time
echo   python monitor.py
echo.
echo Option 2: Set up Windows Task Scheduler (recommended)
echo   Right-click setup_scheduler.ps1 and select "Run with PowerShell"
echo   (Or run: powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1)
echo.
echo Option 3: Run in Docker
echo   docker-compose up -d
echo.
pause
