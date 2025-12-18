# services/media_management/people_bodypart_tagger.py
# Identity-aware body-part tagger using MediaPipe Pose (single-person images).
# Produces owner-specific tags and region boxes for logging/learning.

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception:  # mediapipe optional
    mp = None

# Map index -> name for MediaPipe Pose
BODY_PARTS = {
    0: "nose", 1: "left_eye_inner", 2: "left_eye", 3: "left_eye_outer",
    4: "right_eye_inner", 5: "right_eye", 6: "right_eye_outer",
    7: "left_ear", 8: "right_ear", 9: "mouth_left", 10: "mouth_right",
    11: "left_shoulder", 12: "right_shoulder", 13: "left_elbow", 14: "right_elbow",
    15: "left_wrist", 16: "right_wrist", 17: "left_pinky", 18: "right_pinky",
    19: "left_index", 20: "right_index", 21: "left_thumb", 22: "right_thumb",
    23: "left_hip", 24: "right_hip", 25: "left_knee", 26: "right_knee",
    27: "left_ankle", 28: "right_ankle", 29: "left_heel", 30: "right_heel",
    31: "left_foot_index", 32: "right_foot_index"
}

@dataclass
class RegionDet:
    label: str               # e.g., "butt", "face", "torso", "chest"|"breasts"
    owner: Optional[str]     # person name if known
    conf: float
    box_xyxy: Tuple[int, int, int, int]  # (x1,y1,x2,y2) in image pixels

def _safe_box(x1, y1, x2, y2, w, h, pad=4) -> Tuple[int, int, int, int]:
    x1 = max(0, min(x1 - pad, w-1))
    y1 = max(0, min(y1 - pad, h-1))
    x2 = max(0, min(x2 + pad, w-1))
    y2 = max(0, min(y2 + pad, h-1))
    if x2 <= x1: x2 = min(w-1, x1+1)
    if y2 <= y1: y2 = min(h-1, y1+1)
    return int(x1), int(y1), int(x2), int(y2)

def _box_from_points(points: List[Tuple[int,int]], w: int, h: int, pad: int=6):
    if not points:
        return None
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return _safe_box(min(xs), min(ys), max(xs), max(ys), w, h, pad)

def _to_xy(landmark, w, h):
    return int(landmark.x * w), int(landmark.y * h), float(landmark.visibility)

def tag_bodyparts_with_identity(
    image_path: str,
    owner_name: Optional[str],
    nsfw_label: Optional[str] = None,  # "EXPLICIT", "SUGGESTIVE", or None
    min_vis: float = 0.4
) -> Tuple[List[str], List[RegionDet]]:
    """
    Returns:
      tags:      list like ["person", "face", "Samantha_butt", "Samantha_breasts"]
      regions:   list of RegionDet with boxes for logging/learning
    Notes:
      - Designed for single-person images (MediaPipe Pose).
      - If nsfw_label in {"EXPLICIT","SUGGESTIVE"}, chest is labeled "breasts".
    """
    if mp is None:
        return [], []

    image = cv2.imread(image_path)
    if image is None:
        return [], []
    h, w = image.shape[:2]
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pose = mp.solutions.pose
    tags: List[str] = []
    regions: List[RegionDet] = []

    with pose.Pose(static_image_mode=True) as est:
        res = est.process(rgb)
        if not res.pose_landmarks:
            return tags, regions

        lms = res.pose_landmarks.landmark
        pts = {i: _to_xy(lms[i], w, h) for i in range(len(lms))}
        present = {i: (x, y) for i, (x, y, v) in pts.items() if v >= min_vis}

        # Always tag "person"
        if "person" not in tags:
            tags.append("person")

        # --- Face box (use eyes/ears/nose/mouth)
        face_ids = [0,1,2,3,4,5,6,7,8,9,10]
        face_pts = [present[i] for i in face_ids if i in present]
        face_box = _box_from_points(face_pts, w, h, pad=8)
        if face_box:
            regions.append(RegionDet("face", owner_name, 0.9, face_box))
            tags.append("face")
            if owner_name:
                tags.append(f"{owner_name}_face")

        # --- Torso / Chest(Breasts)
        torso_ids = [11,12,23,24]  # shoulders + hips
        torso_pts = [present[i] for i in torso_ids if i in present]
        torso_box = None
        if len(torso_pts) >= 2:
            torso_box = _box_from_points(torso_pts, w, h, pad=10)
            if torso_box:
                regions.append(RegionDet("torso", owner_name, 0.85, torso_box))
                tags.append("torso")
                if owner_name:
                    tags.append(f"{owner_name}_torso")

            # Chest / Breasts as upper half of torso
            x1,y1,x2,y2 = torso_box
            chest_y2 = int(y1 + 0.5*(y2-y1))
            chest_box = _safe_box(x1, y1, x2, chest_y2, w, h, pad=2)
            chest_label = "breasts" if (nsfw_label in {"EXPLICIT","SUGGESTIVE"}) else "chest"
            regions.append(RegionDet(chest_label, owner_name, 0.75, chest_box))
            tags.append(chest_label)
            if owner_name:
                tags.append(f"{owner_name}_{chest_label}")

        # --- Butt (hips to mid-thigh)
        if 23 in present and 24 in present:
            Lhip = present[23]; Rhip = present[24]
            hip_y = int((Lhip[1] + Rhip[1]) / 2)
            # find thighs: use knees if visible, else ankles as fallback
            thigh_y = None
            if 25 in present and 26 in present:
                thigh_y = int((present[25][1] + present[26][1]) / 2)
            elif 27 in present and 28 in present:
                thigh_y = int((present[27][1] + present[28][1]) / 2)
            if thigh_y is None:
                thigh_y = min(h-1, hip_y + int(0.25*h))
            x_left  = min(Lhip[0], Rhip[0]) - int(0.07*w)
            x_right = max(Lhip[0], Rhip[0]) + int(0.07*w)
            y_top   = hip_y - int(0.08*h)
            y_bot   = int(hip_y + 0.55*(thigh_y-hip_y))
            butt_box = _safe_box(x_left, y_top, x_right, y_bot, w, h, pad=4)
            regions.append(RegionDet("butt", owner_name, 0.75, butt_box))
            tags.append("butt")
            if owner_name:
                tags.append(f"{owner_name}_butt")

        # --- Legs (knees/ankles present)
        if (25 in present and 26 in present) or (27 in present and 28 in present):
            tags.append("legs")
            if owner_name:
                tags.append(f"{owner_name}_legs")

        # De-dup while preserving order
        tags = list(dict.fromkeys([t for t in tags if t]))

    return tags, regions
