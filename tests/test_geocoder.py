import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append('src')

from geocoder import (
    geocode_address,
    _extract_location_type,
    get_cache_stats,
    _cache
)


class TestGeocoder(unittest.TestCase):

    def setUp(self):
        # Clear cache before each test
        _cache.clear()

    def tearDown(self):
        # Clear cache after each test
        _cache.clear()

    def test_extract_location_type_with_addresstype(self):
        mock_location = MagicMock()
        mock_location.raw = {"addresstype": "house"}
        result = _extract_location_type(mock_location)
        self.assertEqual(result, "HOUSE")

    def test_extract_location_type_with_type(self):
        mock_location = MagicMock()
        mock_location.raw = {"type": "highway"}
        result = _extract_location_type(mock_location)
        self.assertEqual(result, "HIGHWAY")

    def test_extract_location_type_fallback(self):
        mock_location = MagicMock()
        mock_location.raw = {}
        result = _extract_location_type(mock_location)
        self.assertEqual(result, "UNKNOWN")

    def test_get_cache_stats_empty(self):
        stats = get_cache_stats()
        self.assertEqual(stats["total_cached"], 0)
        self.assertEqual(stats["successful"], 0)
        self.assertEqual(stats["failed"], 0)

    def test_get_cache_stats_with_data(self):
        _cache["addr1"] = {"status": "success"}
        _cache["addr2"] = {"status": "success"}
        _cache["addr3"] = {"status": "failed"}
        stats = get_cache_stats()
        self.assertEqual(stats["total_cached"], 3)
        self.assertEqual(stats["successful"], 2)
        self.assertEqual(stats["failed"], 1)

    @patch('geocoder.geolocator.geocode')
    @patch('time.sleep')
    def test_geocode_address_success(self, mock_sleep, mock_geocode):
        mock_location = MagicMock()
        mock_location.latitude = -26.2041
        mock_location.longitude = 28.0473
        mock_location.raw = {"addresstype": "house"}
        mock_geocode.return_value = mock_location

        result = geocode_address(
            "12 Main St, Sandton, Gauteng, 2196, South Africa")

        self.assertEqual(result["latitude"], -26.2041)
        self.assertEqual(result["longitude"], 28.0473)
        self.assertEqual(result["location_type"], "HOUSE")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["cleaned_address"],
                         "12 Main St, Sandton, Gauteng, 2196, South Africa")
        mock_geocode.assert_called_once()
        mock_sleep.assert_called_once_with(1)

    @patch('geocoder.geolocator.geocode')
    def test_geocode_address_no_result(self, mock_geocode):
        mock_geocode.return_value = None

        result = geocode_address("Invalid Address")

        self.assertIsNone(result["latitude"])
        self.assertIsNone(result["longitude"])
        self.assertIsNone(result["location_type"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["cleaned_address"], "Invalid Address, South Africa")
        self.assertIn("Invalid Address, South Africa", _cache)

    @patch('geocoder.geolocator.geocode')
    @patch('time.sleep')
    def test_geocode_address_cache_hit(self, mock_sleep, mock_geocode):
        # First call
        mock_location = MagicMock()
        mock_location.latitude = 1.0
        mock_location.longitude = 2.0
        mock_location.raw = {"addresstype": "city"}
        mock_geocode.return_value = mock_location

        result1 = geocode_address("Cached Address")
        self.assertEqual(result1["status"], "success")

        # Second call should use cache
        mock_geocode.reset_mock()
        mock_sleep.reset_mock()

        result2 = geocode_address("Cached Address")
        self.assertEqual(result2["status"], "success")
        self.assertEqual(result1, result2)
        mock_geocode.assert_not_called()
        mock_sleep.assert_not_called()

    @patch('geocoder.geolocator.geocode')
    def test_geocode_address_empty_input(self, mock_geocode):
        result = geocode_address("")
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["cleaned_address"])
        mock_geocode.assert_not_called()

    @patch('geocoder.geolocator.geocode')
    def test_geocode_address_none_input(self, mock_geocode):
        result = geocode_address(None)
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["cleaned_address"])
        mock_geocode.assert_not_called()

    @patch('geocoder.geolocator.geocode')
    @patch('geocoder.logger')
    def test_geocode_address_exception(self, mock_logger, mock_geocode):
        mock_geocode.side_effect = Exception("API Error")

        result = geocode_address("Error Address")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["cleaned_address"], "Error Address, South Africa")
        mock_logger.error.assert_called_once()

    @patch('geocoder.geolocator.geocode')
    @patch('geocoder.logger')
    @patch('time.sleep')
    def test_retry_logic(self, mock_sleep, mock_logger, mock_geocode):
        from geopy.exc import GeocoderTimedOut
        mock_geocode.side_effect = [
            GeocoderTimedOut,
            GeocoderTimedOut,
            MagicMock(
                latitude=1.0,
                longitude=2.0,
                raw={"addresstype": "suburb"}
            )
        ]

        result = geocode_address("Retry Address")

        self.assertEqual(result["status"], "success")
        self.assertEqual(mock_geocode.call_count, 3)
        self.assertEqual(mock_logger.warning.call_count, 2)  # for retries
        mock_sleep.assert_called()


if __name__ == '__main__':
    unittest.main()
