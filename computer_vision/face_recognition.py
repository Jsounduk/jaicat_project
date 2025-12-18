# computer_vision/face_recognition.py

import cv2
import face_recognition
import os
import numpy as np
from typing import List, Tuple, Dict, Optional

KNOWN_FACES_DIR = "enrollment_pictures"

def load_known_faces() -> Tuple[List[np.ndarray], List[str]]:
    """
    Load one encoding per file in KNOWN_FACES_DIR.
    Filename (without extension) becomes the label.
    """
    if not os.path.isdir(KNOWN_FACES_DIR):
        return [], []

    known_faces: List[np.ndarray] = []
    names: List[str] = []
    for name in os.listdir(KNOWN_FACES_DIR):
        path = os.path.join(KNOWN_FACES_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if not encs:
                continue
            known_faces.append(encs[0])
            names.append(os.path.splitext(name)[0])
        except Exception:
            # skip unreadable or non-face files silently
            continue
    return known_faces, names

def start_face_recognition():
    """
    Simple webcam demo window. ESC to exit.
    """
    known_faces, names = load_known_faces()
    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for encoding, location in zip(encodings, face_locations):
            results = face_recognition.compare_faces(known_faces, encoding, tolerance=0.5)
            match = "Unknown"

            if True in results:
                match = names[results.index(True)]

            top, right, bottom, left = [i * 4 for i in location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, match, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            print(f"[security] Face detected: {match}")
            if match == "Unknown":
                # avoid importing TTS on import; only when needed at runtime
                try:
                    from utils.speech import Speech
                    Speech().speak("Alert! Unknown person detected.")
                except Exception:
                    pass

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break

    video.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# New: module-level, cached recognizer for programmatic use
# ---------------------------------------------------------------------------

_KNOWN_CACHE: Optional[Tuple[List[np.ndarray], List[str]]] = None

def _get_known() -> Tuple[List[np.ndarray], List[str]]:
    global _KNOWN_CACHE
    if _KNOWN_CACHE is None:
        _KNOWN_CACHE = load_known_faces()
    return _KNOWN_CACHE

def recognize_faces(
    frame_bgr: np.ndarray,
    *,
    scale: float = 0.25,
    tolerance: float = 0.5,
) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    """
    Programmatic face recognizer used by other modules.

    Args:
      frame_bgr: OpenCV BGR frame (np.ndarray)
      scale: downscale factor for speed (0.25 = 1/4 size)
      tolerance: face_recognition.match tolerance (lower = stricter)

    Returns:
      List of (name, (top, right, bottom, left)) in *original* image coords.
      Unknown faces yield name "Unknown".
    """
    if frame_bgr is None or not hasattr(frame_bgr, "shape"):
        return []

    known_faces, names = _get_known()

    # downscale for speed
    if scale != 1.0:
        small = cv2.resize(frame_bgr, (0, 0), fx=scale, fy=scale)
    else:
        small = frame_bgr

    rgb_small = small[:, :, ::-1]
    face_locations_small = face_recognition.face_locations(rgb_small)
    encodings = face_recognition.face_encodings(rgb_small, face_locations_small)

    results: List[Tuple[str, Tuple[int, int, int, int]]] = []
    inv_scale = int(round(1.0 / scale)) if scale != 0 else 1

    for enc, (top, right, bottom, left) in zip(encodings, face_locations_small):
        name = "Unknown"
        if known_faces:
            matches = face_recognition.compare_faces(known_faces, enc, tolerance=tolerance)
            if True in matches:
                name = names[matches.index(True)]

        # scale back up to original frame coords
        top, right, bottom, left = (top * inv_scale, right * inv_scale, bottom * inv_scale, left * inv_scale)
        results.append((name, (top, right, bottom, left)))

    return results
