import os, json, time
from pathlib import Path
from ultralytics import YOLO

SOURCE = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\SORT"
OUT_DIR = Path("services/media_management/datasets/logs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
det_log = (OUT_DIR/"detections.jsonl").open("a", encoding="utf-8")
pose_log = (OUT_DIR/"poses.jsonl").open("a", encoding="utf-8")

det_model = YOLO("yolo11s.pt")        # detect
pose_model = YOLO("yolo11s-pose.pt")  # pose (optional)

IMAGE_EXTS = {".jpg",".jpeg",".png",".webp",".bmp",".tiff"}

def to_rel(p): return str(Path(p).as_posix())

for root, _, files in os.walk(SOURCE):
    for f in files:
        if Path(f).suffix.lower() in IMAGE_EXTS:
            img = os.path.join(root, f)
            ts = int(time.time())

            # DETECTION
            det_res = det_model.predict(img, verbose=False)
            for r in det_res:
                boxes = r.boxes.xyxy.cpu().numpy().tolist()
                cls   = r.boxes.cls.cpu().numpy().tolist()
                conf  = r.boxes.conf.cpu().numpy().tolist()
                row = {
                    "timestamp": ts,
                    "image": to_rel(img),
                    "model": "yolo11s",
                    "task": "detect",
                    "boxes_xyxy": boxes,
                    "classes": cls,
                    "confs": conf
                }
                det_log.write(json.dumps(row)+"\n")

            # POSE (optional)
            pose_res = pose_model.predict(img, verbose=False)
            for r in pose_res:
                kpts = r.keypoints.xy.cpu().numpy().tolist() if r.keypoints is not None else []
                row = {
                    "timestamp": ts,
                    "image": to_rel(img),
                    "model": "yolo11s-pose",
                    "task": "pose",
                    "keypoints_xy": kpts
                }
                pose_log.write(json.dumps(row)+"\n")

det_log.close(); pose_log.close()
print("✅ Wrote logs to", OUT_DIR)
