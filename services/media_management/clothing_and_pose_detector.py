import cv2
from ultralytics import YOLO

POSE_MODEL_PATH = "services/media_management/yolov8n-pose.pt"
CLOTHING_MODEL_PATH = "services/media_management/yolov8n-deepfashion.pt"

POSE_CLASSES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee",
    "right_knee", "left_ankle", "right_ankle"
]
CLOTHING_CLASSES = [
    "short sleeve top", "long sleeve top", "short sleeve outwear", "long sleeve outwear",
    "vest", "sling", "shorts", "trousers", "skirt", "short sleeve dress", "long sleeve dress",
    "vest dress", "sling dress"
]

_pose_model = None
_clothing_model = None

def get_pose_model():
    global _pose_model
    if _pose_model is None:
        _pose_model = YOLO(POSE_MODEL_PATH)
    return _pose_model

def get_clothing_model():
    global _clothing_model
    if _clothing_model is None:
        _clothing_model = YOLO(CLOTHING_MODEL_PATH)
    return _clothing_model

def detect_pose(image_path, region=None):
    model = get_pose_model()
    img = cv2.imread(image_path)
    if region:
        x0, y0, x1, y1 = [int(v) for v in region]
        img = img[y0:y1, x0:x1]
    results = model(img)
    points = []
    for r in results:
        if hasattr(r, "keypoints") and r.keypoints is not None:
            for kpt in r.keypoints.xy[0]:
                points.append(tuple(kpt.tolist()))
    return points

def detect_clothing(image_path, region=None):
    model = get_clothing_model()
    img = cv2.imread(image_path)
    if region:
        x0, y0, x1, y1 = [int(v) for v in region]
        img = img[y0:y1, x0:x1]
    results = model(img)
    detected = []
    for r in results:
        for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
            label = CLOTHING_CLASSES[int(cls)]
            x0, y0, x1, y1 = map(int, box)
            detected.append({"label": label, "box": (x0, y0, x1, y1)})
    return detected
