# kb/rag_tool.py
from sentence_transformers import SentenceTransformer
from .store import VectorStore
from .ingest import embed

EMB = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
STORE = VectorStore()

def rag_answer(payload: dict) -> str:
    q = payload.get("text","")
    if not q:
        return "What should I look up?"
    qv = EMB.encode([q], convert_to_numpy=True, normalize_embeddings=True)
    hits = STORE.search(qv, k=6)[0]
    # Simple synthesis (replace with your NLG or LLM):
    context = "\n\n".join(h["text"][:800] for h in hits)
    return f"Hereâ€™s what I found:\n\n{context[:1600]}\n\nâ€” sources: " + ", ".join(set(h['meta'].get('source','') for h in hits))[:300]
