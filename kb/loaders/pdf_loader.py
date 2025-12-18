from pypdf import PdfReader

def load_pdf(path):
    reader = PdfReader(str(path))
    texts = []
    for i, page in enumerate(reader.pages):
        t = page.extract_text() or ""
        if t.strip():
            texts.append({"text": t, "source": str(path), "page": i+1, "type":"pdf"})
    return texts
