import PyPDF2


# Define a function to parse a PDF file
def parse_pdf(file_path):
    pdf_file = open(file_path, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    text = ''
    for page_number in range(number_of_pages):
        page = read_pdf.getPage(page_number)
        page_content = page.extractText()
        text += page_content
    return text

# Define a function to parse an EPUB file


# Example usage:
pdf_file_path = "example.pdf"

pdf_text = parse_pdf(pdf_file_path)

print(pdf_text)

