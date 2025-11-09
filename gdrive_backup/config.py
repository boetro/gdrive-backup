import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    destination_folder_id: str
    backup_folders: list[str]
    credentials_path: str
    token_path: str = "token.json"
    max_backup_versions: int = 3

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()

        destination_folder_id = os.environ.get("DESTINATION_FOLDER_ID")
        if not destination_folder_id:
            raise ValueError("DESTINATION_FOLDER_ID environment variable is required")

        backup_folders_str = os.environ.get("BACKUP_FOLDERS")
        if not backup_folders_str:
            raise ValueError("BACKUP_FOLDERS environment variable is required")

        backup_folders = [folder.strip() for folder in backup_folders_str.split(",")]

        credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
        if not credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable is required")

        token_path = os.environ.get("TOKEN_PATH", "token.json")

        max_backup_versions_str = os.environ.get("MAX_BACKUP_VERSIONS", "5")
        try:
            max_backup_versions = int(max_backup_versions_str)
            if max_backup_versions < 1:
                raise ValueError("MAX_BACKUP_VERSIONS must be at least 1")
        except ValueError as e:
            raise ValueError(
                f"Invalid MAX_BACKUP_VERSIONS value: {max_backup_versions_str}"
            ) from e

        return cls(
            destination_folder_id=destination_folder_id,
            backup_folders=backup_folders,
            credentials_path=credentials_path,
            token_path=token_path,
            max_backup_versions=max_backup_versions,
        )
