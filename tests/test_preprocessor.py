import unittest
import sys
import os

# Add src to sys.path to allow importing preprocessor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessor import (
    normalize_whitespace,
    join_multiline,
    expand_province,
    ensure_country,
    title_case_address,
    clean_address
)

class TestPreprocessor(unittest.TestCase):

    def test_normalize_whitespace(self):
        """Test collapsing multiple whitespaces and stripping."""
        self.assertEqual(normalize_whitespace("  12  Main  St  "), "12 Main St")
        self.assertEqual(normalize_whitespace("Sandton\n\nJohannesburg"), "Sandton Johannesburg")
        self.assertEqual(normalize_whitespace("\tCape Town\r\n"), "Cape Town")

    def test_join_multiline(self):
        """Test converting multi-line addresses to comma-separated."""
        address = "12 Main St\nSandton\nJohannesburg"
        self.assertEqual(join_multiline(address), "12 Main St, Sandton, Johannesburg")
        
        # Test with trailing commas in lines
        address_with_commas = "12 Main St,\nSandton,\nJohannesburg"
        self.assertEqual(join_multiline(address_with_commas), "12 Main St, Sandton, Johannesburg")
        
        # Test with empty lines
        address_empty_lines = "12 Main St\n\nSandton\n \nJohannesburg"
        self.assertEqual(join_multiline(address_empty_lines), "12 Main St, Sandton, Johannesburg")

    def test_expand_province(self):
        """Test expanding province abbreviations."""
        self.assertEqual(expand_province("Sandton, GP, 2196"), "Sandton, Gauteng, 2196")
        self.assertEqual(expand_province("Cape Town, WC"), "Cape Town, Western Cape")
        self.assertEqual(expand_province("Durban, KZN"), "Durban, KwaZulu-Natal")
        # Case insensitive
        self.assertEqual(expand_province("Johannesburg, gp"), "Johannesburg, Gauteng")
        # Word boundaries
        self.assertEqual(expand_province("GP Services"), "Gauteng Services")
        self.assertEqual(expand_province("GPT Solutions"), "GPT Solutions") # Should NOT expand GP in GPT

    def test_ensure_country(self):
        """Test appending 'South Africa' if missing."""
        self.assertEqual(ensure_country("12 Main St, Sandton"), "12 Main St, Sandton, South Africa")
        self.assertEqual(ensure_country("12 Main St, South Africa"), "12 Main St, South Africa")
        self.assertEqual(ensure_country("12 Main St, SOUTH AFRICA"), "12 Main St, SOUTH AFRICA")
        # Even if another country is present, append South Africa as per current logic
        self.assertEqual(ensure_country("12 Main St, London, UK"), "12 Main St, London, UK, South Africa")

    def test_title_case_address(self):
        """Test title casing the address string."""
        self.assertEqual(title_case_address("12 main st, sandton"), "12 Main St, Sandton")
        self.assertEqual(title_case_address("CAPE TOWN, WESTERN CAPE"), "Cape Town, Western Cape")
        # Special case for "of" and "the"
        self.assertEqual(title_case_address("CITY OF CAPE TOWN"), "City of Cape Town")
        self.assertEqual(title_case_address("THE SANDTON TOWER"), "the Sandton Tower")

    def test_clean_address_integration(self):
        """Test the master cleaning function with various inputs."""
        # Full integration test
        raw = "  12 main st\nsandton\nGP\n2196  "
        expected = "12 Main St, Sandton, Gauteng, 2196, South Africa"
        self.assertEqual(clean_address(raw), expected)

        # Missing country
        self.assertEqual(clean_address("Cape Town, WC"), "Cape Town, Western Cape, South Africa")

        # Mixed whitespace and tabs
        self.assertEqual(clean_address("12\tMain St"), "12 Main St, South Africa")

    def test_empty_inputs(self):
        """Test handling of empty or None inputs."""
        self.assertIsNone(clean_address(""))
        self.assertIsNone(clean_address(None))
        self.assertIsNone(clean_address("   "))
        self.assertIsNone(clean_address("\n\t"))

if __name__ == '__main__':
    unittest.main()