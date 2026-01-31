# Architecture

## Overview

FileBrowser Monitor is a polling-based file change detection system that:
1. Periodically scans a FileBrowser instance via its REST API
2. Tracks files in a local SQLite database
3. Detects changes (new, modified, deleted)
4. Sends notifications to Discord

## Components

### FileBrowserClient
Handles communication with FileBrowser REST API:
- Authenticates with username/password
- Recursively fetches all files and directories
- Parses file metadata (path, size, modification time)
- Handles errors gracefully

### FileTrackerDB
SQLite database management:
- Stores file metadata and modification times
- Tracks when files were first seen
- Records notification history
- Uses UPSERT for efficient updates

### DiscordNotifier
Discord webhook integration:
- Formats changes into Discord embeds
- Groups files by change type (new/modified/deleted)
- Handles color coding and file size formatting
- Manages embedding limits (max 10 per message, max 15 files per embed)

### FileMonitor
Main orchestration:
- Coordinates between FileBrowserClient, FileTrackerDB, and DiscordNotifier
- Detects changes by comparing database state with current scan
- Filters files based on ignore patterns
- Manages monitoring lifecycle

## Data Flow

```
[FileBrowser API] 
        ↓
[FileBrowserClient - recursively fetches all files]
        ↓
[FileMonitor - compares with database]
        ↓
    [Database] ← → [FileMonitor]
        ↓
[Change Detection: new/modified/deleted]
        ↓
[DiscordNotifier - formats and sends]
        ↓
[Discord Webhook]
```

## Database Schema

### Files Table
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,      -- Full file path
    size INTEGER,                   -- File size in bytes
    mod_time REAL,                  -- Unix timestamp of modification
    is_dir BOOLEAN,                 -- Whether it's a directory
    name TEXT,                      -- Just the filename
    first_seen REAL NOT NULL,       -- When first tracked
    last_checked REAL NOT NULL      -- Last scan time
)
```

### Notifications Table
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,        -- Path of file
    notification_time REAL NOT NULL, -- When notification was sent
    change_type TEXT NOT NULL       -- 'new', 'modified', or 'deleted'
)
```

## Configuration File Structure

```json
{
  "filebrowser": {
    "url": "http://...",            // FileBrowser API URL
    "username": "...",              // Admin username
    "password": "..."               // Admin password
  },
  "discord": {
    "webhook_url": "https://..."    // Discord webhook URL
  },
  "monitoring": {
    "interval_minutes": 30,         // Check interval
    "ignore_dirs": [...],           // Dirs to skip
    "exclude_patterns": [...]       // File patterns to ignore
  }
}
```

## Change Detection Algorithm

1. Fetch current files from FileBrowser
2. Apply filters (ignore patterns)
3. Load previous state from database
4. For each current file:
   - If not in database → **New**
   - If in database but mod_time changed → **Modified**
5. For each previous file not in current:
   - If not a directory → **Deleted**
6. Only report changes within detection window (since last run)

## Error Handling

- **Authentication failures**: Exit with error (credentials invalid)
- **Network errors**: Log and retry after interval
- **FileBrowser API errors**: Log and continue (may be temporary)
- **Discord failures**: Log but don't crash (webhook may be temporary)
- **Database errors**: This would be a critical error

## Performance Considerations

- **First run**: Can be slow with large file systems (100k+ files)
- **Subsequent runs**: Fast due to database caching
- **Network I/O**: Bottleneck is FileBrowser API response time
- **Database size**: Grows with number of tracked files (~1MB per 1000 files)

## Security Model

- Configuration file contains credentials (keep secure)
- Discord webhook URL is sensitive (treat as password)
- Database contains file paths and metadata (not encrypted)
- No SSL pinning (use firewalls if needed)
- Token-based auth with FileBrowser (better than basic auth)

## Limitations

1. **Polling-based**: Not real-time, depends on interval
2. **File deletions**: Only detected if removed from FileBrowser
3. **Directory changes**: Directories aren't reported (only files)
4. **Concurrency**: Single-threaded, sequential scans
5. **File movements**: Reported as new + deleted files
6. **Symlinks**: Followed, not reported separately
7. **No webhook redundancy**: Single Discord endpoint

## Future Improvements

- [ ] Webhook retry logic with exponential backoff
- [ ] Support for multiple webhooks/channels
- [ ] File size thresholds for notifications
- [ ] Slack/Teams integration
- [ ] Real-time monitoring via webhooks (if FileBrowser adds support)
- [ ] Multi-threaded directory traversal
- [ ] Database compression/cleanup
- [ ] Metrics/statistics reporting
- [ ] Configuration hot-reload
- [ ] HTTP basic auth support for FileBrowser
