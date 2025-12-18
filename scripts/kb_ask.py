import argparse
from kb.rag.pipeline import RAGPipeline
from openai import OpenAI
import os
from kb.config import INDEX_DIR, DOCSTORE_DIR, EMBEDDING_MODEL
from kb.vectordb.faiss_store import FAISSStore
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(EMBEDDING_MODEL)
db = FAISSStore(index_dir=INDEX_DIR, docstore_dir=DOCSTORE_DIR)

def ask_kb(query: str):
    docs = db.similarity_search(query, k=3, embedder=model)
    return "\n".join([d.page_content for d in docs])



def openai_llm(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--user", default="global")
    args = ap.parse_args()

    rag = RAGPipeline(user=args.user, llm_callable=openai_llm)
    out = rag.ask(args.question)
    print(out["answer"])
    print("\nSources:")
    for h in out["sources"]:
        print(f"- {h['source']} (score {h['score']:.3f})")
