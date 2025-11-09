from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


class GoogleDriveClient:
    """Client for uploading files to Google Drive using OAuth 2.0."""

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    TOKEN_FILE = "token.json"

    def __init__(self, credentials_path: str):
        """
        Initialize the Google Drive client.

        Args:
            credentials_path: Path to the OAuth 2.0 credentials JSON file
                            (client_secrets.json or similar).
        """
        self.credentials_path = credentials_path
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Authenticate with Google Drive using OAuth 2.0.

        On first run, this will open a browser window for authentication.
        Subsequent runs will use the stored refresh token from token.json.
        """
        creds = None
        token_path = Path(self.TOKEN_FILE)

        # Load existing token if it exists
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(token_path), self.SCOPES
                )
            except Exception as e:
                print(f"Warning: Could not load token file: {e}")
                creds = None

        # If credentials are invalid or don't exist, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    print("Re-authenticating...")
                    creds = None

            if not creds:
                # Run interactive OAuth flow
                if not Path(self.credentials_path).exists():
                    raise FileNotFoundError(
                        f"OAuth credentials file not found: {self.credentials_path}"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=8080)

            # Save the credentials for future runs
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        try:
            service = build("drive", "v3", credentials=creds)
            return service
        except Exception as e:
            raise RuntimeError(f"Failed to build Google Drive service: {e}")

    def upload_file(
        self, file_path: str | Path, folder_id: str, file_name: str | None = None
    ) -> str:
        """
        Upload a file to a Google Drive folder.

        Args:
            file_path: Path to the file to upload.
            folder_id: ID of the Google Drive folder to upload to.
            file_name: Optional name for the file in Google Drive.
                      If None, uses the original file name.

        Returns:
            The ID of the uploaded file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            HttpError: If the upload fails.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_name is None:
            file_name = file_path.name

        file_metadata = {"name": file_name, "parents": [folder_id]}

        try:
            media = MediaFileUpload(str(file_path), resumable=True)
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            file_id = file.get("id")
            return file_id

        except HttpError as error:
            raise HttpError(f"Failed to upload file to Google Drive: {error}")

    def list_files_in_folder(self, folder_id: str) -> list[dict]:
        """
        List all files in a Google Drive folder.

        Args:
            folder_id: ID of the folder to list files from.

        Returns:
            List of file metadata dictionaries.
        """
        try:
            results = (
                self.service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed=false",
                    fields="files(id, name, createdTime, modifiedTime)",
                )
                .execute()
            )
            return results.get("files", [])
        except HttpError as error:
            raise HttpError(f"Failed to list files in folder: {error}")

    def delete_file(self, file_id: str) -> None:
        """
        Delete a file from Google Drive.

        Args:
            file_id: ID of the file to delete.
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
        except HttpError as error:
            raise HttpError(f"Failed to delete file: {error}")
