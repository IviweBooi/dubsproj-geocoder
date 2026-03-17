"""
main.py
-------
DUBSPROJ-202603001 | Automated Geocoding Pipeline

This is the main entry point for the pipeline. It:
1.  Connects to Google Drive to find new CSV files.
2.  Downloads and processes them using the batch processor.
3.  Uploads the geocoded results back to the same Google Drive folder.
"""

import os
import logging
from google_drive_service import list_files_in_folder, download_file, upload_file
from batch_processor import process_csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (uses the settings from geocoder)
logger = logging.getLogger(__name__)

def run_pipeline():
    """
    Main execution loop for the geocoding pipeline.
    """
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        logger.error("GOOGLE_DRIVE_FOLDER_ID not set in .env")
        return

    # 1. List files in Google Drive
    logger.info(f"Checking for new files in Google Drive folder: {folder_id}")
    files = list_files_in_folder(folder_id)
    
    if not files:
        logger.info("No CSV files found to process.")
        return

    # Create local data directory if it doesn't exist
    local_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(local_data_dir, exist_ok=True)

    # 2. Process each file
    for f in files:
        filename = f['name']
        file_id = f['id']
        
        # Skip files that look like geocoded outputs to avoid infinite loops
        if "geocoded" in filename.lower():
            logger.info(f"Skipping output file: {filename}")
            continue

        logger.info(f"--- Processing File: {filename} ---")
        
        local_input = os.path.join(local_data_dir, filename)
        local_output = os.path.join(local_data_dir, f"geocoded_{filename}")

        # Download from Google Drive
        if download_file(file_id, local_input):
            # Process locally
            process_csv(local_input, local_output)
            
            # Upload results back to Google Drive
            upload_file(local_output, folder_id)
            
            logger.info(f"--- Completed: {filename} ---")
        else:
            logger.error(f"Failed to download {filename}")

if __name__ == "__main__":
    run_pipeline()
