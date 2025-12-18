# kb/store.py
import faiss, numpy as np, os, json
from pathlib import Path

class VectorStore:
    def __init__(self, dir="kb_index"):
        Path(dir).mkdir(parents=True, exist_ok=True)
        self.dir = dir
        self.idx_path = os.path.join(dir, "index.faiss")
        self.meta_path = os.path.join(dir, "meta.json")
        self.index = faiss.IndexFlatIP(384)  # MiniLM dims
        self.meta = []

        if os.path.exists(self.idx_path) and os.path.exists(self.meta_path):
            faiss.read_index(self.idx_path, self.index)
            self.meta = json.load(open(self.meta_path,"r"))

    def add(self, vectors: np.ndarray, docs: list[dict]):
        self.index.add(vectors.astype(np.float32))
        self.meta.extend(docs)
        faiss.write_index(self.index, self.idx_path)
        json.dump(self.meta, open(self.meta_path,"w"))

    def search(self, vectors: np.ndarray, k=5):
        D, I = self.index.search(vectors.astype(np.float32), k)
        results = []
        for row in I:
            hits = [self.meta[i] for i in row if i < len(self.meta)]
            results.append(hits)
        return results
