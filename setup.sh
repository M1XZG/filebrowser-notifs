#!/bin/bash
# FileBrowser Monitor - Quick Start Script for Linux/macOS

set -e

echo ""
echo "======================================"
echo "FileBrowser Monitor - Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "[1/4] Python found:"
python3 --version

# Create virtual environment
echo ""
echo "[2/4] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "[3/4] Installing dependencies..."
pip install -q -r requirements.txt

# Create config if it doesn't exist
if [ ! -f "config.json" ]; then
    echo ""
    echo "[4/4] Creating configuration file..."
    python monitor.py --init-config
    echo ""
    echo "Configuration file created: config.json"
    echo ""
    echo "IMPORTANT: Edit config.json and set your:"
    echo "  - FileBrowser URL, username, password"
    echo "  - Discord webhook URL"
    echo ""
    echo "Then run: python monitor.py --once"
    exit 0
else
    echo "[4/4] Configuration file found: config.json"
fi

# Test the configuration
echo ""
echo "Testing configuration..."
python monitor.py --once
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "Setup Complete!"
    echo "======================================"
    echo ""
    echo "The monitor is configured and working."
    echo ""
    echo "Choose your next steps:"
    echo ""
    echo "Option 1: Run continuously (foreground)"
    echo "  source venv/bin/activate && python monitor.py"
    echo ""
    echo "Option 2: Set up systemd service (recommended)"
    echo "  sudo cp filebrowser-monitor.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable filebrowser-monitor"
    echo "  sudo systemctl start filebrowser-monitor"
    echo ""
    echo "Option 3: Add to crontab (every 30 minutes)"
    echo "  crontab -e"
    echo "  Add: */30 * * * * cd $PWD && venv/bin/python monitor.py >> monitor.log 2>&1"
    echo ""
    echo "Option 4: Run in Docker"
    echo "  docker-compose up -d"
    echo ""
else
    echo ""
    echo "ERROR: Configuration test failed"
    echo "Please check your config.json and make sure:"
    echo "  - FileBrowser is running and accessible"
    echo "  - Credentials are correct"
    echo "  - Discord webhook URL is valid"
    exit 1
fi
