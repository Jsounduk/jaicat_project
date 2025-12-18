import mediapipe as mp
import cv2
import numpy as np

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

def detect_body_part(image_path, box):
    # box: (x1, y1, x2, y2) in pixel coords
    mp_pose = mp.solutions.pose
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)
        if not results.pose_landmarks:
            return "No body detected"

        h, w, _ = image.shape
        # Find all landmarks inside the box
        landmarks = []
        for idx, lm in enumerate(results.pose_landmarks.landmark):
            x, y = int(lm.x * w), int(lm.y * h)
            if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                landmarks.append((idx, BODY_PARTS.get(idx, f"unknown_{idx}")))
        if not landmarks:
            # If none inside, find the closest keypoint to box center
            cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
            dists = []
            for idx, lm in enumerate(results.pose_landmarks.landmark):
                x, y = int(lm.x * w), int(lm.y * h)
                d = np.hypot(cx - x, cy - y)
                dists.append((d, idx))
            dists.sort()
            idx = dists[0][1]
            return BODY_PARTS.get(idx, f"unknown_{idx}")
        return ", ".join(part for _, part in landmarks)
