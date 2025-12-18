from pathlib import Path

BASE_DIR = Path(__file__).parent
INDEX_DIR = BASE_DIR / "kb_index"
DOCSTORE_DIR = BASE_DIR / "docstore"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 40
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
