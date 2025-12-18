# services/media_management/tag_ai.py
from __future__ import annotations
import os
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")


import os
from typing import List
from PIL import Image

# ----- CONFIG -----
TAGGING_MODE = "clip"  # "blip", "clip", or "simple". Use "clip" for now to avoid BLIP issues.

# Torch is optional; used for speed if present
try:
    import torch  # noqa
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    torch = None
    DEVICE = "cpu"

# Lazy globals
blip_processor = blip_model = None
clip_processor = clip_model = None


def _lazy_import_blip():
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration  # type: ignore
        return BlipProcessor, BlipForConditionalGeneration
    except Exception:
        return None, None


def _lazy_import_clip():
    # Prefer explicit CLIPProcessor/CLIPModel, else Auto*
    try:
        from transformers import CLIPProcessor, CLIPModel  # type: ignore
        return ("direct", CLIPProcessor, CLIPModel)
    except Exception:
        try:
            from transformers import AutoProcessor, AutoModel  # type: ignore
            return ("auto", AutoProcessor, AutoModel)
        except Exception:
            return (None, None, None)


# ----- BLIP Setup -----
def init_blip():
    global blip_processor, blip_model
    if blip_processor is not None and blip_model is not None:
        return
    BlipProcessor, BlipForConditionalGeneration = _lazy_import_blip()
    if BlipProcessor is None or BlipForConditionalGeneration is None:
        raise ImportError("BLIP is not available in your transformers install.")
    print("🔍 Loading BLIP model...")
    blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    if torch is not None:
        blip_model = blip_model.to(DEVICE)


# ----- CLIP Setup -----
def init_clip():
    global clip_processor, clip_model
    if clip_processor is not None and clip_model is not None:
        return

    mode, P, M = _lazy_import_clip()
    if mode is None:
        raise ImportError("CLIP is not available in your transformers install.")

    print("🔍 Loading CLIP model...")
    if mode == "direct":
        clip_processor = P.from_pretrained("openai/clip-vit-base-patch32")
        clip_model = M.from_pretrained("openai/clip-vit-base-patch32")
    else:  # auto
        clip_processor = P.from_pretrained("openai/clip-vit-base-patch32")
        clip_model = M.from_pretrained("openai/clip-vit-base-patch32")

    if torch is not None:
        clip_model = clip_model.to(DEVICE)


# ----- Public API -----
def generate_tags(image_path: str) -> List[str]:
    """
    Returns list of tags based on mode:
      - "blip": caption → tokens
      - "clip": zero-shot ranking over fixed vocab
      - "simple": filename heuristics
    """
    try:
        if TAGGING_MODE == "blip":
            try:
                init_blip()
            except Exception as e:
                print(f"⚠️ BLIP unavailable, falling back to CLIP/simple: {e}")
                return _tags_clip_or_simple(image_path)

            raw_image = Image.open(image_path).convert("RGB")
            inputs = blip_processor(raw_image, return_tensors="pt")
            if torch is not None:
                inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

            out = blip_model.generate(**inputs, max_new_tokens=32)
            try:
                caption = blip_processor.decode(out[0], skip_special_tokens=True)
            except Exception:
                caption = blip_processor.batch_decode(out, skip_special_tokens=True)[0]

            caption = (caption or "").lower().strip()
            return caption.split(", ") if "," in caption else caption.split()

        if TAGGING_MODE == "clip":
            return _tags_clip(image_path)

        if TAGGING_MODE == "simple":
            return _tags_simple(image_path)

        return []
    except Exception as e:
        print(f"⚠️ Tag generation failed: {e}")
        return []


# ----- Helpers -----
def _tags_clip_or_simple(image_path: str) -> List[str]:
    tags = _tags_clip(image_path)
    return tags if tags else _tags_simple(image_path)


def _tags_clip(image_path: str) -> List[str]:
    candidate_tags = [
        "woman", "man", "pink", "lace", "lingerie", "body", "smile",
        "close-up", "group", "indoor", "outdoor", "handbag", "phone", "jeans"
    ]
    try:
        init_clip()
    except Exception as e:
        print(f"⚠️ CLIP unavailable, falling back to simple: {e}")
        return _tags_simple(image_path)

    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(text=candidate_tags, images=image, return_tensors="pt", padding=True)
    if torch is not None:
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with (torch.no_grad() if torch is not None else _nullcontext()):
        outputs = clip_model(**inputs)
        logits = outputs.logits_per_image  # [1, num_tags]
        probs = logits.softmax(dim=1)[0].tolist() if torch is not None else logits[0].tolist()

    idxs = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:5]
    return [candidate_tags[i] for i in idxs]


def _tags_simple(image_path: str) -> List[str]:
    basename = os.path.basename(image_path).lower()
    guesses = []
    for tag in ["rose", "erin", "becky", "pink", "breasts", "bum", "lace"]:
        if tag in basename:
            guesses.append(tag)
    return guesses


class _nullcontext:
    def __enter__(self): return None
    def __exit__(self, *exc): return False
