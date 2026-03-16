import sys
import os

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from geocoder import geocode_address

def test_real_calls():
    """
    Test the geocoder with real South African addresses to verify 
    integration with the live Nominatim API.
    """
    test_addresses = [
        "University of Cape Town, Rondebosch",
        "Sandton City, Sandton, GP",
        "uShaka Marine World, Durban",
        "121 Castle St, Cape Town Central",
        "Parliament of South Africa, Cape Town",
        "R514 Dyalvane Street, Khayelitsha, 7784, Cape Town"
    ]
    
    print("\n--- Starting Real Geocoding Integration Test ---\n")
    print("Note: This will take a few seconds due to the 1-second rate limit.\n")
    
    results = []
    
    for addr in test_addresses:
        result = geocode_address(addr)
        results.append(result)

    print("\n--- Running Again to Test Cache ---\n")
    for addr in test_addresses:
        result = geocode_address(addr)

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nTest Summary: {success_count}/{len(test_addresses)} addresses successfully geocoded.")

if __name__ == "__main__":
    test_real_calls()
