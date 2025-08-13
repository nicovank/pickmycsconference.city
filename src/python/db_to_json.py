import json
import os
import psycopg2
from database_connection import open_connection
from find_nearest_city import find_nearest_city
from geometric_median import calculate_geometric_median_from_coords

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "www", "data")


def generate_json_for_frontend() -> None:
    """
    Generates a JSON file for each conference and saves it to src/www/data/
    """
    conn = None
    try:
        # os.makedirs(OUTPUT_DIR, exist_ok=True)

        conn = open_connection()
        cur = conn.cursor()

        # Get all distinct conference short names
        cur.execute("SELECT conference_short_name FROM conference_happenings;")
        conference_names = [row[0] for row in cur.fetchall()]
        print(f"Found conferences: {conference_names}")

        # Loop through each conference
        for conf_name in conference_names:
            print(f"Conference: {conf_name}...")

            output_data = {"conference_short_name": conf_name, "happenings": []}

            # Get all happenings for the conference
            cur.execute(
                """
                SELECT year, city, latitude, longitude FROM conference_happenings
                WHERE conference_short_name = %s
                ORDER BY year DESC;
            """,
                (conf_name,),
            )
            happenings = cur.fetchall()

            for year, conf_city, conf_lat, conf_lon in happenings:
                # Get all submissions and their locations for the happening

                # TODO this execute statement
                cur.execute(
                    """
                    SELECT author_name, affiliation_name, latitude, longitude
                    FROM paper_affiliations p_a
                    JOIN papers p ON p_a.paper_doi = p.doi
                    JOIN affiliations aff ON p_a.affiliation_name = aff.affiliation_name
                    WHERE p.conference_short_name = %s AND p.conference_year = %s AND aff.latitude IS NOT NULL AND aff.longitude IS NOT NULL;
                """,
                    (conf_name, year),
                )
                all = cur.fetchall()
                coords = [(sub[2], sub[3]) for sub in all]
                suggested_city_name = "Unknown"

                if coords:
                    median_coords_tuple, total_distance = (
                        calculate_geometric_median_from_coords(coords)
                    )
                    nearest_city_info = find_nearest_city(median_coords_tuple)
                    str(suggested_city_name=nearest_city_info.get("city", "Unknown"))

                submissions = []
                for author_name, aff_name, aff_lat, aff_lon in all:
                    submissions.append(
                        {
                            "author_name": author_name,
                            "affiliation_name": aff_name,
                            "location": {"latitude": aff_lat, "longitude": aff_lon},
                        }
                    )

                # Create happening data here
                happening_data = {
                    "year": year,
                    "location": {
                        "city": conf_city,
                        "latitude": conf_lat,
                        "longitude": conf_lon,
                    },
                    "suggested_city": suggested_city_name,
                    "submissions": submissions,
                }
                # Then append it to output_data
                output_data["happenings"].append(happening_data)

            # Write data to JSON file
            output_f = os.path.join(OUTPUT_DIR, f"{conf_name}.json")
            with open(output_f, "w") as f:
                json.dump(output_data, f, indent=4)
            print(f"Data for {conf_name} written to {output_f}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Non database error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    generate_json_for_frontend()