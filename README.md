# Dubsproj-Geocoder

Automated geocoding pipeline for DUBSPROJ-202603001. This project processes address data to generate geographic coordinates using the Nominatim (OpenStreetMap) API.

## Current Project Status

- [x] Virtual Environment Setup (.venv)
- [x] Dependency Management (requirements.txt)
- [x] Address Preprocessing Module
- [x] Geocoding Module with Fallback Strategy
- [x] Unit and Integration Testing
- [x] Batch Processing Logic
- [x] Google Drive Integration
- [x] Execution Summary and Error Reporting (REQ005, REQ006)
- [x] 30-Day Log History (REQ006)

## Features

- **Robust Preprocessing**: Cleans and standardizes South African addresses (province expansion, whitespace normalization, country enforcement).
- **Fallback Strategy**: Automatically retries geocoding at a less specific level (e.g., street level) if the exact address match fails.
- **Smart Caching**: Stores results locally to avoid redundant API calls and respect rate limits.
- **Production Logging**: Detailed logging to both console and `logs/geocoder.log` with a 30-day rotating history.
- **Automated Reporting**: Generates execution summaries and error reports for manual review after every run.
- **Google Drive Integration**: Automated download of input CSVs and upload of results to a specified Google Drive folder.
- **Rate Limit Compliance**: Enforces Nominatim's 1-request-per-second policy.
- **Exponential Backoff**: Automatic retries for transient network or API errors.

## Installation

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/IviweBooi/dubsproj-geocoder.git
   cd dubsproj-geocoder
   ```

2. **Create and Activate Virtual Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Testing

The project includes comprehensive tests to ensure reliability:

### All Tests
Run all unit tests across all modules:
```powershell
pytest tests/test_preprocessor.py tests/test_geocoder.py tests/test_batch_processor.py tests/test_google_drive_service.py
```

### Integration Tests
Verify real-world connectivity with the live Nominatim API:
```powershell
python tests/integration_test_real_api.py
```

## Directory Structure

- `src/`: Core logic ([preprocessor.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/preprocessor.py), [geocoder.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/geocoder.py), [batch_processor.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/batch_processor.py), [google_drive_service.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/google_drive_service.py), [main.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/main.py))
- `tests/`: Unit and integration tests
- `logs/`: Application logs with 30-day rotation (`geocoder.log`)
- `reports/`: Automated execution summaries and error reports
- `data/`: Local storage for input/output CSV files
- `credentials/`: Secure storage for Service Account keys (Git ignored)

## Usage

To run the full pipeline (Download -> Process -> Upload):
```powershell
python src/main.py
```

This will automatically check the configured Google Drive folder for new CSV files, geocode them locally, and upload the results back to the same folder.

Alternatively, you can run the batch processor on local files only:
```powershell
python src/batch_processor.py
```

## Google Drive Integration

The project includes an automated Google Drive integration for downloading and uploading CSV files. To use this feature:

1.  **Set Up Service Account**: Create a Google Cloud project, enable the Drive API, and generate a Service Account JSON key.
2.  **Configure `.env`**: Copy `.env.example` to `.env` and provide the following:
    - `GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE`: Path to your service account JSON file.
    - `GOOGLE_DRIVE_FOLDER_ID`: The ID of the folder you want to use (e.g., `185lQ5PVa3_8E1LWV17VkUSEEX3ZFXqDJ`).
3.  **Permissions**: Share the target Google Drive folder with the service account email.

The `google_drive_service.py` provides functions for listing, downloading, and uploading CSV files.
