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
    conference: str
    year: int


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
        # If the request fails, print why and just return an e mpty list
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
        if ee_tag and "doi.org" in ee_tag.text:
            return ee_tag.text

        title = soup.find("title")
        conference_short_name = soup.find("booktitle")
        year = soup.find("year")

        if title and conference_short_name and year:
            return {
                "doi": ee_tag.text,
                "title": title.text,
                "conference": conference_short_name.text,
                "year": int(year.text),
            }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching XML for {pub_id}: {e}")

    return None


def ensure_conference_exists(cur: Cursor, conference_name: str, year: int) -> None:
    """
    Ensures the conference and its specific year happening exist in the database(foreign key constraints).
    """
    try:
        # 1. Insert into the main 'conferences' table
        # If the conference short name already exists, this does nothing.
        cur.execute(
            "INSERT INTO conferences (short_name) VALUES (%s) ON CONFLICT (short_name) DO NOTHING;",
            (conference_name,),
        )
        # 2. Insert into the 'conference_happenings' table
        # If the name and year exists, this does nothing.
        cur.execute(
            "INSERT INTO conference_happenings (conference_short_name, year) VALUES (%s, %s) ON CONFLICT (conference_short_name, year) DO NOTHING;",
            (conference_name, year),
        )
    except Exception as e:
        print(f"Error during conference insertion: {e}")
        # We might want to stop the whole process if this fails
        raise e


def insert_paper(cur: Cursor, paper: PaperDetails) -> bool:
    """
    Inserts a paper into the database. Skips insertion if the DOI already exists.
    Returns True if a new record was inserted, False otherwise.
    """
    sql = """
        INSERT INTO papers (doi, title, conference_short_name, conference_year)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (doi) DO NOTHING;
    """
    # skipping duplicates with the ON CONFLICT clause

    try:
        cur.execute(
            sql,
            (
                paper["doi"],
                paper["title"],
                paper["conference"],
                paper["year"],
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
        description="Scrape dblp conference page to fill the database with DOI, title, year, conf_name"
    )
    parser.add_argument(
        "--conference",
        required=True,
        help="The short name of the conference (e.g., 'OSDI')",
    )
    parser.add_argument(
        "--year",
        required=True,
        type=int,
        help="The year of the conference (e.g., 2025)",
    )
    parser.add_argument("--url", required=True, help="The dblp.org URL to scrape")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
