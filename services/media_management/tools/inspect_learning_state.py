# tools/inspect_learning_state.py
import os, json, glob
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root
mm = ROOT / "services" / "media_management"
logs = mm / "datasets" / "logs"

def count_lines(p):
    try:
        return sum(1 for _ in open(p, "r", encoding="utf-8"))
    except Exception:
        return 0

def read_json(p, default=None):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [] if default is None else default

faces = list((mm / "faces").glob("*.npy"))
print(f"Faces encodings: {len(faces)} files in {mm/'faces'}")

tll = mm / "tag_learning_log.json"
clusters = mm / "tag_clusters.json"
regions = mm / "region_annotations.json"
embeds = mm / "region_embeddings.json"

print(f"Tag learning log: {tll} -> {'exists' if tll.exists() else 'missing'}")
print(f"Tag clusters:      {clusters} -> {'exists' if clusters.exists() else 'missing'}")
print(f"Region annots:     {regions} -> {'exists' if regions.exists() else 'missing'}")
print(f"Region embeds:     {embeds} -> {'exists' if embeds.exists() else 'missing'}")

# Tag stats
tags_counter = Counter()
log_data = read_json(tll)
for row in log_data:
    for t in row.get("tags", []):
        tags_counter[t] += 1
print(f"Tag examples in log: {sum(tags_counter.values())} (unique tags: {len(tags_counter)})")
for tag, c in tags_counter.most_common(10):
    print(f"  {tag:20s} {c}")

# Embedding/region stats
region_data = read_json(regions)
print(f"Region annotations: {len(region_data)}")
embed_data = read_json(embeds)
print(f"Region embeddings:  {len(embed_data)}")

# JSONL logs
for name in ("detections.jsonl", "segments.jsonl", "poses.jsonl", "nsfw.jsonl"):
    p = logs / name
    print(f"{name:17s}: {count_lines(p)} lines {'(present)' if p.exists() else '(missing)'}")
