# Dubsproj-Geocoder

Automated geocoding pipeline for DUBSPROJ-202603001. This project processes address data to generate geographic coordinates using the Nominatim (OpenStreetMap) API.

## Current Project Status

- [x] Virtual Environment Setup (.venv)
- [x] Dependency Management (requirements.txt)
- [x] Address Preprocessing Module
- [x] Geocoding Module with Fallback Strategy
- [x] Unit and Integration Testing
- [ ] Batch Processing Logic (Pending)
- [ ] SharePoint Integration (Pending)

## Features

- **Robust Preprocessing**: Cleans and standardizes South African addresses (province expansion, whitespace normalization, country enforcement).
- **Fallback Strategy**: Automatically retries geocoding at a less specific level (e.g., street level) if the exact address match fails.
- **Smart Caching**: Stores results locally to avoid redundant API calls and respect rate limits.
- **Production Logging**: Detailed logging to both console and `logs/geocoder.log`.
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

### Unit Tests
Run unit tests for preprocessing and geocoding logic:
```powershell
pytest tests/test_preprocessor.py tests/test_geocoder.py
```

### Integration Tests
Verify real-world connectivity with the live Nominatim API:
```powershell
python tests/integration_test_real_api.py
```

## Batch Processing

The batch processor handles CSV files with the following production structure:
- **Columns**: `DID Number`, `Country`, `Province`, `Street Address`, `Suburb/Area`.
- **Combined Geocoding**: Combines street, suburb, province, and country into a single query for maximum precision.

To run the batch processor on your input files:
```powershell
python src/batch_processor.py
```

Results will be saved to `data/geocoded_addresses.csv` with added geocoding metadata.
