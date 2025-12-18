# services/media_management/yolo11_adapter.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
from ultralytics import YOLO

from log_utils import ensure_log_dir, jsonl_append

Detection = Dict[str, Any]   # {"box":[x1,y1,x2,y2], "conf":float, "cls":int, "label":str}
Keypoint  = Dict[str, Any]   # {"xy":[(x,y),...], "conf":[float,...]}

class YOLO11Adapter:
    """
    Thin wrapper around Ultralytics YOLO11 for:
      - detect()  : generic object/person boxes
      - pose()    : keypoints for body-part suggestions
      - segment() : clothing/person masks (seg models)
      - track()   : video/webcam tracking (optional)
      - benchmark(): optional perf probe

    If log_dir is provided, calls will log to JSONL:
      detections.jsonl / poses.jsonl / segments.jsonl
    """
    def __init__(
        self,
        detect_weights: str = "yolo11n.pt",
        pose_weights: Optional[str] = "yolo11n-pose.pt",
        seg_weights: Optional[str] = "yolo11n-seg.pt",
        device: Optional[str] = None,
        imgsz: int = 640,
        log_dir: Optional[str] = "services/media_management/datasets/logs"
    ):
        self.device = device
        self.imgsz = imgsz
        self._detect_model = YOLO(detect_weights) if detect_weights else None
        self._pose_model   = YOLO(pose_weights)   if pose_weights   else None
        self._seg_model    = YOLO(seg_weights)    if seg_weights    else None

        self._detect_name = Path(detect_weights).name if detect_weights else None
        self._pose_name   = Path(pose_weights).name   if pose_weights   else None
        self._seg_name    = Path(seg_weights).name    if seg_weights    else None

        self.log_dir = ensure_log_dir(log_dir) if log_dir else None
        if self.log_dir:
            self._det_path = self.log_dir / "detections.jsonl"
            self._pose_path = self.log_dir / "poses.jsonl"
            self._seg_path = self.log_dir / "segments.jsonl"

    # ---------- DETECT ----------
    def detect(self, image_bgr: np.ndarray, conf: float = 0.25) -> List[Detection]:
        if not self._detect_model:
            return []
        results = self._detect_model.predict(
            source=image_bgr, conf=conf, verbose=False, device=self.device, imgsz=self.imgsz
        )
        if not results:
            return []
        r = results[0]
        names = r.names or {}

        dets: List[Detection] = []
        if r.boxes is None:
            return dets

        boxes = []
        clss  = []
        confs = []
        for b in r.boxes:
            xyxy = b.xyxy[0].tolist()
            confv = float(b.conf[0].item()) if getattr(b, "conf", None) is not None else 0.0
            clsid = int(b.cls[0].item()) if getattr(b, "cls", None) is not None else -1
            dets.append({
                "box": [int(x) for x in xyxy],
                "conf": confv,
                "cls": clsid,
                "label": names.get(clsid, str(clsid))
            })
            boxes.append(xyxy); clss.append(clsid); confs.append(confv)

        # log
        if self.log_dir is not None:
            row = {
                "task": "detect",
                "source": "model",
                "model": self._detect_name,
                "imgsz": self.imgsz,
                "conf": conf,
                "boxes_xyxy": boxes,
                "classes": clss,
                "confs": confs,
                "labels": [names.get(int(c), str(c)) for c in clss],
            }
            jsonl_append(self._det_path, row)

        return dets

    # ---------- POSE ----------
    def pose(self, image_bgr: np.ndarray, conf: float = 0.25) -> List[Keypoint]:
        if not self._pose_model:
            return []
        results = self._pose_model.predict(
            source=image_bgr, conf=conf, verbose=False, device=self.device, imgsz=self.imgsz
        )
        if not results:
            return []
        r = results[0]
        if r.keypoints is None:
            # still log an empty entry for completeness
            if self.log_dir is not None:
                jsonl_append(self._pose_path, {
                    "task": "pose",
                    "source": "model",
                    "model": self._pose_name,
                    "imgsz": self.imgsz,
                    "conf": conf,
                    "keypoints_xy": []
                })
            return []

        kps: List[Keypoint] = []
        keypoints_xy = []
        for kp in r.keypoints:
            xy = kp.xy[0].tolist() if hasattr(kp, "xy") else []
            confs = kp.conf[0].tolist() if hasattr(kp, "conf") and kp.conf is not None else None
            kps.append({"xy": [(float(x), float(y)) for x, y in xy], "conf": confs})
            keypoints_xy.append(xy)

        if self.log_dir is not None:
            jsonl_append(self._pose_path, {
                "task": "pose",
                "source": "model",
                "model": self._pose_name,
                "imgsz": self.imgsz,
                "conf": conf,
                "keypoints_xy": keypoints_xy
            })

        return kps

    # ---------- SEGMENT ----------
    def segment(self, image_bgr: np.ndarray, conf: float = 0.25):
        if not self._seg_model:
            return []
        results = self._seg_model.predict(
            source=image_bgr, conf=conf, verbose=False, device=self.device, imgsz=self.imgsz
        )
        if not results:
            return []
        r = results[0]
        names = r.names or {}
        segs = []
        boxes_out, clss_out, confs_out, labels_out, masks_out = [], [], [], [], []

        if r.masks is None or r.boxes is None:
            # log empty entry if needed
            if self.log_dir is not None:
                jsonl_append(self._seg_path, {
                    "task": "segment",
                    "source": "model",
                    "model": self._seg_name,
                    "imgsz": self.imgsz,
                    "conf": conf,
                    "boxes_xyxy": [],
                    "classes": [],
                    "confs": [],
                    "labels": [],
                    "masks": []
                })
            return segs

        for b, mask in zip(r.boxes, r.masks):
            xyxy = b.xyxy[0].tolist()
            clsid = int(b.cls[0].item()) if getattr(b, "cls", None) is not None else -1
            lbl = names.get(clsid, str(clsid))
            m = mask.xy[0].tolist() if hasattr(mask, "xy") else None

            segs.append({
                "box": [int(x) for x in xyxy],
                "cls": clsid,
                "label": lbl,
                "mask_poly": m
            })
            boxes_out.append(xyxy); clss_out.append(clsid)
            confs_out.append(float(b.conf[0].item()) if getattr(b, "conf", None) is not None else 0.0)
            labels_out.append(lbl)
            masks_out.append(m)

        if self.log_dir is not None:
            jsonl_append(self._seg_path, {
                "task": "segment",
                "source": "model",
                "model": self._seg_name,
                "imgsz": self.imgsz,
                "conf": conf,
                "boxes_xyxy": boxes_out,
                "classes": clss_out,
                "confs": confs_out,
                "labels": labels_out,
                "masks": masks_out
            })

        return segs

    # ---------- TRACK ----------
    def track(self, source: str | int, conf: float = 0.25, persist: bool = True, show: bool = False):
        if not self._detect_model:
            return None
        return self._detect_model.track(
            source=source, conf=conf, verbose=False, device=self.device, persist=persist, show=show, imgsz=self.imgsz
        )

    # ---------- BENCHMARK ----------
    def benchmark(self, imgsz: Optional[int] = None):
        if not self._detect_model:
            return None
        return self._detect_model.benchmark(verbose=False, imgsz=imgsz or self.imgsz)
# ---------- END YOLO11Adapter ----------