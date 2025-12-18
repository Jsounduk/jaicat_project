import os, json, random, shutil
from pathlib import Path
from PIL import Image

ROOT = Path("services/media_management")
ANN = ROOT/"region_annotations.json"       # your box tags
DET_LOG = ROOT/"datasets/logs/detections.jsonl"
POSE_LOG = ROOT/"datasets/logs/poses.jsonl"

DETECT_DIR = ROOT/"datasets/jaicat_vision/detect"
POSE_DIR   = ROOT/"datasets/jaicat_vision/pose"

IMAGE_EXTS = {".jpg",".jpeg",".png",".webp",".bmp",".tiff"}

def ensure_dirs(base):
    for split in ["train","val"]:
        (base/"images"/split).mkdir(parents=True, exist_ok=True)
        (base/"labels"/split).mkdir(parents=True, exist_ok=True)

def yolo_norm(b, w, h):
    x1,y1,x2,y2 = b
    cx = (x1+x2)/2.0 / w
    cy = (y1+y2)/2.0 / h
    ww = (x2-x1)/float(w)
    hh = (y2-y1)/float(h)
    return cx, cy, ww, hh

# Map your tag strings to stable class ids:
CLASS_MAP = {
    "person": 0, "face": 1, "dress": 2, "top": 3, "jeans": 4, "shoes": 5, "handbag": 6, "phone": 7
}

def collect_images():
    imgs = set()
    if ANN.exists():
        with open(ANN, "r", encoding="utf-8") as f:
            for r in json.load(f):
                if "image_path" in r: imgs.add(r["image_path"])
    if DET_LOG.exists():
        for line in open(DET_LOG, "r", encoding="utf-8"):
            try:
                row = json.loads(line)
                imgs.add(row["image"])
            except: pass
    return sorted(imgs)

def split_items(items, val_ratio=0.1):
    random.shuffle(items)
    n = max(1, int(len(items)*val_ratio))
    return items[n:], items[:n]

def export_detect():
    ensure_dirs(DETECT_DIR)
    items = collect_images()
    train, val = split_items(items)

    # index detections by image
    det_index = {}
    if DET_LOG.exists():
        for line in open(DET_LOG, "r", encoding="utf-8"):
            row = json.loads(line)
            if row.get("task")=="detect":
                det_index.setdefault(row["image"], []).append(row)

    # index your manual regions by image
    ann_index = {}
    if ANN.exists():
        for r in json.load(open(ANN, "r", encoding="utf-8")):
            img = r.get("image_path")
            if not img: continue
            ann_index.setdefault(img, []).append(r)

    def handle_one(img_path, split_dir):
        try:
            im = Image.open(img_path)
            w,h = im.size
        except:
            return
        img_dst = DETECT_DIR/"images"/split_dir/Path(img_path).name
        lbl_dst = DETECT_DIR/"labels"/split_dir/(Path(img_path).stem + ".txt")
        shutil.copy2(img_path, img_dst)

        rows = []
        # 1) from detections log
        for row in det_index.get(img_path, []):
            boxes = row["boxes_xyxy"]; clss = row["classes"]
            for b,c in zip(boxes, clss):
                # If class id from COCO doesn't match your map, map generically to 'person' for now
                cls_id = CLASS_MAP.get("person", 0) if int(c)==0 else CLASS_MAP.get("face",1)
                cx, cy, ww, hh = yolo_norm(b, w, h)
                rows.append(f"{cls_id} {cx:.6f} {cy:.6f} {ww:.6f} {hh:.6f}")

        # 2) from your manual regions
        for r in ann_index.get(img_path, []):
            tag = (r.get("tag") or r.get("label") or "").lower()
            cls_id = CLASS_MAP.get(tag, CLASS_MAP.get("person",0))
            x1,y1,x2,y2 = r["coords"]
            cx, cy, ww, hh = yolo_norm((x1,y1,x2,y2), w, h)
            rows.append(f"{cls_id} {cx:.6f} {cy:.6f} {ww:.6f} {hh:.6f}")

        with open(lbl_dst, "w", encoding="utf-8") as f:
            f.write("\n".join(rows))

    for img in train: handle_one(img, "train")
    for img in val:   handle_one(img, "val")
    print("✅ Detect dataset exported to", DETECT_DIR)

def export_pose():
    ensure_dirs(POSE_DIR)
    items = collect_images()
    train, val = split_items(items)

    # index pose by image
    pose_index = {}
    if POSE_LOG.exists():
        for line in open(POSE_LOG, "r", encoding="utf-8"):
            row = json.loads(line)
            if row.get("task")=="pose":
                pose_index.setdefault(row["image"], []).append(row)

    def kp_norm(kps, w, h):
        # expects list of [ [x,y], [x,y], ... ]  length 17
        out=[]
        for (x,y) in kps:
            out.extend([x/float(w), y/float(h), 2])  # visible=2
        return out

    def handle_one(img_path, split_dir):
        try:
            im = Image.open(img_path); w,h = im.size
        except:
            return
        img_dst = POSE_DIR/"images"/split_dir/Path(img_path).name
        lbl_dst = POSE_DIR/"labels"/split_dir/(Path(img_path).stem + ".txt")
        shutil.copy2(img_path, img_dst)

        rows=[]
        # YOLO pose row: <cls> <cx> <cy> <w> <h> <kpt1x> <kpt1y> <vis> ... <kpt17x> <kpt17y> <vis>
        # For simplicity, derive bbox from min/max of keypoints
        for row in pose_index.get(img_path, []):
            for seq in row.get("keypoints_xy", []):
                if not seq: continue
                xs=[p[0] for p in seq]; ys=[p[1] for p in seq]
                x1,x2 = max(0,min(xs)), min(w,max(xs))
                y1,y2 = max(0,min(ys)), min(h,max(ys))
                cx, cy, ww, hh = ((x1+x2)/2)/w, ((y1+y2)/2)/h, (x2-x1)/w, (y2-y1)/h
                kps = kp_norm(seq, w, h)
                rows.append(" ".join([str(0), f"{cx:.6f}", f"{cy:.6f}", f"{ww:.6f}", f"{hh:.6f}"] +
                                     [f"{v:.6f}" if isinstance(v,float) else str(v) for v in kps]))

        with open(lbl_dst, "w", encoding="utf-8") as f:
            f.write("\n".join(rows))

    for img in train: handle_one(img, "train")
    for img in val:   handle_one(img, "val")
    print("✅ Pose dataset exported to", POSE_DIR)

if __name__ == "__main__":
    export_detect()
    export_pose()
