# Dubsproj-Geocoder: Automated Geocoding Pipeline

**DUBSPROJ-202603001** | This project provides a production-ready, automated pipeline to process South African addresses from CSV files, convert them to geographic coordinates using the Nominatim (OpenStreetMap) API, and synchronize the results with Google Drive.

---

## Final Compliance Audit

This project successfully meets all specified requirements.

| ID | Requirement | Status | Implementation Details |
| :--- | :--- | :--- | :--- |
| **REQ001** | Geocoding Service | **Completed** | Integrated with the free and open-source **Nominatim (OpenStreetMap) API**. |
| **REQ002** | Address Pre-processing | **Completed** | The `preprocessor.py` module cleans addresses by standardizing provinces, normalizing whitespace, and ensuring proper casing. |
| **REQ003** | Batch Processing | **Completed** | The `batch_processor.py` module processes CSVs, respects API rate limits (1/sec), and uses `backoff` for automatic retries. |
| **REQ004** | Accuracy & Confidence | **Completed** | The output CSV includes `location_type` and a custom `match_level` (exact/fallback) to indicate coordinate precision. |
| **REQ005** | Error Handling & Fallback | **Completed** | The pipeline logs all errors, generates a dedicated `errors_*.csv` report for failed records, and uses a fallback strategy for failed lookups. |
| **REQ006** | Logging & Reporting | **Completed** | Implemented a 30-day rotating file logger (`geocoder.log`) and generates a timestamped execution summary after each run. |

---

## Pipeline Workflow

The system is designed for full automation. When `main.py` is executed, it performs the following steps:

1.  **Scan Google Drive**: Connects to the configured Google Drive folder and searches for new `.csv` files to process.
2.  **Download**: Securely downloads each new file to a local `data/` directory.
3.  **Process & Geocode**: For each address, the system performs:
    - **Preprocessing**: Cleans and standardizes the address string.
    - **Cache Check**: Checks if the address has been processed before to avoid redundant API calls.
    - **API Call**: If not cached, sends the request to the Nominatim API.
    - **Fallback Logic**: If the exact address fails, it retries with a broader search (e.g., street/suburb level).
4.  **Generate Output**: Creates a new `geocoded_*.csv` file containing the original data plus the new coordinate and accuracy columns.
5.  **Upload Results**: Uploads the `geocoded_*.csv` file back to the original Google Drive folder.
6.  **Create Reports**: Generates a final `summary_*.txt` and `errors_*.csv` in the local `reports/` directory.

---

## Installation & Configuration

1.  **Clone the Repository**:
    ```powershell
    git clone https://github.com/IviweBooi/dubsproj-geocoder.git
    cd dubsproj-geocoder
    ```

2.  **Setup Python Environment**:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

3.  **Configure Credentials**:
    - Create a `.env` file by copying the `.env.example` template.
    - Place your **Google Service Account JSON key** in the `credentials/` folder.
    - Update the `.env` file with your `GOOGLE_DRIVE_FOLDER_ID` and the path to your service account file.
    - **Crucially**, share your target Google Drive folder with the `client_email` found in your service account JSON file, granting it **Editor** permissions.

---

## Usage

### Run the Full Automated Pipeline
This is the primary method. It handles downloading from Google Drive, processing, and uploading the results.
```powershell
python src/main.py
```

### Run a Local Batch Process Only
Use this if you want to manually place a file in the `data/` folder and process it without cloud interaction.
```powershell
python src/batch_processor.py
```

---

## Testing

The project includes a comprehensive test suite to ensure code quality and reliability.

### Run All Unit Tests
This command runs all 27+ mocked tests without making live API calls.
```powershell
pytest tests/
```

### Run Live Integration Test
This test connects to the real Nominatim API to verify connectivity and geocoding accuracy.
```powershell
python tests/integration_test_real_api.py
```

---

## Project Directory Structure

- `src/`: Core application logic.
  - `main.py`: Main entry point for the automated pipeline.
  - `geocoder.py`: Handles Nominatim API interaction, caching, and fallback logic.
  - `preprocessor.py`: Address cleaning and standardization functions.
  - `batch_processor.py`: CSV reading, processing, and writing.
  - `google_drive_service.py`: Manages Google Drive file operations.
- `tests/`: Unit and integration test files for all modules.
- `logs/`: Contains the rotating `geocoder.log` with a 30-day history.
- `reports/`: Stores timestamped execution summaries and error reports.
- `data/`: Local staging area for CSV files (ignored by Git).
- `credentials/`: Secure storage for the Google Service Account key (ignored by Git).
