"""
geocoder.py
-----------
DUBSPROJ-202603001 | Task D3.3 - Geocode Addresses to GPS Coordinates

Responsible for sending cleaned address strings to the Nominatim
geocoding API and returning latitude, longitude and location_type.

Respects Nominatim's usage policy:
  - 1 request per second maximum
  - Results are cached to avoid duplicate API calls
  - Single threaded, single machine only

Author : Iviwe
"""

import time
import logging
import backoff
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from preprocessor import clean_address


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Nominatim client
# ---------------------------------------------------------------------------
geolocator = Nominatim(user_agent="dubsproj-geocoder-d3.3")


# ---------------------------------------------------------------------------
# Cache :stores already geocoded addresses to avoid duplicate API calls
# key   : cleaned address string
# value : result dictionary with lat, lng, location_type
# ---------------------------------------------------------------------------
_cache: dict = {}


# ---------------------------------------------------------------------------
# Core geocoding function
# ---------------------------------------------------------------------------
@backoff.on_exception(
    backoff.expo,                                    # exponential wait between retries
    (GeocoderTimedOut, GeocoderServiceError),        # only retry on these errors
    max_tries=3,                                     # give up after 3 attempts
    on_backoff=lambda details: logger.warning(       # log every retry attempt
        f"Retrying geocode - attempt {details['tries']} "
        f"after {details['wait']:.1f}s wait"
    )
)
def _call_nominatim(address: str):
    """
    Makes a single request to the Nominatim API.
    The @backoff decorator handles retrying automatically on failure.
    Prefixed with _ to signal this is an internal/private function -
    only geocode_address() should call this directly.
    """
    return geolocator.geocode(address, addressdetails=True, timeout=10)


def geocode_address(address: str) -> dict:
    """
    Main geocoding function. Takes a raw address string, cleans it,
    checks the cache, calls Nominatim if needed, and returns a result dict.

    Args:
        address: Raw address string from the CSV

    Returns:
        {
            "latitude"      : float or None,
            "longitude"     : float or None,
            "location_type" : str or None,
            "status"        : "success" or "failed",
            "cleaned_address": str or None
        }
    """
    # Build the default result dictionary
    result = {
        "latitude"        : None,
        "longitude"       : None,
        "location_type"   : None,
        "status"          : "failed",
        "cleaned_address" : None
    }

    # Clean the address using preprocessor
    cleaned = clean_address(address)
    if cleaned is None:
        logger.warning(f"Skipping empty address: {repr(address)}")
        return result
    
    result["cleaned_address"] = cleaned

    # Check cache before hitting the API
    if cleaned in _cache:
        logger.info(f"Cache hit: {cleaned}")
        return _cache[cleaned]

    # Call Nominatim (with retry logic via @backoff decorator)
    try:
        location = _call_nominatim(cleaned)

        # Handle no result found (valid response but address not found)
        if location is None:
            logger.warning(f"No result found for: {cleaned}")
            _cache[cleaned] = result        # cache the failure too so we don't retry
            return result

        # Extract what we need from the response
        result["latitude"]       = location.latitude
        result["longitude"]      = location.longitude
        result["location_type"]  = _extract_location_type(location)
        result["status"]         = "success"

        logger.info(f"Geocoded: {cleaned} -> ({location.latitude}, {location.longitude})")

    except Exception as e:
        # Catch anything backoff couldn't handle after max retries
        logger.error(f"Failed to geocode: {cleaned} | Error: {str(e)}")

    # Store in cache regardless of success or failure
    _cache[cleaned] = result

    # Enforce Nominatim's 1 request per second rule
    time.sleep(1)

    return result


def _extract_location_type(location) -> str:
    """
    Extracts the location_type from the Nominatim response.
    This is the confidence indicator - tells the Data Team how
    precise the coordinate is.

    Possible values from Nominatim:
        "house"         -> matched to a specific building (most precise)
        "highway"       -> matched to a street
        "suburb"        -> matched to a suburb
        "city"          -> matched to a city (least precise)

    Falls back to the raw 'type' field if 'addresstype' is missing,
    and to "UNKNOWN" if neither is available.
    """
    raw = location.raw.get("addresstype") or location.raw.get("type") or "UNKNOWN"
    return raw.upper()


def get_cache_stats() -> dict:
    """
    Returns a summary of cache usage.
    Useful for the summary report in batch_processor.py.

    Returns:
        {
            "total_cached"  : int,
            "successful"    : int,
            "failed"        : int
        }
    """
    # Count successful and failed geocodings
    successful = sum(1 for r in _cache.values() if r["status"] == "success")
    failed     = sum(1 for r in _cache.values() if r["status"] == "failed")

    return {
        "total_cached" : len(_cache),
        "successful"   : successful,
        "failed"       : failed
    }