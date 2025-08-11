import sys

import psycopg2

from get_coords_from_affiliation import get_coords_from_affiliation
from database_connection import open_connection


def insert_affiliation(cursor: psycopg2.extensions.cursor, affiliation: str) -> None:
    """
    Handle the conflict when inserting an affiliation into the database.
    If the affiliation already exists, ask user whether to update the coordinates

    Args:
        cursor: The database cursor.
        affiliation: The affiliation to handle.
    """
    coords = get_coords_from_affiliation(affiliation)

    cursor.execute(
        "SELECT latitude, longitude FROM affiliations WHERE affiliation_name = %s",
        (affiliation,),
    )
    existing_coords = cursor.fetchone()

    # If affiliation exists in database.
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
    if len(sys.argv) != 2:
        print("Usage: python coords_entry.py <affiliation>")
        sys.exit(1)

    conn = open_connection()
    cursor = conn.cursor()
    insert_affiliation(cursor, sys.argv[1])
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
