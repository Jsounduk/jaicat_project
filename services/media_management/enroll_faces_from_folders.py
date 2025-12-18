import os
import json
import hashlib
import time
from typing import Dict, Any, Tuple, List

# 3rd party
from PIL import Image  # noqa: F401  # kept for future, we don't open images here
import face_recognition  # only called after we decide to process

# --- CONFIG ---
PICTURES_ROOT = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\Pictures\The Black Folder"
FACES_PATH = "services/media_management/faces"
TAG_LOG_PATH = "services/media_management/tag_learning_log.json"
ENROLL_INDEX_PATH = os.path.join(FACES_PATH, "enrollment_index.json")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif")

# Behavior knobs
FORCE_RESCAN = False            # True => process everything again (ignores index)
RESCAN_IF_CHANGED = False       # True => if size/mtime changed, reprocess; False => skip strictly by path
MAX_FACES_PER_IMAGE = None      # or an int (e.g., 3) to limit saved encodings per image


# ---------------------
# util/fs helpers
# ---------------------
def ensure_dir(d: str):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def norm_key(path: str) -> str:
    """Normalize path for case-insensitive filesystems (Windows)."""
    return os.path.normcase(os.path.abspath(path))


def file_sig(path: str) -> Tuple[int, int]:
    """Return a cheap signature: (size, mtime_ns). Does NOT open/download the file."""
    st = os.stat(path)
    return int(st.st_size), int(st.st_mtime_ns)


def stable_sha1_bytes(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


# ---------------------
# persistence helpers
# ---------------------
def safe_load_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            return json.loads(txt) if txt else default
    except Exception:
        return default


def safe_write_json(path: str, data):
    ensure_dir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def load_index() -> Dict[str, Any]:
    """
    Index shape:
    {
      "by_path": {
        "<normpath>": {
           "sig": [size, mtime_ns],
           "person": "Erin",
           "n_faces": 2,
           "face_files": ["services/media_management/faces/Erin_<sha1>.npy", ...],
           "ts": 1700000000
        },
        ...
      }
    }
    """
    idx = safe_load_json(ENROLL_INDEX_PATH, {})
    if "by_path" not in idx or not isinstance(idx["by_path"], dict):
        idx["by_path"] = {}
    return idx


def update_index(index: Dict[str, Any], image_path: str, sig: Tuple[int, int], person: str, face_files: List[str]):
    index["by_path"][norm_key(image_path)] = {
        "sig": list(sig),
        "person": person,
        "n_faces": len(face_files),
        "face_files": face_files,
        "ts": int(time.time()),
    }


def save_face_encodings(encodings, name: str) -> List[str]:
    """
    Save each encoding to FACES_PATH with a stable sha1-based filename.
    Returns list of file paths written (skips if already exists).
    """
    import numpy as np
    ensure_dir(FACES_PATH)
    out_files = []
    count = 0
    for enc in encodings:
        if MAX_FACES_PER_IMAGE is not None and count >= MAX_FACES_PER_IMAGE:
            break
        arr = np.asarray(enc, dtype="float32")
        fid = stable_sha1_bytes(arr.tobytes())  # stable per vector content
        out_path = os.path.join(FACES_PATH, f"{name}_{fid}.npy")
        if not os.path.exists(out_path):
            np.save(out_path, arr)
        out_files.append(out_path)
        count += 1
    return out_files


def update_tag_log(image_path: str, tags: List[str], folder: str):
    """
    Append an entry if one with same image+folder+tags doesn't already exist.
    """
    if not tags:
        return
    if not folder:
        folder = os.path.dirname(image_path)

    data = safe_load_json(TAG_LOG_PATH, [])
    key_img = norm_key(image_path)
    key_folder = norm_key(folder)
    key_tags = tuple(sorted(tags))

    for row in data:
        if (norm_key(row.get("image", "")) == key_img and
            norm_key(row.get("folder", "")) == key_folder and
            tuple(sorted(row.get("tags", []))) == key_tags):
            return  # already logged

    data.append({
        "image": image_path,
        "folder": folder,
        "tags": list(tags)
    })
    safe_write_json(TAG_LOG_PATH, data)


# ---------------------
# main
# ---------------------
def enroll_all_deep(pictures_root=PICTURES_ROOT):
    index = load_index()
    scanned = 0
    skipped = 0
    changed = 0
    total_faces = 0

    for root, _, files in os.walk(pictures_root):
        for file in files:
            if not file.lower().endswith(IMAGE_EXTS):
                continue
            img_path = os.path.join(root, file)
            npath = norm_key(img_path)

            # Person's name is first folder under the black folder
            rel = os.path.relpath(img_path, pictures_root)
            parts = rel.split(os.sep)
            if len(parts) < 2:
                continue  # Skip files not in a subfolder
            person = parts[0].strip()
            if not person:
                continue

            try:
                if not FORCE_RESCAN:
                    # Early path-level skip (no file open, so no OneDrive download)
                    cached = index["by_path"].get(npath)
                    if cached and not RESCAN_IF_CHANGED:
                        skipped += 1
                        continue

                    if cached and RESCAN_IF_CHANGED:
                        sig_now = file_sig(img_path)
                        if tuple(cached.get("sig", [])) == sig_now:
                            skipped += 1
                            continue
                        # else: changed -> rescan
                        changed += 1
                        sig = sig_now
                    else:
                        sig = file_sig(img_path)
                else:
                    sig = file_sig(img_path)

                # Only now do we open the image (may download OneDrive placeholder)
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image) or []
                face_files = save_face_encodings(encodings, person)
                total_faces += len(face_files)

                # tag log: add the person tag for this image into that person's folder
                update_tag_log(img_path, [person], os.path.join(pictures_root, person))

                # index update
                update_index(index, img_path, sig, person, face_files)
                scanned += 1

                print(f"✅ Enrolled {person} from {file} ({len(face_files)} face vectors)")
            except Exception as e:
                print(f"⚠️ Failed to process {img_path}: {e}")

    # persist index
    safe_write_json(ENROLL_INDEX_PATH, index)
    print(f"\n🎉 Deep scan complete. Scanned: {scanned}, Skipped: {skipped}, Rescanned (changed): {changed}, Faces saved: {total_faces}")


if __name__ == "__main__":
    ensure_dir(FACES_PATH)
    enroll_all_deep()
