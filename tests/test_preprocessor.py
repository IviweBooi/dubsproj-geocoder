import unittest
import sys
sys.path.append('src')
from preprocessor import clean_address

class TestPreprocessor(unittest.TestCase):

    def test_normalize_whitespace(self):
        self.assertEqual(clean_address("  12  Main  St,\n  Johannesburg  "), "12 Main St, Johannesburg, South Africa")
    
    def test_join_multiline(self):
        self.assertEqual(clean_address("12 Main St\nSandton\nJohannesburg"), "12 Main St, Sandton, Johannesburg, South Africa")
    
    def test_expand_province(self):
        self.assertEqual(clean_address("Sandton, GP, 2196"), "Sandton, Gauteng, 2196, South Africa")
        self.assertEqual(clean_address("Cape Town, WC"), "Cape Town, Western Cape, South Africa")
    
    def test_ensure_country(self):
        self.assertEqual(clean_address("12 Main St, Sandton, Gauteng, 2196"), "12 Main St, Sandton, Gauteng, 2196, South Africa")
        self.assertEqual(clean_address("12 Main St, London, UK"), "12 Main St, London, Uk, South Africa")
    
    def test_title_case_address(self):
        self.assertEqual(clean_address("12 main st, sandton, gauteng, 2196, south africa"), "12 Main St, Sandton, Gauteng, 2196, South Africa")
    
    def test_empty_address(self):
        self.assertIsNone(clean_address(""))

    def test_none_address(self):
        self.assertIsNone(clean_address(None))

if __name__ == '__main__':
    unittest.main()