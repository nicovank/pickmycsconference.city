import extract_first_page_of_pdf  # type: ignore
from PyPDF2 import PdfReader  # type: ignore
import os
from openai import OpenAI  # type: ignore
import sys

client = OpenAI()

api_key = os.getenv("OPENAI_API_KEY")


def extract_text(pdf_path: str) -> str:
    """
    Extracts text from the first page of a PDF file.

    Args:
        pdf (str): The path to the input PDF file.

    Returns:
        str: The extracted text.
    """

    reader = PdfReader(pdf_path)
    return reader.pages[0].extract_text()


def get_affiliation(text: str) -> str:
    """
    Sends the extracted text from the first page of a PDF file to the OpenAI API to get the affiliation.

    Args:
        pdf (str): The path to the input PDF file.

    Returns:
        str: The affiliation extracted from the PDF.
    """

    response = client.responses.create(
        model="gpt-3.5-turbo",
        instructions="Extract each author's affiliation from the following text on a new line. If no affiliation is found, skip that author. If there are multiple affiliations, separate them with a semicolon.",
        input=text,
    )

    return response.output_text


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_affiliation.py <input_pdf_path> <output_pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    extract_first_page_of_pdf.extract_first_page_of_pdf(pdf_path, output_path)
    text = extract_text(output_path)
    affiliation = get_affiliation(text)
    print(f"Affiliation extracted from {pdf_path}:\n{affiliation}")
