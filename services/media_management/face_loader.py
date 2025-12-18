# services/media_management/face_loader.py
import os
import glob
import face_recognition
from typing import List, Tuple

SUPPORTED_EXTS = ('.jpg', '.jpeg', '.png', '.webp')

def _iter_images(root: str):
    """Yield image file paths under root (recursively)."""
    for ext in SUPPORTED_EXTS:
        pattern = os.path.join(root, '**', f'*{ext}')
        for path in glob.iglob(pattern, recursive=True):
            yield path

def load_known_faces(faces_path: str, max_per_person: int = 8) -> Tuple[list, list]:
    """
    Original API (kept for backwards compatibility):
    Expects a structure like:
      faces_path/
        Erin/
          e1.jpg
        Rose/
          r1.png
    """
    encodings, names = [], []
    if not os.path.isdir(faces_path):
        print(f"⚠️ faces_path not found: {faces_path}")
        return encodings, names

    counts = {}
    for person in os.listdir(faces_path):
        person_folder = os.path.join(faces_path, person)
        if not os.path.isdir(person_folder):
            continue
        for file in os.listdir(person_folder):
            if not file.lower().endswith(SUPPORTED_EXTS):
                continue
            if counts.get(person, 0) >= max_per_person:
                continue
            try:
                image = face_recognition.load_image_file(os.path.join(person_folder, file))
                enc = face_recognition.face_encodings(image)
                if enc:
                    encodings.append(enc[0])
                    names.append(person)
                    counts[person] = counts.get(person, 0) + 1
            except Exception as e:
                print(f"⚠️ Face load failed {file}: {e}")
    print(f"✅ Loaded {len(encodings)} face encodings for {len(set(names))} people (from faces_path).")
    return encodings, names

def load_known_faces_from_dirs(face_source_dirs: List[str], max_per_person: int = 8) -> Tuple[list, list]:
    """
    New API:
    Scan arbitrary directories. The person label is taken from the *parent* folder name of each image.
    E.g.: ...\Pictures\The Black Folder\Erin\erin1.jpg -> label 'Erin'
    """
    encodings, names = [], []
    counts = {}

    for base in face_source_dirs or []:
        if not base or not os.path.isdir(base):
            print(f"⚠️ Face source not found: {base}")
            continue
        for img_path in _iter_images(base):
            person = os.path.basename(os.path.dirname(img_path)).strip()
            # Skip generic container names
            if not person or person.lower() in ('pictures', 'camera', 'download', 'downloads', 'dcim'):
                continue
            if counts.get(person, 0) >= max_per_person:
                continue
            try:
                image = face_recognition.load_image_file(img_path)
                faces = face_recognition.face_encodings(image)
                if faces:
                    encodings.append(faces[0])
                    names.append(person)
                    counts[person] = counts.get(person, 0) + 1
            except Exception as e:
                print(f"⚠️ Face load failed {img_path}: {e}")

    print(f"✅ Loaded {len(encodings)} face encodings for {len(set(names))} people (from dirs).")
    return encodings, names
