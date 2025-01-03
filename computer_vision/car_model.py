import cv2
import numpy as np
import pytesseract
import os
import json

class UKCarModel:
    def __init__(self, yolo_weights: str, yolo_cfg: str, yolo_names: str, plate_cascade_path: str):
        self.detections_save_path = "computer_vision/detections.json"
        self.local_data_path = "computer_vision/local_car_data.json"

        if not os.path.exists(self.detections_save_path):
            with open(self.detections_save_path, 'w') as file:
                json.dump([], file)

        if not os.path.exists(self.local_data_path):
            with open(self.local_data_path, 'w') as file:
                json.dump({}, file)

        try:
            self.net = cv2.dnn.readNet(yolo_weights, yolo_cfg)
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            
            with open(yolo_names, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]

            self.plate_cascade = cv2.CascadeClassifier(plate_cascade_path)

        except Exception as e:
            print(f"Error initializing model: {e}")

    def detect_cars(self, frame: np.ndarray) -> list:
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

                if confidence > 0.5 and class_id == 2:
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

    def save_detection(self, detection_data: dict) -> None:
        try:
            with open(self.detections_save_path, 'r') as file:
                data = json.load(file)
            data.append(detection_data)

            with open(self.detections_save_path, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Detection saved: {detection_data}")
        except Exception as e:
            print(f"Error saving detection: {e}")

    def export_detections(self, export_path: str) -> None:
        try:
            with open(self.detections_save_path, 'r') as file:
                data = json.load(file)

            with open(export_path, 'w') as export_file:
                json.dump(data, export_file, indent=4)
            print(f"Detections exported to: {export_path}")
        except Exception as e:
            print(f"Error exporting detections: {e}")

    def start_detection(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to capture video.")
                break

            detected_cars = self.detect_cars(frame)
            license_plate = self.detect_license_plate(frame)

            if license_plate:
                print(f"Detected License Plate: {license_plate}")
                vehicle_data = self.get_vehicle_data(license_plate)
                detection_data = {
                    "license_plate": license_plate,
                    "vehicle_data": vehicle_data,
                    "detected_cars": [{"box": box, "confidence": conf} for box, conf in detected_cars],
                }
                self.save_detection(detection_data)

            for (box, confidence) in detected_cars:
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Car: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Car and License Plate Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def get_vehicle_data(self, plate_number: str) -> dict:
        try:
            with open(self.local_data_path, 'r') as file:
                data = json.load(file)
            return data.get(plate_number, {"model": "Unknown", "manufacturer": "Unknown"})
        except Exception as e:
            print(f"Error retrieving vehicle data: {e}")
            return {}

    def save_to_local_data(self, plate_number: str, vehicle_data: dict) -> None:
        try:
            with open(self.local_data_path, 'r') as file:
                data = json.load(file)
            data[plate_number] = vehicle_data

            with open(self.local_data_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving vehicle data: {e}")
