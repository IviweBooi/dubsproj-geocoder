"""
preprocessor.py
---------------
DUBSPROJ-202603001 | Task D3.3 - Geocode Addresses to GPS Coordinates

Responsible for cleaning and standardizing volunteer address strings
before they are sent to the Nominatim geocoding API.

Authors : Iviwe
"""

import re


# ---------------------------------------------------------------------------
# Province abbreviation map (spec REQ002 + D3.2 REQ004)
# Maps common abbreviations to their full official SA province names
# ---------------------------------------------------------------------------
PROVINCE_MAP = {
    "GP":  "Gauteng",
    "WC":  "Western Cape",
    "KZN": "KwaZulu-Natal",
    "EC":  "Eastern Cape",
    "FS":  "Free State",
    "LP":  "Limpopo",
    "MP":  "Mpumalanga",
    "NC":  "Northern Cape",
    "NW":  "North West",
}


def normalize_whitespace(address: str) -> str:
    """
    Remove leading/trailing whitespace and collapse any internal
    sequences of whitespace (spaces, tabs, newlines) into a single space.

    Example:
        "  12  Main  St,\n  Johannesburg  " -> "12 Main St, Johannesburg"
    """
    return re.sub(r"\s+", " ", address.strip())


def join_multiline(address: str) -> str:
    """
    Convert a multi-line address into a single comma-separated string.
    Nominatim expects one continuous string, not line breaks.

    Example:
        "12 Main St\nSandton\nJohannesburg" -> "12 Main St, Sandton, Johannesburg"
    """
    # Split on newlines, strip each part, drop empty parts, rejoin with ", "
    parts = [part.strip().rstrip(", ") for part in address.splitlines()]
    parts = [part for part in parts if part]  # remove empty strings
    return ", ".join(parts)


def expand_province(address: str) -> str:
    """
    Replace known province abbreviations with their full names.
    Only replaces whole words so "GP" inside "GPT Solutions" is not touched.

    Example:
        "Sandton, GP, 2196" -> "Sandton, Gauteng, 2196"
        "Cape Town, WC"     -> "Cape Town, Western Cape"
    """
    for abbr, full in PROVINCE_MAP.items():
        # \b = word boundary ensures we only match the abbreviation standalone
        address = re.sub(rf"\b{abbr}\b", full, address, flags=re.IGNORECASE)
    return address


def ensure_country(address: str) -> str:
    """
    Append ', South Africa' if no country reference is present.
    This greatly improves Nominatim match rates for SA addresses.

    Example:
        "12 Main St, Sandton, Gauteng, 2196" -> "12 Main St, Sandton, Gauteng, 2196, South Africa"
        "12 Main St, London, UK"             -> "12 Main St, London, Uk, South Africa"
    """

    country_hints = ["south africa"]
    lower = address.lower()
    if not any(hint in lower for hint in country_hints):
        address = address.rstrip(", ") + ", South Africa"
    return address


def title_case_address(address: str) -> str:
    """
    Apply title casing to the address while preserving postal codes
    (sequences of digits) and country codes that are already uppercase.

    Example:
        "12 main st, sandton, gauteng, 2196, south africa"
        -> "12 Main St, Sandton, Gauteng, 2196, South Africa"
    """
    # Title-case the whole string first
    address = address.title()
    # Fix "South Africa" casing edge case from title() on mixed strings
    address = address.replace("Of ", "of ").replace("The ", "the ")
    return address


def clean_address(address: str) -> str | None:
    """
    Master cleaning function - runs all steps in the correct order.
    This is the only function that batch_processor.py needs to call.

    Steps:
        1. Return None immediately if the address is empty/missing
        2. Join multi-line address into one string
        3. Normalize whitespace
        4. Expand province abbreviations
        5. Ensure South Africa is appended if no country detected
        6. Apply title casing
        7. Final whitespace cleanup

    Returns:
        Cleaned address string, or None if the input was empty.

    Example:
        raw  = "  12 main st\nsandton\nGP\n2196  "
        clean= "12 Main St, Sandton, Gauteng, 2196, South Africa"
    """
    # guard against empty/None values
    if not address or not str(address).strip():
        return None

    address = str(address)  # ensure string (handles float NaN from pandas)
    address = join_multiline(address)
    address = normalize_whitespace(address)
    address = expand_province(address)
    address = ensure_country(address)
    address = title_case_address(address)
    address = normalize_whitespace(address)

    return address
