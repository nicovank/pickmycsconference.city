import sys
from pypdf import PdfReader, PdfWriter


def extract_first_page_of_pdf(pdf: str, desired_path: str) -> None:
    """
    Extracts the first page of a PDF file and saves it to a new file.

    Args:
        pdf (str): The path to the input PDF file.
        desired_path (str): The path where the first page will be saved.
    """
dfjkgnbjksndfnjdbf nms
    reader = PdfReader(pdf)
    writer = PdfWriter()
    base_name = pdf.replace(".pdf", "")

    # Add the first page to the writer
    if len(reader.pages) > 0:
        writer.add_page(reader.pages[0])

    # Write the first page to the desired path
    with open(desired_path, "wb") as output_pdf:
        writer.write(output_pdf)
    print(f"First page of {base_name} saved to {desired_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python extract_first_page_of_pdf.py <input_pdf_path> <output_pdf_path>"
        )
        sys.exit(1)
    extract_first_page_of_pdf(sys.argv[1], sys.argv[2])
