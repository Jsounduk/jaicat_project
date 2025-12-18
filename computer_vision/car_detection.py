import cv2
import torch

class CarDetection:
    CAR_CLASS_ID = 2

    def __init__(self, weights_path: str):
        try:
            self.model = torch.hub.load('WongKinYiu/yolov7', 'custom', weights_path, source='local')
        except Exception as e:
            print(f"Error loading model: {e}")

    def detect_cars(self, frame: cv2.Mat) -> list:
        """
        Detect cars in a given frame.

        Args:
            frame (cv2.Mat): Input frame.

        Returns:
            list: List of detected cars, each represented as a dictionary containing coordinates and confidence.
        """
        if frame is None:
            raise ValueError("Invalid input frame")

        results = self.model(frame)
        detections = results.xyxy[0]  # Get detections

        detected_cars = []
        for *xyxy, conf, cls in detections:
            if int(cls) == self.CAR_CLASS_ID:
                detected_cars.append({
                    'coordinates': [int(x) for x in xyxy],
                    'confidence': conf.item()
                })
        return detected_cars
