"""
google_drive_service.py
-----------------------
Responsible for interacting with the Google Drive API using a Service Account.
Handles listing, downloading, and uploading CSV files for the geocoding pipeline.
"""

import os
import io
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Scopes required for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """
    Authenticates using the service account file specified in .env
    and returns a Google Drive API service instance.
    """
    service_account_file = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE")
    
    if not service_account_file or not os.path.exists(service_account_file):
        logger.error(f"Service account file not found: {service_account_file}")
        return None

    try:
        creds = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Drive: {str(e)}")
        return None

def list_files_in_folder(folder_id: str):
    """
    Lists all CSV files in a specific Google Drive folder.
    """
    service = get_drive_service()
    if not service:
        return []

    try:
        query = f"'{folder_id}' in parents and mimeType = 'text/csv' and trashed = false"
        results = service.files().list(
            q=query, fields="files(id, name)").execute()
        return results.get('files', [])
    except Exception as e:
        logger.error(f"Failed to list files in folder {folder_id}: {str(e)}")
        return []

def download_file(file_id: str, local_path: str):
    """
    Downloads a file from Google Drive to a local path.
    """
    service = get_drive_service()
    if not service:
        return False

    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(f"Download progress for {file_id}: {int(status.progress() * 100)}%")
        
        logger.info(f"Successfully downloaded file {file_id} to {local_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download file {file_id}: {str(e)}")
        return False

def upload_file(local_path: str, folder_id: str, filename: str = None):
    """
    Uploads a local file to a specific Google Drive folder.
    """
    service = get_drive_service()
    if not service:
        return None

    if not filename:
        filename = os.path.basename(local_path)

    try:
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(local_path, mimetype='text/csv')
        file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
        
        logger.info(f"Successfully uploaded {filename} to folder {folder_id}. File ID: {file.get('id')}")
        return file.get('id')
    except Exception as e:
        logger.error(f"Failed to upload file {local_path}: {str(e)}")
        return None

if __name__ == "__main__":
    logger.info("Google Drive Service module loaded.")
