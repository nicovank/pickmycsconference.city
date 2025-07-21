import psycopg2
from get_coords_from_affiliation import get_coords_from_affiliation


# sample affiliations
list_of_affiliations = [
    "Umass Amherst",
    "Villanova University",
    "University of Wisconsin-Madison",
    "Oxford University",
    "Kyoto University",
]


def handle_conflict(cursor, coords, affiliation) -> None:
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

    if existing_coords:
        print(
            f"Affiliation '{affiliation}' already exists with coordinates {existing_coords}."
        )
        update = input("Do you want to update the coordinates? (y/n): ").strip().lower()
        if update == "y":
            # Update the coordinates in the database
            cursor.execute(
                "UPDATE affiliations SET latitude = %s, longitude = %s, manually_edited = TRUE WHERE affiliation_name = %s",
                (coords["latitude"], coords["longitude"], affiliation),
            )
            print(f"Updated coordinates for {affiliation}.")
        # If the user does not want to update, do nothing
    else:
        cursor.execute(
            "INSERT INTO affiliations (affiliation_name, latitude, longitude, manually_edited) VALUES (%s, %s, %s, FALSE)",
            (affiliation, coords["latitude"], coords["longitude"]),
        )
        print(f"Inserted new affiliation: {affiliation} with coordinates {coords}.")


def main() -> None:
    # Connect to the database
    conn = psycopg2.connect(
        database="urv",
        host="157.230.67.84",
        user="urv",
        password="urv-summer-2025",
        port=5432,
    )

    cursor = conn.cursor()

    """TABLE affiliations
        affiliation_name VARCHAR(255) PRIMARY KEY,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        manually_edited BOOLEAN DEFAULT FALSE NOT NULL
    """

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
