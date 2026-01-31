# FileBrowser Monitor

A Python script that monitors a FileBrowser instance for new or modified files and sends notifications via Discord webhook. The script runs on a configurable interval (default 30 minutes) and batches all changes into a single Discord message.

## Features

- **Periodic Monitoring**: Runs every 30 minutes (configurable)
- **Change Detection**: Detects new files, modified files, and deletions
- **Batch Notifications**: Groups all changes into a single Discord message
- **Persistent Tracking**: Uses SQLite to track file modifications across runs
- **Smart Filtering**: Ignore specific directories and file patterns
- **Robust Error Handling**: Continues operating even if temporary errors occur
- **Formatted Notifications**: Beautiful Discord embeds with file sizes and timestamps

## Requirements

- Python 3.8+
- FileBrowser instance with API access
- Discord webhook URL

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/filebrowser-notifs.git
cd filebrowser-notifs

# Install dependencies
pip install -r requirements.txt

# Initialize configuration
python monitor.py --init-config
```

### Configuration

Edit `config.json` with your settings:

```json
{
  "filebrowser": {
    "url": "http://localhost:8080",
    "username": "admin",
    "password": "admin"
  },
  "discord": {
    "webhook_url": "https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
  },
  "monitoring": {
    "interval_minutes": 30,
    "ignore_dirs": [".git", "__pycache__", "node_modules"],
    "exclude_patterns": [".tmp", ".cache"]
  }
}
```

### Getting a Discord Webhook URL

1. Go to your Discord Server → Settings → Webhooks
2. Click "New Webhook"
3. Name it (e.g., "FileBrowser Monitor")
4. Select the channel where notifications should be sent
5. Click "Copy Webhook URL"
6. Paste into your `config.json`

### Usage

#### Run Once (for testing)

```bash
python monitor.py --once
```

#### Run Continuously

```bash
python monitor.py
```

This starts the monitor in a loop, checking every 30 minutes (or your configured interval).

#### Run with Custom Config

```bash
python monitor.py --config /path/to/custom/config.json
```

## Scheduling

### Linux/macOS (cron)

Add to crontab:

```bash
*/30 * * * * cd /path/to/filebrowser-notifs && python monitor.py >> monitor.log 2>&1
```

Or use the included systemd service:

```bash
sudo cp filebrowser-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable filebrowser-monitor
sudo systemctl start filebrowser-monitor
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "FileBrowser Monitor"
4. Trigger: Daily → Repeat task every 30 minutes
5. Action:
   - Program: `C:\Python\python.exe` (your Python path)
   - Arguments: `C:\path\to\monitor.py`
   - Start in: `C:\path\to\filebrowser-notifs\`

Or use the included PowerShell script for Task Scheduler setup:

```powershell
.\setup_scheduler.ps1
```

### Docker

Use the included docker-compose configuration:

```bash
docker-compose up -d
```

## How It Works

1. **Scans FileBrowser** - Makes API calls to get all files and their modification times
2. **Tracks Changes** - SQLite database stores file metadata and modification history
3. **Detects Updates** - Every 30 mins, compares current files with previous state
4. **Smart Batching** - Groups all changes into a single Discord message
5. **Formats Nicely** - Shows file paths, sizes, and change types with emojis:
   - 📦 New Files (green)
   - ✏️ Modified Files (yellow)
   - 🗑️ Files Deleted (red)

## Database

The script maintains a SQLite database (`file_tracker.db`) that tracks:

- All files and their modification times
- When files were first seen
- Notification history

This database is created automatically and persists across runs.

## Logging

Logs are printed to console. To save logs to a file, redirect output:

```bash
python monitor.py >> monitor.log 2>&1
```

## Troubleshooting

### Connection Refused
- Ensure FileBrowser is running and accessible at the configured URL
- Check firewall settings

### Authentication Failed
- Verify username and password in config.json
- Ensure the user has admin privileges in FileBrowser

### Discord Webhook Not Working
- Verify the webhook URL is correct and not expired
- Check Discord channel permissions
- Ensure the bot can access the channel

### High Database Size
If `file_tracker.db` grows too large:

```bash
rm file_tracker.db
python monitor.py --once
```

This will reset the database. The next run may show all files as "new" since the database is empty.

## Advanced Features

### Skip First Run Notifications

To avoid getting notified about all existing files on first run:

```bash
python monitor.py --once
```

Then start the continuous monitoring the next time.

### Custom Ignore Patterns

Exclude files matching certain patterns by updating `exclude_patterns` in config.json:

```json
"exclude_patterns": [
    ".tmp",
    ".cache",
    "~",
    ".swp"
]
```

## Performance Considerations

- The script recursively scans all files in FileBrowser
- For large file systems (100k+ files), initial scans may take a few minutes
- The database query is fast even for large numbers of files
- Subsequent runs are usually much faster

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the same license as FileBrowser. See the LICENSE file in the main FileBrowser repository for details.

## Support

For issues or questions:
- Check the [INSTALL.md](INSTALL.md) file for detailed setup instructions
- Review the troubleshooting section in this README
- Check FileBrowser logs
- Open an issue on GitHub

## Related

- [FileBrowser](https://github.com/filebrowser/filebrowser) - The main FileBrowser project
