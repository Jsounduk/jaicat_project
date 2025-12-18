# services/media_management/region_clip_embedder.py
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
from PIL import Image

# Optional torch (for speed/Device placement). Code runs without it.
try:
    import torch  # noqa
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    torch = None
    DEVICE = "cpu"

# ---- Paths ----
ANNOTATIONS_PATH = "services/media_management/region_annotations.json"
EMBEDDINGS_PATH = "services/media_management/region_embeddings.json"

# Lazy globals for transformers CLIP
_clip_processor = None
_clip_model = None
_clip_mode = None  # "direct" or "auto"


# ---------- Utils ----------
def safe_load_json(path: str, default):
    """
    Load JSON; create file with default if missing.
    Returns a deep copy-like structure to avoid accidental mutation.
    """
    p = Path(path)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        # Return a "fresh" default
        return json.loads(json.dumps(default))
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return json.loads(json.dumps(default))


def _lazy_import_clip():
    """
    Try explicit CLIP classes first; fall back to Auto* if needed.
    Returns: (mode, ProcessorClass, ModelClass) or (None, None, None)
    """
    try:
        from transformers import CLIPProcessor, CLIPModel  # type: ignore
        return "direct", CLIPProcessor, CLIPModel
    except Exception:
        try:
            from transformers import AutoProcessor, AutoModel  # type: ignore
            return "auto", AutoProcessor, AutoModel
        except Exception:
            return None, None, None


def _ensure_clip() -> bool:
    """
    Lazy-load a CLIP model if possible.
    Returns True if CLIP is available, else False (fallback will be used).
    """
    global _clip_processor, _clip_model, _clip_mode
    if _clip_processor is not None and _clip_model is not None:
        return True

    mode, P, M = _lazy_import_clip()
    if mode is None:
        print("⚠️ transformers CLIP not available. Using color-hist fallback for embeddings.")
        return False

    print("🔍 Loading CLIP (transformers)...")
    if mode == "direct":
        _clip_processor = P.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model = M.from_pretrained("openai/clip-vit-base-patch32")
    else:
        _clip_processor = P.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model = M.from_pretrained("openai/clip-vit-base-patch32")

    if torch is not None:
        _clip_model = _clip_model.to(DEVICE)

    _clip_mode = mode
    return True


def _normalize(vec: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(vec)) + 1e-8
    return (vec / n).astype(np.float32)


def _embed_color_hist(pil_img: Image.Image) -> np.ndarray:
    """
    Lightweight fallback embedding: concatenated per-channel histograms.
    Deterministic, fast, portable (no transformers needed).
    """
    arr = np.asarray(pil_img.convert("RGB"))
    feats = []
    for ch in range(3):
        h, _ = np.histogram(arr[:, :, ch], bins=64, range=(0, 255), density=True)
        feats.append(h.astype(np.float32))
    return _normalize(np.concatenate(feats))


def _embed_clip(pil_img: Image.Image) -> np.ndarray:
    ok = _ensure_clip()
    if not ok:
        return _embed_color_hist(pil_img)

    # Prepare inputs
    inputs = _clip_processor(text=["a photo"], images=pil_img, return_tensors="pt", padding=True)
    if torch is not None:
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        with torch.no_grad():
            # Prefer official image features; fallback to pooled token output if needed
            if hasattr(_clip_model, "get_image_features"):
                feats = _clip_model.get_image_features(**inputs)  # [1, D]
                vec = feats[0].float().cpu().numpy()
            else:
                outputs = _clip_model(**inputs)
                vec = outputs.last_hidden_state.mean(dim=1)[0].detach().cpu().numpy()
    else:
        # Extremely rare path (no torch): still call model and mean-pool
        outputs = _clip_model(**inputs)
        vec = outputs.last_hidden_state.mean(dim=1)[0].detach().cpu().numpy()

    return _normalize(vec)


def _crop_box(pil_img: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
    x1, y1, x2, y2 = [int(v) for v in box]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = max(x1 + 1, x2), max(y1 + 1, y2)
    return pil_img.crop((x1, y1, x2, y2))


def _resolve_image_key(region: Dict[str, Any]) -> Optional[str]:
    """
    Accept both legacy ('image') and new ('image_path') keys.
    """
    return region.get("image_path") or region.get("image")


# ---------- Public API ----------
def get_region_embedding(image_path: str, coords) -> List[float]:
    """
    Compute (or recompute) a single region embedding.
    Returns a normalized vector (list[float]).
    """
    img = Image.open(image_path).convert("RGB")
    crop = _crop_box(img, coords)
    vec = _embed_clip(crop)
    return vec.tolist()


def main():
    """
    Recompute embeddings for all regions in ANNOTATIONS_PATH and write EMBEDDINGS_PATH.
    Output format: list of entries: {
        "image": <path>,
        "label": <string>,
        "coords": [x1,y1,x2,y2],
        "embedding": [..float..]
    }
    """
    regions = safe_load_json(ANNOTATIONS_PATH, [])
    embedding_entries = []

    for region in regions:
        try:
            img_path = _resolve_image_key(region)
            if not img_path:
                continue
            coords = region.get("coords") or region.get("box") or region.get("bbox")
            if not coords or len(coords) != 4:
                continue
            emb = get_region_embedding(img_path, coords)
            entry = {
                "image": img_path,
                "label": region.get("label", region.get("tag", "")),
                "coords": coords,
                "embedding": emb
            }
            embedding_entries.append(entry)
        except Exception as e:
            try:
                offending = region.get("image") or region.get("image_path") or "unknown"
            except Exception:
                offending = "unknown"
            print(f"⚠️ Failed on {offending}: {e}")

    Path(EMBEDDINGS_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(EMBEDDINGS_PATH).write_text(json.dumps(embedding_entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Region embeddings saved: {EMBEDDINGS_PATH}")


def update_embeddings_for_image(image_path: str):
    """
    Recompute embeddings only for regions that belong to `image_path`.
    Preserves others in EMBEDDINGS_PATH.
    """
    regions = safe_load_json(ANNOTATIONS_PATH, [])
    try:
        all_embeds = safe_load_json(EMBEDDINGS_PATH, [])
    except Exception:
        all_embeds = []

    # keep all entries not for this image
    existing = [e for e in all_embeds if e.get("image") != image_path]
    new_embeds = []

    for region in regions:
        img_path = _resolve_image_key(region)
        if img_path != image_path:
            continue
        coords = region.get("coords") or region.get("box") or region.get("bbox")
        if not coords or len(coords) != 4:
            continue
        try:
            emb = get_region_embedding(img_path, coords)
            entry = {
                "image": img_path,
                "label": region.get("label", region.get("tag", "")),
                "coords": coords,
                "embedding": emb
            }
            new_embeds.append(entry)
        except Exception as e:
            print(f"⚠️ Failed on {img_path}: {e}")

    out = existing + new_embeds
    Path(EMBEDDINGS_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(EMBEDDINGS_PATH).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Embeddings updated for {image_path}")


def ensure_region_embeddings():
    """
    Ensure embedding store exists; build if missing.
    """
    if not Path(EMBEDDINGS_PATH).exists():
        main()


if __name__ == "__main__":
    main()
