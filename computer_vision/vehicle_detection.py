import cv2
import numpy as np

class VehicleDetection:
    def __init__(self, computer_vision/yolov7.weights.pt, computer_vision/yolov7.cfg, computer_vision/coco.names.txt):
        # Load YOLO model
        self.net = cv2.dnn.readNet(computer_vision/yolov7.weights.pt, computer_vision/yolov7.cfg)
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        self.classes = []
        with open(computer_vision/coco.names.txt, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

    def detect_vehicles(self, frame):
        height, width, _ = frame.shape

        # Prepare the frame for detection
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)

        class_ids, confidences, boxes = [], [], []

        # Loop through detections
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                # Filter car (class_id == 2) and motorbike (class_id == 3)
                if confidence > 0.5 and class_id in [2, 3]:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Non-Maximum Suppression to remove overlapping boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        return [(boxes[i], confidences[i], self.classes[class_ids[i]]) for i in indexes.flatten()]

    def start_detection(self):
        cap = cv2.VideoCapture(0)  # Open the webcam
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to capture video.")
                break

            detections = self.detect_vehicles(frame)
            for (box, confidence, label) in detections:
                x, y, w, h = box
                label = f"{label} - {confidence:.2f}"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Vehicle Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

