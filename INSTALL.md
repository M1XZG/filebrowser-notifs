# Installation Guide

## Quick Start

### Windows
1. Double-click `setup.bat`
2. Follow the prompts to create your configuration
3. Set up Windows Task Scheduler when prompted

### Linux/macOS
```bash
chmod +x setup.sh
./setup.sh
```

---

## Detailed Setup Instructions

### Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **FileBrowser** - Running and accessible with admin credentials
- **Discord Webhook URL** - Set up in your Discord server

### Step 1: Get Discord Webhook URL

1. Open your Discord server
2. Go to **Settings → Integrations → Webhooks**
3. Click **New Webhook**
4. Name it: "FileBrowser Monitor"
5. Select the channel where notifications should appear
6. Click **Copy Webhook URL**
7. Keep this URL safe - you'll need it in Step 4

### Step 2: Get FileBrowser Credentials

You'll need:
- **FileBrowser URL** (e.g., `http://localhost:8080` or `http://192.168.1.100:8080`)
- **Username** (usually `admin`)
- **Password** (your admin password)

### Step 3: Install Python Dependencies

#### On Windows (Command Prompt):
```cmd
cd path\to\filebrowser-notifs
pip install -r requirements.txt
```

#### On Linux/macOS (Terminal):
```bash
cd /path/to/filebrowser-notifs
python3 -m pip install --user -r requirements.txt
```

Or use a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Create Configuration

#### Option A: Interactive Setup
```bash
python monitor.py --init-config
```
Then edit the generated `config.json` file.

#### Option B: Manual Setup
1. Copy `config.example.json` to `config.json`
2. Edit `config.json`:

```json
{
  "filebrowser": {
    "url": "http://localhost:8080",
    "username": "admin",
    "password": "your-password"
  },
  "discord": {
    "webhook_url": "https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
  },
  "monitoring": {
    "interval_minutes": 30,
    "ignore_dirs": [".git", "__pycache__", "node_modules"],
    "exclude_patterns": [".tmp", ".cache"]
  }
}
```

### Step 5: Test Configuration

```bash
python monitor.py --once
```

This will:
- Connect to FileBrowser
- Scan all files
- Send a test notification to Discord
- Exit

**Expected output:**
- No errors
- Discord receives a message with file information
- Log messages show "successfully"

If you see errors, check:
- FileBrowser is running and URL is correct
- Credentials are correct
- Discord webhook URL is valid
- Your network allows outgoing connections

### Step 6: Set Up Scheduling

Choose one of these methods to run every 30 minutes:

#### Option A: Windows Task Scheduler (Easiest)

**Method 1: PowerShell Script**
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\setup_scheduler.ps1
```

**Method 2: Manual Setup**
1. Open **Task Scheduler**
2. Create Basic Task → name it "FileBrowser Monitor"
3. Trigger: Daily → Repeat every 30 minutes
4. Action: 
   - Program: `C:\Python311\python.exe` (your Python path)
   - Arguments: `C:\path\to\monitor.py`
   - Start in: `C:\path\to\filebrowser-notifs\`

#### Option B: Linux/macOS - Cron

Edit crontab:
```bash
crontab -e
```

Add this line (runs every 30 minutes):
```
*/30 * * * * cd /path/to/filebrowser-notifs && /usr/bin/python3 monitor.py >> monitor.log 2>&1
```

Save and exit.

#### Option C: Linux/macOS - Systemd Service

1. Edit `filebrowser-monitor.service`:
   - Set `User` to your username
   - Update `WorkingDirectory` path

2. Install and start:
```bash
sudo cp filebrowser-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable filebrowser-monitor
sudo systemctl start filebrowser-monitor
```

3. Check status:
```bash
sudo systemctl status filebrowser-monitor
```

#### Option D: Docker (If you have Docker installed)

1. Update `docker-compose.yml` with your paths
2. Run:
```bash
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f filebrowser-monitor
```

---

## Configuration Reference

### FileBrowser Settings

- **url**: Base URL of your FileBrowser instance
  - Example: `http://localhost:8080`
  - Include protocol (http/https) but NOT trailing slash

- **username**: FileBrowser admin username
  - Should be an admin user for full access

- **password**: FileBrowser admin password
  - Use strong passwords
  - Consider using environment variables in production

### Discord Settings

- **webhook_url**: Your Discord webhook URL
  - Format: `https://discordapp.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN`
  - Keep this secret!
  - Never commit to version control

### Monitoring Settings

- **interval_minutes**: How often to check (default: 30)
  - Minimum: 1 minute
  - Recommended: 15-60 minutes
  - Higher = fewer API calls but slower detection

- **ignore_dirs**: Directory names to skip
  - Useful for excluding cache/build directories
  - Example: `[".git", "node_modules", "__pycache__"]`

- **exclude_patterns**: File patterns to ignore
  - Matched against file extensions
  - Example: `[".tmp", ".cache", ".swp", "~"]`

---

## Verification Checklist

After setup, verify everything works:

- [ ] Python 3.8+ is installed (`python --version`)
- [ ] Dependencies installed (`pip list | grep requests`)
- [ ] `config.json` is created
- [ ] FileBrowser URL is accessible and running
- [ ] FileBrowser credentials work
- [ ] Discord webhook URL is valid
- [ ] `python monitor.py --once` runs without errors
- [ ] Discord receives the test notification
- [ ] Scheduled task/cron job is created
- [ ] Scheduler shows the task as active

---

## First Run Notes

On the first run:
- All existing files are added to the database as "seen"
- Files uploaded AFTER the first run will be detected
- To avoid noise, run `--once` first, then enable scheduling

To reset tracking (detect all files as new):
```bash
rm file_tracker.db
python monitor.py --once
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
```

### "Connection refused" or "Cannot reach FileBrowser"
- Check FileBrowser is running
- Verify URL is correct: `curl http://your-url/api/status`
- Check firewall allows connections
- If using Docker, ensure container network is accessible

### "Authentication failed"
- Verify username is correct
- Check password is correct
- Ensure user has admin privileges
- Try logging into FileBrowser web UI manually

### "Invalid webhook URL"
- Regenerate webhook in Discord server settings
- Check URL format is complete
- Ensure webhook hasn't been deleted
- Verify Discord server hasn't moved to a different webhook endpoint

### "No changes detected" but files were added
- Check file modification time is recent (within 30 minutes)
- Verify file permissions allow reading
- Check `ignore_dirs` and `exclude_patterns` aren't filtering files
- Review database: `sqlite3 file_tracker.db "SELECT * FROM files LIMIT 5;"`

### Very high database size
Reset the database:
```bash
rm file_tracker.db
python monitor.py --once
```

### Scheduler not running
- **Windows**: Check Task Scheduler → History tab
- **Linux**: Check logs: `journalctl -u filebrowser-monitor -f`
- **Cron**: Check mail: `mail` or log file output

---

## Monitoring the Monitor

### View Logs

**Windows/Linux/macOS:**
```bash
# If you redirected output
tail -f monitor.log
```

**Linux/systemd:**
```bash
sudo journalctl -u filebrowser-monitor -f
```

**Docker:**
```bash
docker-compose logs -f filebrowser-monitor
```

### Check Database

```bash
sqlite3 file_tracker.db
```

Useful queries:
```sql
-- See all tracked files
SELECT path, modified FROM files LIMIT 10;

-- Count files by directory
SELECT COUNT(*), dirname(path) as dir FROM files GROUP BY dirname(path);

-- See notification history
SELECT * FROM notifications ORDER BY notification_time DESC LIMIT 20;

-- Check database size
SELECT page_count * page_size / 1024 / 1024 FROM pragma_page_count(), pragma_page_size();
```

---

## Security Considerations

1. **Credentials in config.json**
   - Don't commit to version control
   - Add to `.gitignore`
   - Consider using environment variables:
     ```json
     {
       "filebrowser": {
         "url": "${FB_URL}",
         "username": "${FB_USER}",
         "password": "${FB_PASS}"
       }
     }
     ```

2. **Discord Webhook**
   - If compromised, anyone can send messages to your channel
   - Regenerate in Discord settings if exposed
   - Treat like a password

3. **Database**
   - Contains file history and timestamps
   - Keep backups
   - Restrict file permissions: `chmod 600 file_tracker.db`

4. **Logs**
   - May contain error messages with sensitive info
   - Rotate logs periodically
   - Don't share publicly

---

## Performance Tips

1. **Large Filesystems**
   - First scan may take several minutes
   - Subsequent scans are faster (database caching)
   - Consider increasing `interval_minutes` to reduce load

2. **Reduce Notifications**
   - Use `ignore_dirs` and `exclude_patterns`
   - Example: Ignore node_modules, .git, cache directories

3. **Network Optimization**
   - Run monitor on same network as FileBrowser
   - Use direct IP instead of DNS if possible
   - Consider running in Docker on same host

---

## Advanced Configuration

### Environment Variables

Create `.env` file (optional):
```bash
FB_URL=http://localhost:8080
FB_USER=admin
FB_PASS=your-password
DISCORD_WEBHOOK=https://...
MONITOR_INTERVAL=30
```

### Custom Notifications

Edit `DiscordNotifier` class to customize message format, colors, include statistics, etc.

### Multiple Instances

Run multiple monitors for different FileBrowser instances:
```bash
python monitor.py --config config-backup.json
python monitor.py --config config-media.json
```

---

## Next Steps

1. ✅ Verify monitor is running
2. ✅ Test with manual file upload
3. ✅ Monitor Discord for notifications
4. ✅ Adjust `interval_minutes` as needed
5. ✅ Set up monitoring/alerting for the monitor itself

---

## Support

For issues or questions, check the README.md or open an issue on GitHub.
