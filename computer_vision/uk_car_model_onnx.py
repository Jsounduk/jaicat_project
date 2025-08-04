
import cv2
import numpy as np
import onnxruntime as ort

class UKCarModel:
    def __init__(self, weights_path, names_path, plate_cascade_path, providers=['CPUExecutionProvider']):
        self.session = ort.InferenceSession(weights_path, providers=providers)
        self.plate_cascade = cv2.CascadeClassifier(plate_cascade_path)
        with open(names_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

    def preprocess(self, image, new_shape=(640, 640)):
        resized = cv2.resize(image, new_shape)
        img = resized.transpose((2, 0, 1))[None]
        return img.astype(np.float32) / 255.0

    def detect(self, image, conf_threshold=0.3):
        input_tensor = self.preprocess(image)
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_tensor})[0]

        detections = []
        for *box, cls_id, score in outputs:
            if score < conf_threshold:
                continue
            cls_id = int(cls_id)
            detections.append({
                "class_name": self.class_names[cls_id],
                "score": float(score),
                "box": [int(x) for x in box]
            })
        return detections

    def detect_plates(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray, 1.1, 4)
        return plates
