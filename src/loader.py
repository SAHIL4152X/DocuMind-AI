from pypdf import PdfReader


def load_pdf(pdf_source):
    reader = PdfReader(pdf_source)

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            documents.append({
                "page": page_number,
                "text": text
            })

    return documents