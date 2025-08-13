import sys
import json
import numpy as np
from geopy.distance import geodesic  # type: ignore
from scipy.optimize import minimize  # type: ignore


def calculate_geometric_median_from_coords(
    coords: list[tuple[float, float]],
) -> tuple[tuple[float, float], float]:
    """
    Calculates the geometric median from a list of coordinates.
    This is the core logic function.
    """
    # Use the average coordinate as the starting point for the optimization
    lat0 = np.mean([latitude for latitude, _ in coords])
    lon0 = np.mean([longitude for _, longitude in coords])
    initial_guess = np.array([lat0, lon0])

    def get_total_distance(point: np.ndarray) -> float:
        """Calculates the sum of geodesic distances from a point to all coordinates."""
        return float(sum(geodesic(point, coord).miles for coord in coords))

    # Find the point that minimizes the total distance
    result = minimize(get_total_distance, initial_guess, method="Nelder-Mead")

    best_point = (float(result.x[0]), float(result.x[1]))
    distance = float(result.fun)
    return (best_point, distance)


def get_geometric_median_from_file(JSON_path: str) -> tuple[tuple[float, float], float]:
    """
    This function handles reading a file and then calls the core logic function.
    It's used when running this script as a standalone tool.
    """
    with open(JSON_path, "r") as f:
        data = json.load(f)

    # Extract coordinates from the JSON data
    coords = [(c["latitude"], c["longitude"]) for c in data]

    # Call the core logic function with the extracted coordinates
    return calculate_geometric_median_from_coords(coords)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_json>")
        sys.exit(1)
    JSON_path = sys.argv[1]
    median_coords, total_distance = get_geometric_median_from_file(JSON_path)
    print(f"Geometric Median Coordinates: {median_coords}")
    print(f"Total Distance: {total_distance} miles")
