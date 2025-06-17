import os
from PyPDF2 import PdfReader, PdfWriter

pdf_files = [] # List of PDF files to process. How do we want to access them long-term? For now, I created a path for a folder in my local directory


# Adds all .pdf files in the PDFs folder to the list
for filename in os.listdir("./sample PDFs"): #CHANGE PATH TO YOUR LOCAL DIRECTORY
    if filename.endswith(".pdf"):
        pdf_files.append(filename)

print(pdf_files)

for pdf in pdf_files:
    base_name = pdf.replace('.pdf','')
    pdf_path = os.path.join("./sample PDFs", pdf)
    reader = PdfReader(pdf_path)
    writer = PdfWriter()  

    writer.add_page(reader.pages[0])
    
    with open(f'extracted PDFs/first_page {pdf}'.format(base_name), 'wb') as output_pdf:
        writer.write(output_pdf)
    print(f"First page of {pdf} saved as 'first_page_{base_name}.pdf'")  