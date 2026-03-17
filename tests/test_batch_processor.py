import unittest
import os
import pandas as pd
import sys
from unittest.mock import patch

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from batch_processor import process_csv

class TestBatchProcessor(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "temp_test_data")
        os.makedirs(self.test_dir, exist_ok=True)
        self.input_csv = os.path.join(self.test_dir, "input.csv")
        self.output_csv = os.path.join(self.test_dir, "output.csv")

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.input_csv):
            os.remove(self.input_csv)
        if os.path.exists(self.output_csv):
            os.remove(self.output_csv)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    @patch('batch_processor.geocode_address')
    def test_process_csv_success(self, mock_geocode):
        # Mock geocoder response
        mock_geocode.return_value = {
            "latitude": -33.9567,
            "longitude": 18.4675,
            "location_type": "AMENITY",
            "status": "success",
            "cleaned_address": "Mocked Address",
            "match_level": "exact",
            "source": "api"
        }

        # Create sample input CSV
        input_df = pd.DataFrame({
            "DID Number": ["TEST001"],
            "Country": ["South Africa"],
            "Province": ["Western Cape"],
            "Street Address": ["15 Long Street"],
            "Suburb/Area": ["Cape Town"]
        })
        input_df.to_csv(self.input_csv, index=False)

        # Run processor
        process_csv(self.input_csv, self.output_csv)

        # Verify output file exists
        self.assertTrue(os.path.exists(self.output_csv))

        # Verify output content
        output_df = pd.read_csv(self.output_csv)
        self.assertIn("Latitude", output_df.columns)
        self.assertIn("Longitude", output_df.columns)
        self.assertIn("Location_Type", output_df.columns)
        self.assertIn("Match_Level", output_df.columns)
        
        self.assertEqual(output_df.iloc[0]["Latitude"], -33.9567)
        self.assertEqual(output_df.iloc[0]["DID Number"], "TEST001")

    def test_process_csv_missing_file(self):
        with self.assertLogs('batch_processor', level='ERROR') as cm:
            process_csv("non_existent.csv", self.output_csv)
            self.assertTrue(any("Input file not found" in msg for msg in cm.output))

    def test_process_csv_missing_columns(self):
        # Create CSV with wrong columns
        input_df = pd.DataFrame({"Wrong": ["Data"]})
        input_df.to_csv(self.input_csv, index=False)

        with self.assertLogs('batch_processor', level='ERROR') as cm:
            process_csv(self.input_csv, self.output_csv)
            self.assertTrue(any("Missing columns in CSV" in msg for msg in cm.output))

if __name__ == "__main__":
    unittest.main()
