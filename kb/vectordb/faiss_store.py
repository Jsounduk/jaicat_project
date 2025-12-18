from kb.config import INDEX_DIR, DOCSTORE_DIR, EMBEDDING_MODEL
from kb.vectordb.faiss_store import FAISSStore
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(EMBEDDING_MODEL)
db = FAISSStore(index_dir=INDEX_DIR, docstore_dir=DOCSTORE_DIR)

def ask_kb(query: str):
    docs = db.similarity_search(query, k=3, embedder=model)
    return "\n".join([d.page_content for d in docs])
