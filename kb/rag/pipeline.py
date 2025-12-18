from textwrap import dedent
from ..vectordb.faiss_store import FAISSStore
from ..config import INDEX_DIR, EMBEDDING_MODEL, TOP_K

class RAGPipeline:
    def __init__(self, user="global", llm_callable=None):
        self.store = FAISSStore(INDEX_DIR / f"{user}.index",
                                INDEX_DIR / f"{user}.meta.json",
                                EMBEDDING_MODEL)
        self.llm = llm_callable

    def ask(self, question: str) -> dict:
        hits = self.store.search(question, top_k=TOP_K)
        context = "\n\n".join(f"[{i+1}] {h['source']}\n{h.get('text','')[:1000]}" for i,h in enumerate(hits))
        prompt = dedent(f"""
        You are a helpful assistant. Answer the user's question using ONLY the context.
        If the answer is uncertain, say you don't know.

        Question: {question}

        Context:
        {context}

        Answer:
        """)
        answer = self.llm(prompt) if self.llm else "LLM not configured."
        return {"answer": answer, "sources": hits}
