import requests
from bs4 import BeautifulSoup
import os
import time
from typing import List, Optional, Tuple

# This function grabs main page and takes all the publication IDs from it
# Its like a first step to get the list of things we need to look up later
def get_publication_ids(url: str) -> List[str]:
    """
    Scrapes the given dblp.org URL to extract publication IDs.
    """
    try:
        # Pretend we're a browser so the site is ok with our request
        response: requests.Response = requests.get(url, headers={'User-Agent': 'My-DOI-Scraper/1.0'})
        # Cathes error if the page is broken or something (like a 404 error)
        response.raise_for_status()
        # If we get rate limited
        # HTML into BeautifulSoup
        thing: BeautifulSoup = BeautifulSoup(response.content, 'html.parser')

        ids: List[str] = []
        # The IDs are in <li> tags with class="entry" and an id attribute
        # This loops through every single one it finds on the page
        for entry in thing.find_all('li', class_='entry', id=True):
            ids.append(entry['id'])
        return ids
    
    except requests.exceptions.RequestException as e:
        # If the request fails, print why and just return an empty list
        print(f"Error fetching the URL: {e}")
        return []

# This function takes one of those IDs from the first step,
# goes to its special XML page, and tries to find the DOI.
def get_doi_from_xml(pub_id: str) -> Optional[str]:
    """
    Fetches the XML data for a publication and extracts the DOI.
    """
    xml_url: str = f"https://dblp.org/rec/{pub_id}.xml"
    try:
        response: requests.Response = requests.get(xml_url, headers={'User-Agent': 'My-DOI-Scraper/1.0'})

        if response.status_code == 429:
            retry_after: int = int(response.headers.get('Retry-After', 5))
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return get_doi_from_xml(pub_id) # type: ignore # Retry the request

        response.raise_for_status()

        soup: BeautifulSoup = BeautifulSoup(response.content, 'xml')

        ee_tag = soup.find('ee')
        if ee_tag and 'doi.org' in ee_tag.text:
            return ee_tag.text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching XML for {pub_id}: {e}")

    return None

def main() -> None:
    """
    Main function to run the scraper and save the DOIs to a file.
    """
    target_url: str = "https://dblp.org/db/conf/sigsoft/fse2024c.html"
    output_file: str = "dois.txt"

    print(f"Scraping publication IDs from: {target_url}")
    publication_ids: List[str] = get_publication_ids(target_url)

    if not publication_ids:
        print("No publication IDs found. Exiting.")
        return

    print(f"Found {len(publication_ids)} publications. Fetching DOIs...")

    all_dois: List[str] = []
    for pub_id in enumerate(publication_ids):
        doi: Optional[str] = get_doi_from_xml(pub_id)
        if doi:
            print(f"Found DOI for {pub_id}: {doi}")
            all_dois.append(doi)
        else:
            print(f"DOI not found for {pub_id}")

        # Respectful delay between requests
        time.sleep(2) # Wait for 2 seconds before the next request

    if all_dois:
        with open(output_file, 'w') as f:
            for doi in all_dois:
                f.write(f"{doi}\n")
        print(f"\nSuccessfully extracted {len(all_dois)} DOIs to {os.path.abspath(output_file)}")
    else:
        print("\nNo DOIs were extracted.")

if __name__ == "__main__":
    main()