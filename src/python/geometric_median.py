import sys
import json
import numpy as np
from geopy.distance import geodesic  # type: ignore
from scipy.optimize import minimize

cities = json.loads(open("../www/sample.json").read())


def get_geometric_median(JSON_path: str) -> list:
    """
    Calculate the geometric median of a set of geographical coordinates using the Nelder-Mead algorithm: minimizes sum of distances to all points.

    Args:
        cities (list): A list of dictionaries, each containing latitude and longitude.

    Returns:
        tuple: A tuple containing the latitude and longitude of the geometric median.
    """

    cities = json.loads(open(JSON_path).read())

    coords = [(c["latitude"], c["longitude"]) for c in cities]

    lat0 = np.mean([latitude for latitude, _ in coords])
    lon0 = np.mean([longitude for _, longitude in coords])
    initial_guess = np.array([lat0, lon0])

    def get_total_distance(point: np.ndarray) -> float:
        """
        Calculate the total distance from a point to all coordinates.

        Args:
            point (tuple): A tuple containing latitude and longitude calculated by scipy.optimize.minimize.

        Returns:
            float: The total distance from the point to all coordinates.
        """
        return sum(geodesic(point, coord).miles for coord in coords)

    result = minimize(get_total_distance, initial_guess, method="Nelder-Mead")
    best_point = [float(result.x[0]), float(result.x[1])]
    distance = float(result.fun)
    return [best_point, distance]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_json>")
        sys.exit(1)
    JSON_path = sys.argv[1]
    median_coords, total_distance = get_geometric_median(JSON_path)
    print(f"Geometric Median Coordinates: {median_coords}")
    print(f"Total Distance: {total_distance} miles")
