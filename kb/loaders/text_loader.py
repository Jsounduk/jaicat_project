def load_text(path):
    t = open(path, "r", encoding="utf-8", errors="ignore").read()
    return [{"text": t, "source": str(path), "type":"text"}] if t.strip() else []
