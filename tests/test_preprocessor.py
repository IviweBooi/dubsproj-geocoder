import unittest
from preprocessor import clean_address

class TestPreprocessor(unittest.TestCase):

    def test_normalize_whitespace(self):
        self.assertEqual(clean_address("  12  Main  St,\n  Johannesburg  "), "12 Main St, Johannesburg") #output = 12 Main St,, Johannesburg, South Africa' != '12 Main St, Johannesburg' not sure how to fix this, seems like the join_multiline is adding an extra comma after St, not sure why
    
    def test_join_multiline(self):
        self.assertEqual(clean_address("12 Main St\nSandton\nJohannesburg"), "12 Main St, Sandton, Johannesburg") #output is adding south africa at the end of the address, not sure why
    
    def test_expand_province(self):
        self.assertEqual(clean_address("Sandton, GP, 2196"), "Sandton, Gauteng, 2196, South Africa")
        self.assertEqual(clean_address("Cape Town, WC"), "Cape Town, Western Cape, South Africa")
    
    def test_ensure_country(self):
        self.assertEqual(clean_address("12 Main St, Sandton, Gauteng, 2196"), "12 Main St, Sandton, Gauteng, 2196, South Africa")
        self.assertEqual(clean_address("12 Main St, London, UK"), "12 Main St, London, UK") #test fails Uk!=UK for some reason
    
    def test_title_case_address(self):
        self.assertEqual(clean_address("12 main st, sandton, gauteng, 2196, south africa"), "12 Main St, Sandton, Gauteng, 2196, South Africa")
    
    def test_empty_address(self):
        self.assertIsNone(clean_address(""))

    def test_none_address(self):
        self.assertIsNone(clean_address(None))

if __name__ == '__main__':
    unittest.main()