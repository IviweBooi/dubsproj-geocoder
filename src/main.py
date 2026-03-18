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
from datetime import datetime
from google_drive_service import list_files_in_folder, download_file, upload_file
from batch_processor import process_csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_reports(filename: str, summary: dict):
    """
    Generates summary and error reports for a processed file.
    (REQ005, REQ006)
    """
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_base = f"{os.path.splitext(filename)[0]}_{timestamp}"
    
    # 1. Summary Report (Text)
    summary_path = os.path.join(reports_dir, f"summary_{report_base}.txt")
    with open(summary_path, "w") as f:
        f.write(f"Geocoding Execution Summary\n")
        f.write(f"---------------------------\n")
        f.write(f"File: {filename}\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        f.write(f"Total Records:     {summary['total']}\n")
        f.write(f"Successful:        {summary['successful']}\n")
        f.write(f"Failed:            {summary['failed']}\n\n")
        f.write(f"Exact Matches:     {summary['exact_matches']}\n")
        f.write(f"Fallback Matches:  {summary['fallback_matches']}\n")
    
    logger.info(f"Summary report generated: {summary_path}")

    # 2. Error Report (CSV) - REQ005
    if summary['failed'] > 0:
        error_path = os.path.join(reports_dir, f"errors_{report_base}.csv")
        summary['failed_records'].to_csv(error_path, index=False)
        logger.warning(f"Error report generated for {summary['failed']} failed records: {error_path}")

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
            summary = process_csv(local_input, local_output)
            
            if summary:
                # Generate reports (REQ005, REQ006)
                generate_reports(filename, summary)
                
                # Upload results back to Google Drive
                upload_file(local_output, folder_id)
                
                logger.info(f"--- Completed: {filename} ---")
            else:
                logger.error(f"Processing failed for {filename}")
        else:
            logger.error(f"Failed to download {filename}")

if __name__ == "__main__":
    run_pipeline()
