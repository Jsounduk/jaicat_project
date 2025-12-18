# services/media_management/yolo_pose.py
from __future__ import annotations
import os
from typing import List, Tuple, Union
import numpy as np
import cv2

# Ultralytics shared API; supports both 11 and 8 via YOLO(...)
from ultralytics import YOLO

# Prefer YOLO11 pose; fall back to YOLOv8 pose if not available
_POSE_WEIGHTS_CANDIDATES = [
    "yolo11n-pose.pt",
    "yolo11s-pose.pt",
    "yolov8n-pose.pt",
    "yolov8s-pose.pt",
]

_YOLO_MODEL = None
_YOLO_WEIGHTS = None


def _first_existing(weights_list) -> str | None:
    for w in weights_list:
        # YOLO will auto-download if not present, but we keep the order explicit
        return w
    return None


def load_model(device: str | None = None, imgsz: int = 640):
    """
    Loads a YOLO pose model once and caches it.
    Order: YOLO11 pose -> YOLOv8 pose.
    """
    global _YOLO_MODEL, _YOLO_WEIGHTS
    if _YOLO_MODEL is not None:
        return _YOLO_MODEL

    weights = _first_existing(_POSE_WEIGHTS_CANDIDATES)
    if weights is None:
        raise RuntimeError("No pose weights configured.")

    _YOLO_MODEL = YOLO(weights)
    _YOLO_WEIGHTS = weights
    # device/imgsz are passed at predict time in Ultralytics; we store for reference
    _YOLO_MODEL.__dict__.setdefault("_jaicat_device", device)
    _YOLO_MODEL.__dict__.setdefault("_jaicat_imgsz", imgsz)
    return _YOLO_MODEL


def _to_bgr(image_or_path: Union[str, np.ndarray]) -> np.ndarray:
    if isinstance(image_or_path, str):
        img = cv2.imread(image_or_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to read image: {image_or_path}")
        return img
    elif isinstance(image_or_path, np.ndarray):
        # assume already BGR
        return image_or_path
    else:
        raise TypeError("Expected file path or np.ndarray(BGR).")


def detect_pose(image_or_path: Union[str, np.ndarray],
                conf: float = 0.25) -> List[np.ndarray]:
    """
    Returns a list of keypoint arrays, each shaped (K, 2) float64.
    Works with YOLO11-pose or YOLOv8-pose.
    """
    model = load_model()
    device = getattr(model, "_jaicat_device", None)
    imgsz = getattr(model, "_jaicat_imgsz", 640)

    # Ultralytics accepts file paths or numpy arrays directly
    results = model.predict(
        source=image_or_path,
        conf=conf,
        verbose=False,
        device=device,
        imgsz=imgsz
    )

    poses: List[np.ndarray] = []
    if not results:
        return poses

    r = results[0]
    if r.keypoints is None:
        return poses

    # r.keypoints.xy shape: (num_people, num_kpts, 2)
    kp_xy = r.keypoints.xy.cpu().numpy()
    for person_kps in kp_xy:
        # person_kps -> (K, 2)
        poses.append(person_kps.astype(float))
    return poses


def run_yolo_pose(image_path: str,
                  conf: float = 0.25) -> Tuple[List[str], List[np.ndarray]]:
    """
    Backward-compatible helper your sorter expects.
    Returns (tags, keypoints_list).
      - tags: simple human-readable tag list (we use ["pose points"] if any pose found)
      - keypoints_list: list of (K,2) arrays
    """
    kps_list = detect_pose(image_path, conf=conf)
    tags = ["pose points"] if len(kps_list) else []
    return tags, kps_list


def draw_pose_on_image(image_or_path: Union[str, np.ndarray],
                       output_path: str | None = None,
                       conf: float = 0.25) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Draws detected keypoints on a copy of the image.
    Returns (image_bgr_with_points, keypoints_list).
    """
    img_bgr = _to_bgr(image_or_path).copy()
    kps_list = detect_pose(img_bgr, conf=conf)

    for kps in kps_list:
        for (x, y) in kps.astype(int):
            cv2.circle(img_bgr, (int(x), int(y)), 3, (0, 255, 0), -1)

    if output_path:
        cv2.imwrite(output_path, img_bgr)
    return img_bgr, kps_list
