import fitz


def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from every page of a PDF.
    """

    pdf_document = fitz.open(
        stream= uploaded_file.read(), 
        filetype= "pdf")

    extracted_text = ""

    for page in pdf_document:
        extracted_text += page.get_text()

    pdf_document.close()

    return extracted_text