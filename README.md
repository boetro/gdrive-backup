# Google Drive Backup Utility

A Python utility for automatically backing up local folders to Google Drive with version management. Creates compressed tar.xz archives with timestamps and automatically maintains a configurable number of backup versions.

## Features

- **Automated Backups**: Create compressed backups of local folders and upload to Google Drive
- **Version Management**: Automatically delete old backups, keeping only the specified number of versions
- **High Compression**: Uses tar.xz (LZMA) compression for efficient storage
- **OAuth 2.0 Authentication**: Secure authentication with automatic token refresh
- **Unattended Operation**: After initial setup, runs completely automated (perfect for cron jobs)
- **Multi-folder Support**: Backup multiple folders in a single run

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Google Cloud project with Drive API enabled
- OAuth 2.0 credentials (Desktop application type)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gdrive-backup
```

2. Install dependencies using uv:
```bash
uv sync
```

## Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Required: Google Drive folder ID where backups will be uploaded
# Find this in the URL when viewing the folder in Google Drive
DESTINATION_FOLDER_ID=your_folder_id_here

# Required: Comma-separated list of local folder paths to backup
BACKUP_FOLDERS=/path/to/folder1,/path/to/folder2

# Required: Path to your OAuth 2.0 credentials JSON file
GOOGLE_CREDENTIALS_PATH=client_secrets.json

# Optional: Number of backup versions to retain (default: 5)
MAX_BACKUP_VERSIONS=5
```

### Getting Google Drive Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the credentials JSON file
6. Save it as `client_secrets.json` (or update `GOOGLE_CREDENTIALS_PATH` accordingly)

## Initial Setup

The first time you run the backup, you'll need to authenticate with Google:

```bash
uv run main.py
```

This will:
1. Open a browser window for Google authentication
2. Ask you to sign in and grant permissions
3. Save a refresh token to `token.json`
4. Perform the first backup

After this initial setup, all subsequent runs (including automated cron jobs) will authenticate automatically using the saved token.

## Usage

### Manual Backup

Run the backup manually:
```bash
uv run main.py
```

## How It Works

1. **Archive Creation**: For each folder specified in `BACKUP_FOLDERS`:
   - Creates a compressed tar.xz archive
   - Names it with format: `{folder_name}_{YYYYMMDD_HHMMSS}.tar.xz`

2. **Upload**: Uploads the archive to the specified Google Drive folder

3. **Cleanup**:
   - Lists all backups in the destination folder matching the pattern
   - Sorts by creation time (oldest first)
   - Deletes the oldest versions if total exceeds `MAX_BACKUP_VERSIONS`

## Development

### Linting and Formatting

```bash
# Check code style
uv run ruff check

# Format code
uv run ruff format
```

### Install/Update Dependencies

```bash
uv sync
```
## Backup Naming Convention

Backups are named using the pattern: `{folder_name}_{YYYYMMDD_HHMMSS}.tar.xz`

Example: `documents_20250109_140530.tar.xz`

This ensures:
- Easy identification of backup contents
- Chronological sorting
- Proper filtering during cleanup operations
