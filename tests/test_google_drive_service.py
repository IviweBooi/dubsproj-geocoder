import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_drive_service import (
    get_drive_service,
    list_files_in_folder,
    download_file,
    upload_file
)

class TestGoogleDriveService(unittest.TestCase):

    @patch('google_drive_service.service_account.Credentials.from_service_account_file')
    @patch('google_drive_service.build')
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_get_drive_service_success(self, mock_getenv, mock_exists, mock_build, mock_creds):
        mock_getenv.return_value = "fake_path.json"
        mock_exists.return_value = True
        
        service = get_drive_service()
        
        self.assertIsNotNone(service)
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds.return_value)

    @patch('os.path.exists')
    @patch('os.getenv')
    def test_get_drive_service_no_file(self, mock_getenv, mock_exists):
        mock_getenv.return_value = "non_existent.json"
        mock_exists.return_value = False
        
        service = get_drive_service()
        self.assertIsNone(service)

    @patch('google_drive_service.get_drive_service')
    def test_list_files_in_folder(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_service.files.return_value.list.return_value.execute.return_value = {
            'files': [{'id': '123', 'name': 'test.csv'}]
        }
        
        files = list_files_in_folder("folder_id")
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], 'test.csv')

    @patch('google_drive_service.MediaIoBaseDownload')
    @patch('io.FileIO', new_callable=mock_open)
    @patch('google_drive_service.get_drive_service')
    def test_download_file(self, mock_get_service, mock_file_io, mock_download):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock downloader behavior
        mock_downloader_instance = mock_download.return_value
        mock_downloader_instance.next_chunk.side_effect = [(MagicMock(progress=lambda: 1.0), True)]
        
        result = download_file("file_id", "local_path.csv")
        
        self.assertTrue(result)
        mock_service.files.return_value.get_media.assert_called_once_with(fileId="file_id")

    @patch('google_drive_service.MediaFileUpload')
    @patch('google_drive_service.get_drive_service')
    def test_upload_file(self, mock_get_service, mock_upload_media):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_service.files.return_value.create.return_value.execute.return_value = {'id': 'new_id'}
        
        file_id = upload_file("local_path.csv", "folder_id")
        
        self.assertEqual(file_id, 'new_id')
        mock_service.files.return_value.create.assert_called_once()

if __name__ == "__main__":
    unittest.main()
