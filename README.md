# Dubsproj-Geocoder

Automated geocoding pipeline for DUBSPROJ-202603001. This project processes address data to generate geographic coordinates using geocoding services.

## Prerequisites

- Python 3.14 or higher
- Git

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/IviweBooi/dubsproj-geocoder.git
   cd dubsproj-geocoder
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     .\.venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Setup

- Ensure your virtual environment is activated before running any scripts.
- Place input data in the `data/` directory.
- Logs will be generated in the `logs/` directory.
- Reports will be output to the `reports/` directory.

