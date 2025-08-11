import os
import sys
import tempfile

from unidecode import unidecode
from openai import OpenAI

import extract_first_page_of_pdf

client = OpenAI()

api_key = os.getenv("OPENAI_API_KEY")


def get_affiliations(pdf_path: str) -> list[tuple[str, str]]:
    """
    Sends the extracted text from the first page of a PDF file to the OpenAI API to get the affiliation.

    Args:
        pdf (str): The path to the input PDF file.

    Returns:
        str: The affiliation extracted from the PDF.
    """

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        temp_pdf_path = tmp.name
        extract_first_page_of_pdf.extract_first_page_of_pdf(pdf_path, temp_pdf_path)
        file = client.files.create(file=open(tmp.name, "rb"), purpose="user_data")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "file", "file": {"file_id": file.id}},
                    {
                        "type": "text",
                        "text": (
                            "Return the following data ONLY. For this PDF, for each author, on one line:\n"
                            " 1. The author name.\n"
                            " 2. A separator, specifically: '---'\n"
                            ' 3. The author\'s "main" affiliation. If multiple affiliations are present but no clear main one, just return the first one. Include the city name and country.\n'
                            "Separate each author's data with a newline."
                        ),
                    },
                ],
            }
        ],
    )
    client.files.delete(file.id)

    results = []
    for line in str(response.choices[0].message.content).splitlines():
        if line.strip():
            parts = line.split("---")
            assert len(parts) == 2
            if len(parts) == 2:
                # OpenAI sometimes returns weird unicode characters.
                # Use unidecode to convert them to ASCII.
                author_name = unidecode(parts[0].strip())
                affiliation = unidecode(parts[1].strip())
                results.append((author_name, affiliation))

    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_affiliation.py <input_pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    affiliations = get_affiliations(pdf_path)
    print(f"Affiliations extracted from {pdf_path}:")
    for i, (author_name, affiliation) in enumerate(affiliations):
        print(f" {i + 1}. {author_name}: {affiliation}")
