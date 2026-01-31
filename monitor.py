#!/usr/bin/env python3
"""
FileBrowser Notification Monitor
Monitors a FileBrowser instance for new/modified files and sends Discord notifications
"""

import os
import sys
import json
import time
import sqlite3
import argparse
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FileRecord:
    path: str
    size: int
    mod_time: float
    is_dir: bool
    name: str


class FileTrackerDB:
    """Manages SQLite database for tracking file modifications"""
    
    def __init__(self, db_path: str = "file_tracker.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    path TEXT UNIQUE NOT NULL,
                    size INTEGER,
                    mod_time REAL,
                    is_dir BOOLEAN,
                    name TEXT,
                    first_seen REAL NOT NULL,
                    last_checked REAL NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    notification_time REAL NOT NULL,
                    change_type TEXT NOT NULL
                )
            ''')
            conn.commit()
    
    def get_all_files(self) -> Dict[str, FileRecord]:
        """Get all tracked files from database"""
        result = {}
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM files')
            for row in cursor.fetchall():
                result[row['path']] = FileRecord(
                    path=row['path'],
                    size=row['size'],
                    mod_time=row['mod_time'],
                    is_dir=row['is_dir'],
                    name=row['name']
                )
        return result
    
    def update_or_insert_file(self, file_record: FileRecord, current_time: float):
        """Update or insert a file record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO files (path, size, mod_time, is_dir, name, first_seen, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    size = excluded.size,
                    mod_time = excluded.mod_time,
                    last_checked = excluded.last_checked
            ''', (file_record.path, file_record.size, file_record.mod_time, 
                  file_record.is_dir, file_record.name, current_time, current_time))
            conn.commit()
    
    def get_first_seen_time(self, path: str) -> Optional[float]:
        """Get when a file was first seen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT first_seen FROM files WHERE path = ?', (path,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def record_notification(self, file_path: str, change_type: str, current_time: float):
        """Record that a notification was sent for a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (file_path, notification_time, change_type)
                VALUES (?, ?, ?)
            ''', (file_path, current_time, change_type))
            conn.commit()


class FileBrowserClient:
    """Client for interacting with FileBrowser API"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with FileBrowser and get token"""
        url = f"{self.base_url}/api/login"
        payload = {
            "username": self.username,
            "password": self.password
        }
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            # Check if response is JSON or plain text token
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                # Standard JSON response with {"token": "..."}
                data = response.json()
                self.token = data.get('token')
            elif 'text/plain' in content_type:
                # Some FileBrowser versions return token directly as plain text
                self.token = response.text.strip()
                logger.info("Received token as plain text (older FileBrowser format)")
            else:
                logger.error(f"FileBrowser returned unexpected content type: {content_type}")
                logger.error(f"Response text (first 200 chars): {response.text[:200]}")
                raise ValueError(f"Expected JSON or text response but got {content_type}. Is FileBrowser running at {self.base_url}?")
            
            if not self.token:
                raise ValueError("No token received from authentication")
            logger.info("Successfully authenticated with FileBrowser")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to FileBrowser at {self.base_url}")
            logger.error(f"Please ensure FileBrowser is running and the URL is correct")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Connection to FileBrowser at {self.base_url} timed out")
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def get_files(self, path: str = "/") -> List[FileRecord]:
        """Recursively get all files in a directory"""
        files = []
        self._fetch_directory(path, files)
        return files
    
    def _fetch_directory(self, path: str, files: List[FileRecord]):
        """Recursively fetch directory contents"""
        url = f"{self.base_url}/api/resources{path}"
        headers = {"X-Auth": self.token}
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # If it's a directory with items
            if data.get('items'):
                for item in data['items']:
                    file_record = FileRecord(
                        path=item['path'],
                        size=item['size'],
                        mod_time=self._parse_timestamp(item['modified']),
                        is_dir=item['isDir'],
                        name=item['name']
                    )
                    files.append(file_record)
                    
                    # Recursively fetch subdirectories
                    if item['isDir'] and item['path'] != '/':
                        self._fetch_directory(item['path'], files)
        except Exception as e:
            logger.warning(f"Error fetching directory {path}: {e}")
    
    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> float:
        """Parse ISO format timestamp to Unix timestamp"""
        try:
            # Handle format like "2024-01-15T10:30:45Z"
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.timestamp()
        except Exception:
            return time.time()


class DiscordNotifier:
    """Sends notifications to Discord via webhook"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session = requests.Session()
    
    def send_notification(self, changes: Dict[str, List[Dict]]):
        """Send formatted notification to Discord"""
        if not changes:
            return
        
        embeds = []
        
        # Group changes by type
        for change_type, files in changes.items():
            if not files:
                continue
            
            # Create chunks of files (Discord has limits)
            for chunk in self._chunk_files(files, 15):
                embed = self._create_embed(change_type, chunk)
                embeds.append(embed)
        
        # Send embeds in chunks (max 10 per message)
        for embed_chunk in self._chunk_embeds(embeds, 10):
            self._send_webhook({"embeds": embed_chunk})
    
    def _create_embed(self, change_type: str, files: List[Dict]) -> Dict:
        """Create a Discord embed for a batch of files"""
        colors = {
            "new": 0x00ff00,      # Green
            "modified": 0xffff00, # Yellow
            "deleted": 0xff0000   # Red
        }
        
        title_map = {
            "new": "📦 New Files Uploaded",
            "modified": "✏️ Files Modified",
            "deleted": "🗑️ Files Deleted"
        }
        
        # Format file list
        file_lines = []
        total_size = 0
        for file_info in files:
            path = file_info.get('path', 'unknown')
            size = file_info.get('size', 0)
            
            if size > 0:
                size_str = self._format_size(size)
                file_lines.append(f"`{path}` ({size_str})")
                total_size += size
            else:
                file_lines.append(f"`{path}`")
        
        description = "\n".join(file_lines[:15])  # Limit to 15 files per embed
        
        embed = {
            "title": title_map.get(change_type, "Files Changed"),
            "description": description,
            "color": colors.get(change_type, 0x808080),
            "footer": {
                "text": f"Total: {len(files)} file(s) | {self._format_size(total_size)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return embed
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @staticmethod
    def _chunk_files(files: List[Dict], chunk_size: int) -> List[List[Dict]]:
        """Split files into chunks"""
        return [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]
    
    @staticmethod
    def _chunk_embeds(embeds: List[Dict], chunk_size: int) -> List[List[Dict]]:
        """Split embeds into chunks"""
        return [embeds[i:i + chunk_size] for i in range(0, len(embeds), chunk_size)]
    
    def _send_webhook(self, data: Dict):
        """Send data to Discord webhook"""
        try:
            response = self.session.post(self.webhook_url, json=data)
            response.raise_for_status()
            logger.info("Notification sent to Discord")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")


class FileMonitor:
    """Main monitor coordinating file tracking and notifications"""
    
    def __init__(self, 
                 fb_url: str,
                 fb_username: str,
                 fb_password: str,
                 discord_webhook: str,
                 db_path: str = "file_tracker.db",
                 ignore_dirs: Optional[List[str]] = None,
                 exclude_patterns: Optional[List[str]] = None):
        
        self.fb_client = FileBrowserClient(fb_url, fb_username, fb_password)
        self.discord = DiscordNotifier(discord_webhook)
        self.db = FileTrackerDB(db_path)
        self.ignore_dirs = ignore_dirs or []
        self.exclude_patterns = exclude_patterns or []
        self.last_run = None
    
    def monitor(self):
        """Perform a monitoring cycle"""
        logger.info("Starting monitoring cycle")
        current_time = time.time()
        
        # Fetch current files from FileBrowser
        logger.info("Fetching files from FileBrowser...")
        current_files = self.fb_client.get_files()
        current_files = self._filter_files(current_files)
        
        logger.info(f"Found {len(current_files)} files")
        
        # Convert to dict for easier lookup
        current_dict = {f.path: f for f in current_files}
        
        # Get previously tracked files
        previous_dict = self.db.get_all_files()
        
        # Detect changes
        changes = defaultdict(list)
        detection_time = current_time - (30 * 60)  # 30 minutes ago (for first run, use full 30 mins)
        
        if self.last_run:
            detection_time = self.last_run
        
        # Check for new and modified files
        for file_path, current_file in current_dict.items():
            if file_path not in previous_dict:
                # New file
                if current_file.mod_time >= detection_time:
                    changes["new"].append({
                        "path": file_path,
                        "size": current_file.size,
                        "name": current_file.name
                    })
                    logger.info(f"New file detected: {file_path}")
            else:
                # Existing file - check if modified
                previous_file = previous_dict[file_path]
                if current_file.mod_time > previous_file.mod_time and current_file.mod_time >= detection_time:
                    changes["modified"].append({
                        "path": file_path,
                        "size": current_file.size,
                        "name": current_file.name
                    })
                    logger.info(f"Modified file detected: {file_path}")
        
        # Check for deleted files
        for file_path, previous_file in previous_dict.items():
            if file_path not in current_dict and not previous_file.is_dir:
                changes["deleted"].append({
                    "path": file_path,
                    "size": previous_file.size,
                    "name": previous_file.name
                })
                logger.info(f"Deleted file detected: {file_path}")
        
        # Update database with current files
        for file_record in current_files:
            self.db.update_or_insert_file(file_record, current_time)
        
        # Send notifications if there are changes
        if any(changes.values()):
            logger.info(f"Sending notification with {sum(len(v) for v in changes.values())} changes")
            self.discord.send_notification(dict(changes))
        else:
            logger.info("No changes detected")
        
        self.last_run = current_time
        logger.info("Monitoring cycle completed")
    
    def _filter_files(self, files: List[FileRecord]) -> List[FileRecord]:
        """Filter out ignored directories and patterns"""
        filtered = []
        for f in files:
            # Skip directories
            if f.is_dir:
                continue
            
            # Check ignore patterns
            skip = False
            for pattern in self.ignore_dirs:
                if pattern in f.path:
                    skip = True
                    break
            
            for pattern in self.exclude_patterns:
                if f.path.endswith(pattern):
                    skip = True
                    break
            
            if not skip:
                filtered.append(f)
        
        return filtered


def create_config_template(config_path: str):
    """Create a template configuration file"""
    template = {
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
    
    with open(config_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    logger.info(f"Template configuration created at {config_path}")


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        create_config_template(config_path)
        raise FileNotFoundError(f"Configuration file not found. Template created at {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor FileBrowser for new files and send Discord notifications"
    )
    parser.add_argument('--config', default='config.json',
                       help='Path to configuration file (default: config.json)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (don\'t loop)')
    parser.add_argument('--init-config', action='store_true',
                       help='Create a template configuration file')
    
    args = parser.parse_args()
    
    if args.init_config:
        create_config_template(args.config)
        return
    
    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Extract configuration
    fb_config = config.get('filebrowser', {})
    discord_config = config.get('discord', {})
    monitor_config = config.get('monitoring', {})
    
    # Validate required config
    if not all([fb_config.get('url'), fb_config.get('username'), 
                fb_config.get('password'), discord_config.get('webhook_url')]):
        logger.error("Missing required configuration. Please update your config.json")
        sys.exit(1)
    
    # Create monitor
    monitor = FileMonitor(
        fb_url=fb_config['url'],
        fb_username=fb_config['username'],
        fb_password=fb_config['password'],
        discord_webhook=discord_config['webhook_url'],
        ignore_dirs=monitor_config.get('ignore_dirs', []),
        exclude_patterns=monitor_config.get('exclude_patterns', [])
    )
    
    interval = monitor_config.get('interval_minutes', 30) * 60
    
    logger.info(f"Starting FileBrowser Monitor (interval: {interval}s)")
    logger.info(f"Monitoring: {fb_config['url']}")
    
    try:
        if args.once:
            monitor.monitor()
        else:
            while True:
                try:
                    monitor.monitor()
                    logger.info(f"Next check in {interval} seconds")
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error during monitoring cycle: {e}", exc_info=True)
                    logger.info(f"Retrying in {interval} seconds")
                    time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
