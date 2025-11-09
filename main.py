import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from gdrive_backup.client import GoogleDriveClient
from gdrive_backup.config import Config


def _backup_folder(
    client: GoogleDriveClient,
    destination_folder_id: str,
    to_backup: str,
    max_versions: int,
):
    """
    Create a compressed archive of a folder and upload it to Google Drive.
    Maintains a maximum number of backup versions by deleting oldest backups.

    Args:
        client: GoogleDriveClient instance for uploading.
        destination_folder_id: Google Drive folder ID to upload to.
        to_backup: Path to the folder to backup.
        max_versions: Maximum number of backup versions to keep.
    """
    backup_path = Path(to_backup)

    if not backup_path.exists():
        raise FileNotFoundError(f"Folder not found: {to_backup}")

    if not backup_path.is_dir():
        raise ValueError(f"Path is not a directory: {to_backup}")

    # Create a timestamp for the backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = backup_path.name
    archive_name = f"{folder_name}_{timestamp}.tar.xz"

    # Create temporary directory for the archive
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / archive_name

        # Create compressed tar archive with xz (LZMA) compression
        # xz provides excellent lossless compression
        print(f"Creating archive for {to_backup}...")
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(backup_path, arcname=folder_name)

        print(
            f"Archive created: {archive_name} ({archive_path.stat().st_size / 1024 / 1024:.2f} MB)"
        )

        # Upload to Google Drive
        print("Uploading to Google Drive...")
        file_id = client.upload_file(
            file_path=archive_path,
            folder_id=destination_folder_id,
            file_name=archive_name,
        )

        print(f"Successfully uploaded {archive_name} (ID: {file_id})")

    # Cleanup old backups
    _cleanup_old_backups(client, destination_folder_id, folder_name, max_versions)


def _cleanup_old_backups(
    client: GoogleDriveClient, folder_id: str, folder_name: str, max_versions: int
):
    """
    Remove old backup versions exceeding the maximum allowed.

    Args:
        client: GoogleDriveClient instance.
        folder_id: Google Drive folder ID containing backups.
        folder_name: Name of the backed-up folder (for filtering).
        max_versions: Maximum number of versions to keep.
    """
    print(f"Checking for old backups of {folder_name}...")

    # List all files in the destination folder
    all_files = client.list_files_in_folder(folder_id)

    # Filter for backups of this specific folder
    backup_prefix = f"{folder_name}_"
    backup_suffix = ".tar.xz"
    backups = [
        f
        for f in all_files
        if f["name"].startswith(backup_prefix) and f["name"].endswith(backup_suffix)
    ]

    # Sort by creation time (oldest first)
    backups.sort(key=lambda x: x["createdTime"])

    # Calculate how many to delete
    num_to_delete = len(backups) - max_versions

    if num_to_delete > 0:
        print(
            f"Found {len(backups)} backup(s), deleting {num_to_delete} oldest version(s)..."
        )
        for backup in backups[:num_to_delete]:
            print(f"  Deleting: {backup['name']} (ID: {backup['id']})")
            client.delete_file(backup["id"])
        print(f"Cleanup complete. {max_versions} version(s) retained.")
    else:
        print(
            f"No cleanup needed. {len(backups)} version(s) found (max: {max_versions})."
        )


def main():
    config = Config.from_env()
    client = GoogleDriveClient(config.credentials_path, config.token_path)

    for to_backup in config.backup_folders:
        _backup_folder(
            client, config.destination_folder_id, to_backup, config.max_backup_versions
        )


if __name__ == "__main__":
    main()
