import sys
import json
import math


def calculate_geometric_median_from_coords(
    coords: list[tuple[float, float]],
) -> tuple[tuple[float, float], float]:
    """
    Calculates the geometric median from a list of coordinates.
    """

    # Initial estimate: centroid
    x = sum(p[0] for p in coords) / len(coords)
    y = sum(p[1] for p in coords) / len(coords)

    # Convergence parameters
    tolerance = 1e-7
    max_iterations = 1000

    for _ in range(max_iterations):
        num_x = 0.0
        num_y = 0.0
        denom = 0.0
        for px, py in coords:
            dist = math.hypot(x - px, y - py)
            # Avoid division by zero
            if dist < tolerance:
                return (px, py), sum(math.hypot(px - cx, py - cy) for cx, cy in coords)
            weight = 1 / dist
            num_x += px * weight
            num_y += py * weight
            denom += weight

        new_x = num_x / denom
        new_y = num_y / denom

        if math.hypot(new_x - x, new_y - y) < tolerance:
            x, y = new_x, new_y
            break

        x, y = new_x, new_y

    total_distance = sum(math.hypot(x - px, y - py) for px, py in coords)
    return (x, y), total_distance


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
