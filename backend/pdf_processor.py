from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyPDF2"""
    extracted_text = ""

    try:
        with open(file_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text() or ""
                extracted_text += f"--- Page {page_num} ---\n{text}\n"

        body = extracted_text.replace("--- Page", "").strip()
        if len(body) < 50:
            raise ValueError("No readable text found. This may be a scanned PDF.")

        return extracted_text

    except Exception as e:
        raise Exception(f"Error extracting PDF: {e}") from e
