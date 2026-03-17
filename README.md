# Dubsproj-Geocoder

Automated geocoding pipeline for DUBSPROJ-202603001. This project processes South African address data to generate geographic coordinates using the Nominatim (OpenStreetMap) API and synchronizes results with Google Drive.

## Current Project Status

- [x] **Virtual Environment Setup** (.venv)
- [x] **Dependency Management** (requirements.txt)
- [x] **Address Preprocessing Module** (Standardization & Cleaning)
- [x] **Geocoding Module** (with Fallback Strategy)
- [x] **Unit & Integration Testing** (27+ tests passing)
- [x] **Batch Processing Logic** (CSV multi-column handling)
- [x] **Google Drive Integration** (Automated Upload/Download)
- [x] **Execution Summary & Error Reporting** (REQ005, REQ006)
- [x] **30-Day Log History** (REQ006: Rotating Logs)

## Features

- **Robust Preprocessing**: Standardizes South African addresses by expanding provinces (e.g., GP -> Gauteng), normalizing whitespace, and enforcing title casing.
- **Fallback Strategy**: If an exact address match fails, the system automatically retries at the street/suburb level to ensure data coverage for the Data Team.
- **Automated Pipeline**: End-to-end flow that downloads new CSVs from Google Drive, processes them locally, and uploads results back to the cloud.
- **Production-Grade Logging**: 30-day rotating logs stored in `logs/geocoder.log` for auditing and troubleshooting.
- **Smart Caching**: Local memory cache prevents redundant API calls, speeding up processing and respecting rate limits.
- **Detailed Reporting**: Generates a text summary and a CSV error report (listing failed addresses) after every execution.

## Installation

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/IviweBooi/dubsproj-geocoder.git
   cd dubsproj-geocoder
   ```

2. **Setup Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Configure Credentials**:
   - Create a `.env` file from `.env.example`.
   - Place your Google Service Account JSON key in the `credentials/` folder.

## Usage

### Run Full Pipeline
To scan Google Drive, process files, and upload results:
```powershell
python src/main.py
```

### Run Local Batch Only
To process a CSV file already in your `data/` folder:
```powershell
python src/batch_processor.py
```

## Testing

### Unit Tests (All Modules)
```powershell
pytest tests/test_preprocessor.py tests/test_geocoder.py tests/test_batch_processor.py tests/test_google_drive_service.py
```

### Live Integration Test
```powershell
python tests/integration_test_real_api.py
```

## Directory Structure

- `src/`: Core source code ([main.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/main.py), [geocoder.py](file:///c:/Users/USER/OneDrive%20-%20University%20of%20Cape%20Town/Documents/Dubs%20Projects/dubsproj-geocoder/src/geocoder.py), etc.)
- `tests/`: Comprehensive test suite.
- `logs/`: Rotating log files (30-day history).
- `reports/`: Execution summaries and error reports.
- `data/`: Local storage for processing files (Git ignored).
- `credentials/`: Secure folder for API keys (Git ignored).
