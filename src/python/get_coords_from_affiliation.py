import sys
import os
from geopy.geocoders import GoogleV3  # type: ignore

api_key = os.getenv("GEOCODING_API_KEY")
geolocator = GoogleV3(api_key)


def get_coords_from_affiliation(affiliation: str) -> tuple[float, float]:
    """
    Get coordinates from an affiliation string using geocoding.

    Args:
        affiliation: The affiliation string to geocode.
    Returns:
        A tuple containing latitude and longitude.
    """

    location = geolocator.geocode(affiliation)
    if location:
        return location.latitude, location.longitude
    else:
        raise Exception("Location not found")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_coords_from_affiliation.py <affiliation string>")
        sys.exit(1)
    print(get_coords_from_affiliation(sys.argv[1]))
