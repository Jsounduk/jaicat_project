# computer_vision/motorbike_model.py

import cv2
import numpy as np
import json
import os
import pytesseract

class MotorbikeModel:
    def __init__(self, yolo_weights: str, yolo_cfg: str, yolo_names: str, plate_cascade_path: str):
        try:
            self.net = cv2.dnn.readNet(yolo_weights, yolo_cfg)
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            with open(yolo_names, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
            self.plate_cascade = cv2.CascadeClassifier(plate_cascade_path)

            # Initialize local motorbike data storage
            self.local_motorbike_data = "computer_vision/local_motorbike_data.json"
            if not os.path.exists(self.local_motorbike_data):
                with open(self.local_motorbike_data, 'w') as file:
                    json.dump({}, file)

        except Exception as e:
            print(f"Error initializing motorbike model: {e}")

    def detect_motorbikes(self, frame: np.ndarray) -> list:
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids, confidences, boxes = [], [], []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5 and class_id == 3:  # Assuming motorbike is class ID 3 in COCO dataset
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        return [(boxes[i], confidences[i]) for i in indexes.flatten()]

    def detect_license_plate(self, frame: np.ndarray) -> str:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in plates:
            plate_img = frame[y:y + h, x:x + w]
            plate_text = pytesseract.image_to_string(plate_img, config='--psm 8')
            return plate_text.strip()
        return None

    def save_motorbike_detection(self, detection_data: dict):
        try:
            with open(self.local_motorbike_data, 'r') as file:
                data = json.load(file)
            data.append(detection_data)

            with open(self.local_motorbike_data, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving motorbike detection: {e}")

    def start_detection(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to capture video.")
                break

            motorbikes = self.detect_motorbikes(frame)
            for (box, confidence) in motorbikes:
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Motorbike: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Motorbike Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
