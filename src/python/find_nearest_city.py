import os
import sys
import csv
from geometric_median import get_geometric_median_from_file
from geopy.distance import geodesic  # type: ignore


def find_nearest_city(target_coords: tuple[float, float]) -> dict[str, str | float]:
    cities_path = os.path.join(os.path.dirname(__file__), "worldcities.csv")
    with open("worldcities.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        cities = list(reader)

    nearest_city = None
    min_distance = float("inf")
    for city in cities:
        city_coords = (float(city["lat"]), float(city["lng"]))
        distance = geodesic(target_coords, city_coords).miles

        if distance < min_distance:
            min_distance = distance
            nearest_city = city

    if nearest_city is None:
        return {}

    return {
        "city": nearest_city["city"],
        "country": nearest_city["country"],
        "latitude": nearest_city["lat"],
        "longitude": nearest_city["lng"],
        "distance": min_distance,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_json>")
        sys.exit(1)
    JSON_path = sys.argv[1]
    median_coords, total_distance = get_geometric_median_from_file(JSON_path)
    print(f"Geometric Median Coordinates: {median_coords}")
    city = find_nearest_city(median_coords)
    print(city)
