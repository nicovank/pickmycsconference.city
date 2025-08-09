import argparse
import time
from typing import Optional
import requests
from bs4 import BeautifulSoup
from database_connection import open_connection
from psycopg2.extensions import cursor as Cursor
from typing import Optional, TypedDict


class PaperDetails(TypedDict):
    doi: str
    title: str
    dblp_xml_url: str
    authors: list[str]


# This function grabs main page and takes all the publication IDs from it
# Its like a first step to get the list of things we need to look up later


def get_publication_ids(url: str) -> list[str]:
    """
    Scrapes the given dblp.org URL to extract publication IDs.
    """
    try:
        # Pretend we're a browser so the site is ok with our request

        response: requests.Response = requests.get(
            url, headers={"User-Agent": "My-DOI-Scraper/1.0"}
        )
        # Cathes error if the page is broken or something (like a 404 error)

        response.raise_for_status()
        # If we get rate limited
        # HTML into BeautifulSoup

        thing: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

        ids: list[str] = []
        # The IDs are in <li> tags with class="entry" and an id attribute
        # This loops through every single one it finds on the page

        for entry in thing.find_all("li", class_="entry", id=True):
            ids.append(entry["id"])
        return ids
    except requests.exceptions.RequestException as e:
        # If the request fails, print why and just return an empty list

        print(f"Error fetching the URL: {e}")
        return []


def get_details_from_xml(pub_id: str) -> Optional[PaperDetails]:
    """
    Fetches the XML data for a publication and extracts the DOI.
    """
    xml_url: str = f"https://dblp.org/rec/{pub_id}.xml"
    try:
        response: requests.Response = requests.get(
            xml_url, headers={"User-Agent": "My-DOI-Scraper/1.0"}
        )

        if response.status_code == 429:
            retry_after: int = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return get_details_from_xml(pub_id)  # Retry the request
        response.raise_for_status()

        soup: BeautifulSoup = BeautifulSoup(response.content, "xml")

        ee_tag = soup.find("ee")
        title = soup.find("title")
        authors = [author.get_text(strip=True) for author in soup.find_all("author")]

        if not authors:
            print(f"No author found: https://dblp.org/rec/{pub_id}.xml")
            return None

        if title and ee_tag:
            doi = ee_tag.text
            assert doi.startswith("https://doi.org/")
            doi = doi[16:]
            return {
                "doi": doi,
                "title": title.text,
                "dblp_xml_url": xml_url,
                "authors": authors,
            }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching XML for {pub_id}: {e}")
    return None


def ensure_conference_exists(
    cur: Cursor, conference_name: str, year: int, latitude: str, longitude: str
) -> None:
    """
    Ensures the conference and its specific year happening exist in the database(foreign key constraints).
    """
    try:
        sql = """
            INSERT INTO conference_happenings (conference_short_name, year, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (conference_short_name, year) DO NOTHING;
        """
        # ON CONFLICT (conference_short_name, year) DO UPDATE SET
        #       latitude = EXCLUDED.latitude,
        #       longitude = EXCLUDED.longitude;

        cur.execute(
            sql,
            (conference_name, year, latitude, longitude),
        )
    except Exception as e:
        print(f"Error during conference insertion: {e}")
        # We might want to stop the whole process if this fails

        raise e


def insert_paper(
    cur: Cursor, paper: PaperDetails, conf_name: str, conf_year: int
) -> bool:
    """
    Inserts a paper into the database. Skips insertion if the DOI already exists.
    Returns True if a new record was inserted, False otherwise.
    """
    sql = """
        INSERT INTO papers (doi, title, conference_short_name, conference_year, dblp_xml_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (doi) DO NOTHING;
    """
    # skipping duplicates with the ON CONFLICT clause

    try:
        cur.execute(
            sql,
            (
                paper["doi"],
                paper["title"],
                conf_name,
                conf_year,
                paper["dblp_xml_url"],
            ),
        )
        return cur.rowcount > 0
    except Exception as e:
        print(f"Error during paper insertion: {e}")
        return False


def main() -> None:
    """
    Main function to run the scraper and save the DOIs to a file.
    """
    parser = argparse.ArgumentParser(
        description="Scrape dblp conference page to fill the database 'conference' and 'papers' tables"
    )
    parser.add_argument(
        "--conference",
        required=True,
        help="The short name of the conference",
    )
    parser.add_argument(
        "--year",
        required=True,
        type=int,
        help="The year of the conference",
    )
    parser.add_argument(
        "--latitude",
        required=True,
        help="The latitude of the conference location (listed on their website)",
    )
    parser.add_argument(
        "--longitude",
        required=True,
        help="The longitude of the conference location (listed on their website)",
    )
    parser.add_argument("--url", required=True, help="The full dblp.org URL to scrape.")
    args = parser.parse_args()

    conn = None
    try:
        conn = open_connection()
        cur = conn.cursor()
        print("Connected to DB")

        ensure_conference_exists(
            cur, args.conference, args.year, args.latitude, args.longitude
        )
        conn.commit()

        print(f"Scraping publication IDs from: {args.url}")
        publication_ids = get_publication_ids(args.url)

        if not publication_ids:
            print("No publication IDs found")
            return
        print(
            f"Found {len(publication_ids)} publications. Starting to scrape for details"
        )

        inserted_count = 0
        skipped_exist_count = 0
        skipped_xmlfetch_count = 0

        for i, pub_id in enumerate(publication_ids):
            print(f"Processing {i + 1}/{len(publication_ids)}")
            paper_details = get_details_from_xml(pub_id)

            if paper_details:
                if insert_paper(cur, paper_details, args.conference, args.year):
                    print(f"Inserted new paper: {paper_details['doi']}")
                    inserted_count += 1
                else:
                    print(f"Skipped (already exists): {paper_details['doi']}")
                    skipped_exist_count += 1
            else:
                print(f"Skipped (Couldn't fetch details from XML)")
                skipped_xmlfetch_count += 1
            time.sleep(1)
        conn.commit()

        print(f"New papers inserted: {inserted_count}")
        print(f"Papers skipped (already in DB): {skipped_exist_count}")
        print(f"Papers skipped (XML fetch issue): {skipped_xmlfetch_count}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("DB connection closed")


if __name__ == "__main__":
    main()
