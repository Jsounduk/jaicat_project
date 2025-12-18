from pathlib import Path
from .config import INDEX_DIR, DOCSTORE_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from .vectordb.faiss_store import FAISSStore
from .loaders.pdf_loader import load_pdf
from .loaders.epub_loader import load_epub
from .loaders.text_loader import load_text
from .ocr.tesseract import ocr_image
from .loaders.youtube_loader import load_youtube
from .loaders.web_loader import load_url
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(EMBEDDING_MODEL)

def ingest_file(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        docs = load_pdf(file_path)
    elif ext == ".txt":
        docs = load_text(file_path)
    elif ext == ".epub":
        docs = load_epub(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        docs = ocr_image(file_path)
    else:
        raise Exception("Unsupported file type")

    db = FAISSStore(index_dir=INDEX_DIR, docstore_dir=DOCSTORE_DIR)
    db.add_documents(docs, embedder=model)
