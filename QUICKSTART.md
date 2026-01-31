# Quick Start Guide

Get FileBrowser Monitor running in 5 minutes!

## Prerequisites

- Python 3.8+
- FileBrowser v2+ running and accessible
- Discord server with webhook permissions

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/filebrowser-notifs.git
cd filebrowser-notifs
```

## 2. Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

## 3. Install Dependencies

**Important:** Make sure your virtual environment is activated (you should see `(venv)` in your prompt).

```bash
# Use python -m pip to ensure it installs to the venv
python -m pip install -r requirements.txt
```

**Troubleshooting:** If you see "Defaulting to user installation" or later get "ModuleNotFoundError", try:
```bash
# Deactivate and reactivate the virtual environment
deactivate
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Then install again
python -m pip install -r requirements.txt
```

## 4. Get Discord Webhook

1. Open Discord → Server → Settings → Integrations → Webhooks
2. New Webhook → Give it a name like "FileBrowser Monitor"
3. Copy the webhook URL
4. Keep it safe!

## 5. Initialize Config

**Note:** Ensure your virtual environment is still activated.

```bash
python monitor.py --init-config
```

## 6. Edit config.json

```bash
# On Windows
notepad config.json

# On Linux/macOS
nano config.json
```

Fill in:
- `filebrowser.url` - Your FileBrowser address (e.g., http://localhost:8080)
- `filebrowser.username` - Admin username
- `filebrowser.password` - Admin password
- `discord.webhook_url` - The Discord webhook URL from step 3

**Note:** Ensure your virtual environment is still activated.

## 7. Test It

```bash
python monitor.py --once
```

You should see:
1. FileBrowser connection success
2. Files being scanned
3. A Discord notification appears

## 8. Set Up Scheduling

### Option A: Windows (Easiest)

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\setup_scheduler.ps1
```

### Option B: Linux/macOS Cron

```bash
crontab -e
```

Add this line:
```
*/30 * * * * cd /path/to/filebrowser-notifs && python monitor.py >> monitor.log 2>&1
```

### Option C: Docker

```bash
docker-compose up -d
```

### Option D: Systemd (Linux)

```bash
sudo cp filebrowser-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable filebrowser-monitor
sudo systemctl start filebrowser-monitor
```

## Done! 🎉

FileBrowser Monitor is now running and will check every 30 minutes for new files!

## Next Steps

- Check logs: `tail -f monitor.log`
- Adjust interval in `config.json` under `monitoring.interval_minutes`
- Add files to FileBrowser and confirm Discord notification
- Read [INSTALL.md](INSTALL.md) for advanced configuration

## Troubleshooting

**"Connection refused" or "Cannot connect to FileBrowser"**
- Check FileBrowser is running: `curl http://localhost:8080/api/login` (should NOT return "Connection refused")
- Verify URL in config.json (include http:// or https://, no trailing slash)
- If using Docker, ensure the container is running: `docker ps | grep filebrowser`
- Try accessing FileBrowser in your web browser first

**"Authentication failed" or "Expected JSON response"**
- Verify the URL is correct and points to FileBrowser (not a random webpage)
- Check credentials in config.json
- Verify user is admin in FileBrowser
- Try logging into FileBrowser web UI manually with same credentials
- Ensure FileBrowser version is v2.0 or higher
- Check if FileBrowser is behind a reverse proxy that might be interfering

**"Invalid webhook URL"**
- Copy webhook URL again from Discord
- Make sure it starts with `https://discordapp.com/api/webhooks/`

**No notifications sent**
- Run `python monitor.py --once` to test
- Check Discord channel permissions
- Verify webhook URL is in config.json

**"ModuleNotFoundError: No module named 'requests'" (even with venv active)**
- Deactivate and reactivate venv: `deactivate && source venv/bin/activate`
- Install using: `python -m pip install -r requirements.txt`
- Verify correct Python: `which python` should point to venv/bin/python

## Support

See [INSTALL.md](INSTALL.md) for full troubleshooting guide.
