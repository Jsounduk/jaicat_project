# services/media_management/bulk_region_learner.py
from __future__ import annotations
import os, sys, json
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import face_recognition

# Reuse your project utilities
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from services.media_management.region_clip_embedder import update_embeddings_for_image
from services.media_management.log_utils import ensure_log_dir, jsonl_append
from services.media_management.unified_image_sorter import load_known_faces  # reuse the same loader
from services.media_management.people_bodypart_tagger import tag_bodyparts_with_identity

FACES_PATH = "services/media_management/faces"
ANNOT_PATH = "services/media_management/region_annotations.json"
LOG_DIR    = "services/media_management/datasets/logs"

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")

def recognize_primary_person(image_path: str,
                             known_encodings: List[np.ndarray],
                             known_names: List[str],
                             tolerance: float = 0.5) -> Optional[str]:
    """
    Returns the first matched name if any; otherwise None.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        encs = face_recognition.face_encodings(image)
        for enc in encs:
            matches = face_recognition.compare_faces(known_encodings, enc, tolerance=tolerance)
            if True in matches:
                return known_names[matches.index(True)]
    except Exception as e:
        print(f"   face-recognition skipped ({e})")
    return None

def _load_annotations() -> List[dict]:
    if not os.path.exists(ANNOT_PATH):
        return []
    try:
        with open(ANNOT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to read {ANNOT_PATH}: {e}")
        return []

def _save_annotations(all_rows: List[dict]) -> None:
    try:
        with open(ANNOT_PATH, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to write {ANNOT_PATH}: {e}")

def _coerce_box_xyxy(r) -> List[int]:
    # Handle both dataclass-like (attrs) and dict-like regions
    box = getattr(r, "box_xyxy", None)
    if box is None and isinstance(r, dict):
        box = r.get("box_xyxy") or r.get("coords")
    if not box:  # last resort
        return [0, 0, 1, 1]
    return [int(round(b)) for b in box]

def _coerce_label(r) -> str:
    lbl = getattr(r, "label", None)
    if lbl is None and isinstance(r, dict):
        lbl = r.get("label") or r.get("tag")
    return (lbl or "").strip()

def _coerce_owner(r) -> Optional[str]:
    owner = getattr(r, "owner", None)
    if owner is None and isinstance(r, dict):
        owner = r.get("owner")
    return owner

def learn_from_folder(train_dir: str,
                      faces_path: str = FACES_PATH,
                      min_conf: float = 0.30) -> None:
    if not os.path.isdir(train_dir):
        print(f"❌ Training folder not found: {train_dir}")
        return

    known_encs, known_names = load_known_faces(faces_path)
    print(f"✅ Faces loaded: {len(known_encs)} encodings for {len(set(known_names))} people.")
    ann = _load_annotations()

    det_path = ensure_log_dir(LOG_DIR) / "detections.jsonl"

    # Gather images
    files = [str(Path(train_dir, f)) for f in os.listdir(train_dir)
             if f.lower().endswith(IMAGE_EXTS)]
    files.sort()
    print(f"📂 Scanning {len(files)} images in {train_dir}")

    for i, img in enumerate(files, 1):
        try:
            # 1) Who's in the photo?
            owner = recognize_primary_person(img, known_encs, known_names, tolerance=0.5)
            # 2) Tag body parts (pass owner so tags/regions carry identity)
            id_tags, id_regions = tag_bodyparts_with_identity(
                image_path=img,
                owner_name=owner,      # None is okay; the tagger may infer or leave blank
                nsfw_label=None        # training pass doesn't need the nsfw fuse
            )

            # 3) Persist region annotations (owner + part)
            new_rows = []
            for r in (id_regions or []):
                box = _coerce_box_xyxy(r)
                label = _coerce_label(r)
                region_owner = _coerce_owner(r) or owner

                # Skip super-low confidence regions if your tagger provides `conf`
                conf = getattr(r, "conf", None)
                if conf is None and isinstance(r, dict):
                    conf = r.get("conf")
                if conf is not None and float(conf) < min_conf:
                    continue

                # Write a human-friendly label used by your UI/suggestions
                if region_owner:
                    ui_label = f"{region_owner} {label}".strip()
                else:
                    ui_label = label

                # region_annotations.json row (used by your existing tools)
                new_rows.append({
                    "image": img,
                    "coords": box,       # [x0,y0,x1,y1]
                    "label": ui_label    # UI label (what you'll see in dropdowns)
                })

            if new_rows:
                ann.extend(new_rows)

                # 4) Log as detections for downstream learning/analytics
                try:
                    jsonl_append(det_path, {
                        "task": "detect",
                        "source": "bulk_region_learner",
                        "model": "mediapipe_pose+rules",
                        "image": img,
                        "boxes_xyxy": [r["coords"] for r in new_rows],
                        "classes": [None] * len(new_rows),
                        "confs": [1.0] * len(new_rows),     # you can pipe real confs if available
                        "labels": [r["label"] for r in new_rows]
                    })
                except Exception as e:
                    print(f"   ⚠️ log failed: {e}")

                # 5) Build/update CLIP region embeddings for this image
                try:
                    update_embeddings_for_image(img)
                except Exception as e:
                    print(f"   ⚠️ embeddings update failed: {e}")

            print(f"[{i}/{len(files)}] {os.path.basename(img)} -> "
                  f"{len(new_rows)} regions ({owner or 'unknown owner'})")

        except KeyboardInterrupt:
            print("⏹️ Stopped by user.")
            break
        except Exception as e:
            print(f"⚠️ Skipped {os.path.basename(img)}: {e}")

    _save_annotations(ann)
    print(f"✅ Done. Regions: {len(ann)} total in {ANNOT_PATH}")
    print(f"   Embeddings updated. Logs at {det_path}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if not target:
        print("Usage: python services/media_management/bulk_region_learner.py <TRAIN_FOLDER>")
        sys.exit(1)
    learn_from_folder(target)
