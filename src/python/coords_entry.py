import psycopg2
from get_coords_from_affiliation import get_coords_from_affiliation
from database_connection import open_connection


# sample affiliations
list_of_affiliations = [
    "Umass Amherst",
    "Villanova University",
    "University of Wisconsin-Madison",
    "Oxford University",
    "Kyoto University",
]


def handle_conflict(
    cursor: psycopg2.extensions.cursor, coords: tuple[float, float], affiliation: str
) -> None:
    """
    Handle the conflict when inserting an affiliation into the database.
    If the affiliation already exists, ask user whether to update the coordinates

    Args:
        cursor: The database cursor.
        affiliation: The affiliation to handle.
    """
    cursor.execute(
        "SELECT latitude, longitude FROM affiliations WHERE affiliation_name = %s",
        (affiliation,),
    )
    existing_coords = cursor.fetchone()

    # if Affiliation exists in database
    if existing_coords:
        # Do nothing if the coordinates match or if the entry has been manually edited
        if (
            existing_coords[0] == coords[0] and existing_coords[1] == coords[1]
        ) or existing_coords[2] is True:
            print(
                f"Affiliation '{affiliation}' already exists with the same coordinates {existing_coords[0]}, {existing_coords[1]} or has been manually edited."
            )
        else:
            # If coordinates do not match, ask user for confirmation to update
            print(
                f"Affiliation already exists with different coordinates {existing_coords[0]}, {existing_coords[1]}. It attempted to overwrite with {coords[0]}, {coords[1]}."
            )
            latitude = input("Insert latitude: ")
            longitude = input("Insert longitude: ")
            cursor.execute(
                "UPDATE affiliations SET latitude = %s, longitude = %s, manually_edited = TRUE WHERE affiliation_name = %s",
                (latitude, longitude, affiliation),
            )
            print(f"Updated coordinates for {affiliation} to {latitude}, {longitude}.")
    else:
        # If the affiliation does not exist, insert it with the new coordinates
        cursor.execute(
            "INSERT INTO affiliations (affiliation_name, latitude, longitude, manually_edited) VALUES (%s, %s, %s, FALSE)",
            (affiliation, coords[0], coords[1]),
        )
        print(f"Inserted new affiliation: {affiliation} with coordinates {coords}.")


def main() -> None:
    # Connect to the database
    conn = open_connection()

    cursor = conn.cursor()

    for affiliation in list_of_affiliations:
        # Get coordinates from the affiliation

        coords = get_coords_from_affiliation(affiliation)

        # Insert the coordinates into the database
        handle_conflict(cursor, coords, affiliation)
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
