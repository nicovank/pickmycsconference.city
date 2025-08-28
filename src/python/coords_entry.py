import sys

import psycopg2

from get_coords_from_affiliation import get_coords_from_affiliation
from database_connection import open_connection


def insert_affiliation(cursor: psycopg2.extensions.cursor, affiliation: str) -> None:
    """
    Insert a new affiliation into the database if not present.

    Args:
        cursor: The database cursor.
        affiliation: The affiliation to handle.
    """
    cursor.execute(
        "SELECT COUNT(*) FROM affiliations WHERE affiliation_name = %s",
        (affiliation,),
    )
    if cursor.fetchone()[0]:
        return

    coords = get_coords_from_affiliation(affiliation)

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
