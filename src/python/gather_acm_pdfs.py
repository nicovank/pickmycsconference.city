import argparse
import pywinauto  # type: ignore
import time

from database_connection import open_connection

BROWSER_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"

# Note: this script works better with an empty downloads directory.
# It could maybe be extended to specify a different output directly.


def download_pdf(url: str, name: str) -> None:
    pywinauto.application.Application().start(f'"{BROWSER_PATH}" --new-window {url}')
    time.sleep(3)

    pywinauto.keyboard.send_keys("^s")
    time.sleep(1)

    pywinauto.keyboard.send_keys(name, with_spaces=True)
    time.sleep(1)

    pywinauto.keyboard.send_keys("{ENTER}")
    time.sleep(1)

    pywinauto.keyboard.send_keys("^w")


def main(args: argparse.Namespace) -> None:
    connection = open_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT doi FROM papers WHERE conference_short_name = %s AND conference_year = %s",
        (args.conference, args.year),
    )
    for entry in cursor.fetchall():
        doi = entry[0]
        doi = doi[16:]  # TODO: Maybe we shouldn't save that https://doi.org part.
        download_pdf(f"https://dl.acm.org/doi/pdf/{doi}", f"{doi.replace('/', '_')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conference", type=str, required=True)
    parser.add_argument("--year", type=int, required=True)
    main(parser.parse_args())
