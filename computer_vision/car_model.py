import cv2
import numpy as np
import pytesseract
import os
import json
import onnxruntime as ort

class UKCarModel:
    def __init__(self, yolo_weights, yolo_cfg, yolo_names, plate_cascade_path, fallback_onnx=None):
        self.detections_save_path = "computer_vision/detections.json"
        self.local_data_path = "computer_vision/local_car_data.json"
        self.fallback_onnx = fallback_onnx

        for path, default in [
            (self.detections_save_path, []),
            (self.local_data_path, {})
        ]:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(default, f)

        try:
            self.net = cv2.dnn.readNet(yolo_weights, yolo_cfg)
            self.framework = "darknet"
            print("âœ… Darknet YOLO model loaded.")
        except Exception as e:
            print(f"âš ï¸ Darknet model failed: {e}")
            if fallback_onnx:
                self.session = ort.InferenceSession(fallback_onnx, providers=["CPUExecutionProvider"])
                self.framework = "onnx"
                print("âœ… Fallback ONNX model loaded.")
            else:
                raise RuntimeError("Both YOLO and fallback failed.")

        with open(yolo_names, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]



    def detect_cars(self, frame):
        return self._detect_darknet(frame) if self.framework == "darknet" else self._detect_onnx(frame)

    def _detect_darknet(self, frame):
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.net.getUnconnectedOutLayersNames())

        boxes, confidences = [], []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id == 2:
                    center_x, center_y = int(detection[0] * width), int(detection[1] * height)
                    w, h = int(detection[2] * width), int(detection[3] * height)
                    x, y = int(center_x - w / 2), int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        return [(boxes[i], confidences[i]) for i in indexes.flatten()]

    def _detect_onnx(self, frame):
        img = cv2.resize(frame, (640, 640))
        img_input = img.transpose((2, 0, 1))[np.newaxis].astype(np.float32) / 255.0
        outputs = self.session.run(None, {self.session.get_inputs()[0].name: img_input})[0]

        results = []
        for det in outputs:
            x0, y0, x1, y1, conf, cls_id = det[:6]
            if conf < 0.5:
                continue
            box = [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]
            results.append((box, float(conf)))
        return results

    def detect_license_plate(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray, 1.1, 5)
        for (x, y, w, h) in plates:
            roi = frame[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, config='--psm 8')
            return text.strip()
        return None

    def save_detection(self, detection_data):
        try:
            with open(self.detections_save_path, 'r') as f:
                data = json.load(f)
            data.append(detection_data)
            with open(self.detections_save_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving detection: {e}")

    def get_vehicle_data(self, plate_number):
        try:
            with open(self.local_data_path, 'r') as f:
                return json.load(f).get(plate_number, {"model": "Unknown", "manufacturer": "Unknown"})
        except:
            return {}

    def save_to_local_data(self, plate_number, vehicle_data):
        try:
            with open(self.local_data_path, 'r') as f:
                data = json.load(f)
            data[plate_number] = vehicle_data
            with open(self.local_data_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving vehicle data: {e}")

    def start_detection(self, cam_index=0):
        cap = cv2.VideoCapture(cam_index)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ðŸš« Failed to grab frame.")
                break

            cars = self.detect_cars(frame)
            plate = self.detect_license_plate(frame)

            if plate:
                data = {
                    "license_plate": plate,
                    "vehicle_data": self.get_vehicle_data(plate),
                    "detections": [{"box": box, "confidence": conf} for box, conf in cars]
                }
                self.save_detection(data)

            for box, conf in cars:
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Car {conf:.2f}", (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cv2.imshow("Jaicat Car Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def start_detection_onnx(self, cam_index=0):
        cap = cv2.VideoCapture(cam_index)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ðŸš« Failed to grab frame.")
                break

            cars = self._detect_onnx(frame)

            for box, conf in cars:
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Car {conf:.2f}", (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cv2.imshow("Jaicat Car Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
