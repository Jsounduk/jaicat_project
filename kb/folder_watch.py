# kb/folder_watch.py
import os, time, traceback
from pathlib import Path
from kb.ingest import embed, load_pdf, load_text, load_epub, ocr_image
from kb.store import VectorStore

# Optional: Add new loaders here
EXTENSION_LOADER_MAP = {
    ".pdf": load_pdf,
    ".txt": load_text,
    ".epub": load_epub,
    ".jpg": ocr_image,
    ".jpeg": ocr_image,
    ".png": ocr_image,
}

WATCH_DIR = Path("kb/incoming")
PROCESSED_DIR = Path("kb/processed")
WATCH_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

store = VectorStore()


def scan_and_ingest():
    for file in WATCH_DIR.glob("*.*"):
        try:
            ext = file.suffix.lower()
            loader = EXTENSION_LOADER_MAP.get(ext)
            if not loader:
                print(f"[skip] Unsupported file type: {file.name}")
                continue

            print(f"[load] {file.name} using {loader.__name__}")
            docs = loader(file)
            if not isinstance(docs, list):
                docs = [docs]
            
            texts = [doc["text"] for doc in docs if doc.get("text")]
            vectors = embed(texts)

            for i in range(len(docs)):
                docs[i]["meta"] = docs[i].get("meta", {})
                docs[i]["meta"]["source"] = str(file.name)

            store.add(vectors, docs)

            dest = PROCESSED_DIR / file.name
            file.rename(dest)
            print(f"[done] Moved to {dest}")

        except Exception as e:
            print(f"[error] {file.name}: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    print("ðŸ“ Watching folder for new knowledge drops...")
    while True:
        scan_and_ingest()
        time.sleep(10)  # scan every 10 seconds
