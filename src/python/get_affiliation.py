import extract_first_page_of_pdf
import os
from openai import OpenAI  # type: ignore
import sys
import tempfile
from typing import IO


client = OpenAI()

api_key = os.getenv("OPENAI_API_KEY")


def get_affiliations(pdf: str) -> str:
    """
    Sends the extracted text from the first page of a PDF file to the OpenAI API to get the affiliation.

    Args:
        pdf (str): The path to the input PDF file.

    Returns:
        str: The affiliation extracted from the PDF.
    """

    file = client.files.create(file=open(pdf, "rb"), purpose="user_data")

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
                            "For each author, extract the affiliation. Seperate each author's affiliations with a new line."
                            "Do not include the author's name. "
                            "If there is no affiliation, skip."
                            "If there are multiple affiliations, separate them with a comma."
                        ),
                    },
                ],
            }
        ],
    )
    client.files.delete(file.id)

    return str(response.choices[0].message.content).strip()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_affiliation.py <input_pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        temp_pdf_path = tmp.name
        extract_first_page_of_pdf.extract_first_page_of_pdf(pdf_path, temp_pdf_path)
        tmp.flush()
        affiliation = get_affiliations(tmp.name)
        print(f"Affiliation extracted from {pdf_path}:\n{affiliation}")
