import sys
import json
import os
import geopy
from geopy.geocoders import GoogleV3

api_key = os.getenv("GEOCODING_API_KEY")
geolocator = GoogleV3(api_key)


def get_coords_from_affiliation(affiliation: str) -> tuple:
    location = geolocator.geocode(affiliation)
    if location:
        return json.dumps(
            {"latitude": location.latitude, "longitude": location.longitude}
        )
    else:
        return json.dumps({"error": "Location not found"})


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_coords_from_affiliation.py <affiliation string>")
        sys.exit(1)
    print(get_coords_from_affiliation(sys.argv[1]))
