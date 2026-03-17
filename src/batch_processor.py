"""
batch_processor.py
------------------
DUBSPROJ-202603001 | Task D3.3 - Geocode Addresses to GPS Coordinates

Responsible for reading input CSV files, processing each address 
through the geocoder, and saving the results to a new CSV.

Authors : Iviwe
"""

import os
import pandas as pd
import logging
from geocoder import geocode_address, get_cache_stats

logger = logging.getLogger(__name__)

def process_csv(input_path: str, output_path: str, address_cols: list = None):
    """
    Reads a CSV, geocodes addresses by combining specified columns, and saves the result.
    
    Args:
        input_path: Path to the input CSV file
        output_path: Path where the processed CSV will be saved
        address_cols: List of column names to combine into a single address string.
                      Defaults to ["Street Address", "Suburb/Area", "Province", "Country"]
    """
    if address_cols is None:
        address_cols = ["Street Address", "Suburb/Area", "Province", "Country"]

    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return None

    logger.info(f"Starting batch process: {input_path}")
    
    try:
        # Load the CSV
        df = pd.read_csv(input_path)
        
        # Verify columns exist
        missing_cols = [col for col in address_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing columns in CSV: {missing_cols}")
            return None

        # Prepare results
        results = []
        
        # Process each row
        total_rows = len(df)
        for i, row in df.iterrows():
            logger.info(f"Processing row {i+1}/{total_rows}")
            
            # Combine specified columns into a single comma-separated address string
            address_parts = [str(row[col]).strip() for col in address_cols if pd.notna(row[col])]
            combined_address = ", ".join(address_parts)
            
            res = geocode_address(combined_address)
            results.append(res)

        # Create new columns from results
        df['Latitude'] = [r['latitude'] for r in results]
        df['Longitude'] = [r['longitude'] for r in results]
        df['Location_Type'] = [r['location_type'] for r in results]
        df['Match_Level'] = [r['match_level'] for r in results]

        # Save the result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Batch process complete. Results saved to: {output_path}")
        
        # Calculate summary for the report
        summary = {
            "total": total_rows,
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "exact_matches": sum(1 for r in results if r.get("match_level") == "exact"),
            "fallback_matches": sum(1 for r in results if r.get("match_level") == "fallback"),
            "failed_records": df[df['Latitude'].isna()].copy()
        }
        
        return summary

    except Exception as e:
        logger.error(f"Error during batch processing: {str(e)}")
        return None

if __name__ == "__main__":
    print("Batch processor module loaded. Use process_csv() to process files.")
