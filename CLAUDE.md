# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python utility for backing up local folders to Google Drive using OAuth 2.0 authentication. Creates compressed tar.xz archives with timestamps and automatically manages backup versions by deleting old backups.

## Development Commands

**Run the backup:**
```bash
uv run main.py
```

**Linting:**
```bash
uv run ruff check
uv run ruff format
```

**Install dependencies:**
```bash
uv sync
```

## Configuration

The application requires a `.env` file with the following variables:

- `DESTINATION_FOLDER_ID`: Google Drive folder ID where backups are uploaded
- `BACKUP_FOLDERS`: Comma-separated list of local folder paths to backup
- `GOOGLE_CREDENTIALS_PATH`: Path to OAuth 2.0 credentials JSON file (e.g., `client_secrets.json`)
- `MAX_BACKUP_VERSIONS`: (Optional) Number of backup versions to retain (default: 5)

## Initial Setup

**First-time authentication:**

1. Ensure you have OAuth 2.0 credentials from Google Cloud Console (Desktop application type)
2. Update `.env` with the path to your OAuth credentials file
3. Run the backup manually for the first time:
   ```bash
   uv sync  # Install/update dependencies including google-auth-oauthlib
   uv run main.py
   ```
4. A browser window will open for authentication - sign in with your Google account
5. Grant the requested permissions
6. The refresh token will be saved to `token.json`
7. All subsequent runs (including cron jobs) will authenticate automatically using the saved token

**Automated cron execution:**

After the initial setup, the script runs completely unattended. Example crontab entry:
```bash
0 2 * * * cd /path/to/gdrive-backup && /path/to/uv run main.py
```

## Architecture

**Core Components:**

- `gdrive_backup/client.py`: `GoogleDriveClient` handles Google Drive API operations (upload, list, delete) using OAuth 2.0 user credentials with `drive.file` scope
- `gdrive_backup/config.py`: `Config` dataclass loads and validates environment variables from `.env`
- `main.py`: Entry point that orchestrates the backup workflow:
  1. Creates tar.xz archives with timestamp naming (`{folder_name}_{YYYYMMDD_HHMMSS}.tar.xz`)
  2. Uploads to Google Drive via `GoogleDriveClient`
  3. Cleans up old backups by listing files in destination folder, filtering by name pattern, sorting by creation time, and deleting oldest versions exceeding `max_backup_versions`

**Authentication:**
Uses OAuth 2.0 with user credentials. On first run, opens browser for authentication and saves a refresh token to `token.json`. Subsequent runs automatically refresh the access token using the saved refresh token. Files are uploaded to the authenticated user's Google Drive and count against their storage quota.

**Backup Versioning:**
The cleanup logic filters backups by checking for files matching `{folder_name}_*.tar.xz` pattern in the destination folder, ensuring only backups for the specific folder are managed.
