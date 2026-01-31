# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-31

### Added
- Initial release of FileBrowser Monitor
- Periodic file monitoring (every 30 minutes, configurable)
- SQLite-based file tracking across runs
- Change detection for new, modified, and deleted files
- Beautiful Discord webhook notifications with embeds
- Smart file filtering (ignore directories and patterns)
- Multiple deployment options:
  - Direct Python execution
  - Windows Task Scheduler
  - Linux Cron
  - Systemd service
  - Docker/Docker Compose
- Comprehensive documentation and installation guide
- Setup scripts for Windows, Linux, and macOS
- Configuration file support with examples
- Batch notifications (all changes in one message)
- File size formatting in notifications
- Error handling and logging

[Unreleased]: https://github.com/yourusername/filebrowser-notifs/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/filebrowser-notifs/releases/tag/v1.0.0
