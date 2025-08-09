import json
import os
import psycopg2
from database_connection import open_connection

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "www", "data")


def generate_json_for_frontend():
    """
    Generates a JSON file for each conference and saves it to src/www/data/
    """
    conn = None
    try:
        # os.makedirs(OUTPUT_DIR, exist_ok=True)

        conn = open_connection()
        cur = conn.cursor()

        # Get all distinct conference short names
        cur.execute("SELECT DISTINCT conference_short_name FROM conference_happenings;")
        conference_names = [row[0] for row in cur.fetchall()]
        print(f"Found conferences: {conference_names}")

        # Loop through each conference
        for conf_name in conference_names:
            print(f"Conference: {conf_name}...")

            output_data = {
                "conference_short_name": conf_name,
                "happenings": []
            }

            # Get all happenings for the conference
            cur.execute("""
                SELECT year, latitude, longitude FROM conference_happenings
                WHERE conference_short_name = %s
                ORDER BY year DESC;
            """, (conf_name,))
            happenings = cur.fetchall()

            for year, conf_lat, conf_lon in happenings:
                # Get all submissions and their locations for the happening

                # TODO this execute statement
                cur.execute()  

                submissions = []
                for author_name, aff_name, aff_lat, aff_lon in cur.fetchall():
                    submissions.append({
                        "author_name": author_name,
                        "affiliation_name": aff_name,
                        "location": {
                            "latitude": aff_lat,
                            "longitude": aff_lon
                        }
                    })

                # TODO: Create happening data here
                
                # TODO: Then append it to output_data

            # TODO Write data to JSON file

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
