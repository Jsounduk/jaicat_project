"""
ObjectDetection class detects objects in a given frame using YOLO.

Attributes:
    net (cv2.dnn_Net): The YOLO model.
    classes (list[str]): List of class names from the COCO dataset.

Methods:
    detect_objects(frame: np.ndarray) -> tuple[list[tuple[int, int, int, int]], list[float], list[int]]:
        Detect objects in a given frame.
        Args:
            frame (np.ndarray): Input frame.
        Returns:
            tuple[list[tuple[int, int, int, int]], list[float], list[int]]: Detected objects with bounding boxes, confidences, and class IDs.
"""
import cv2
import numpy as np
import os
import unittest

class ObjectDetection:
    """
    Initialize the YOLO model.

    Args:
        yolo_weights (str): Path to YOLO weights file (e.g., 'computer_vision/yolov7.weights').
        yolo_cfg (str): Path to YOLO configuration file (e.g., 'computer_vision/yolov7.cfg').
        coco_names (str): Path to COCO names file (e.g., 'computer_vision/coco.names').
    """

    def __init__(self, yolo_weights: str, yolo_cfg: str, coco_names: str) -> None:
        print(f"Loading YOLO model from {yolo_weights} and {yolo_cfg}...")
        self.net = cv2.dnn.readNetFromDarknet(os.path.abspath(yolo_cfg), os.path.abspath(yolo_weights))
        if self.net is None:
            raise ValueError(f"Failed to load YOLO model from {yolo_weights} and {yolo_cfg}")
        
        print(f"Loading COCO class names from {coco_names}...")
        self.classes: list[str] = []
        try:
            with open(coco_names, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
        except OSError as e:
            raise ValueError(f"Failed to load COCO class names from {coco_names}: {e}")
        
        print(f"Loaded {len(self.classes)} class names.")

    def detect_objects(self, frame: np.ndarray) -> tuple[list[tuple[int, int, int, int]], list[float], list[int]]:
        """
        Detect objects in a given frame.

        Args:
            frame (np.ndarray): Input frame.

        Returns:
            tuple[list[tuple[int, int, int, int]], list[float], list[int]]: Detected objects with bounding boxes, confidences, and class IDs.
        """
        print("Detecting objects...")
        if frame is None:
            raise ValueError("Input frame is null")
        
        height, width = frame.shape[:2]
        print(f"Frame size: {width}x{height}")
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        outs = self.net.forward(output_layers)

        boxes: list[tuple[int, int, int, int]] = []
        confidences: list[float] = []
        class_ids: list[int] = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype('int')
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append((x, y, w, h))
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        return boxes, confidences, class_ids

    def draw_detected_objects(self, frame: np.ndarray, boxes: list[tuple[int, int, int, int]], confidences: list[float], class_ids: list[int]):
        """
        Draw bounding boxes around detected objects.

        Args:
            frame (np.ndarray): Input frame.
            boxes (list): Detected bounding boxes.
            confidences (list): Confidence levels of detected objects.
            class_ids (list): Class IDs of detected objects.
        """
        for i in range(len(boxes)):
            x, y, w, h = boxes[i]
            label = f"{self.classes[class_ids[i]]}: {confidences[i]:.2f}"
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow('Object Detection', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



class TestObjectDetection(unittest.TestCase):
    def test_detect_objects(self):
        """
        Test object detection on a sample image.
        """
        # Load sample image
        frame = cv2.imread('samples/person.jpg')

        # Initialize object detection model
        od = ObjectDetection(yolo_weights='computer_vision/yolov7.weights',
                              yolo_cfg='computer_vision/yolov7.cfg',
                              coco_names='computer_vision/coco.names')

        # Detect objects
        boxes, confidences, class_ids = od.detect_objects(frame)

        # Assert at least one object is detected
        self.assertGreaterEqual(len(boxes), 1)

        # Assert the detected object is a person
        self.assertEqual(class_ids[0], 0)

        # Assert the confidence is high
        self.assertGreaterEqual(confidences[0], 0.8)

        # Assert the bounding box is within the frame
        x, y, w, h = boxes[0]
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertLessEqual(x + w, frame.shape[1])
        self.assertLessEqual(y + h, frame.shape[0])

# --- lightweight singleton + wrapper so other modules can `from ... import detect_objects` ---

# Default model files (adjust if you keep different ones)
_YOLO_WEIGHTS = os.path.abspath("computer_vision/yolov7.weights")
_YOLO_CFG     = os.path.abspath("computer_vision/yolov7.cfg")
_COCO_NAMES   = os.path.abspath("computer_vision/coco.names")

_DETECTOR_SINGLETON = None

def _get_detector():
    """
    Lazily construct a single ObjectDetection instance.
    Keeps startup fast and avoids repeated model loads.
    """
    global _DETECTOR_SINGLETON
    if _DETECTOR_SINGLETON is None:
        # You can switch to YOLOv11 later; this keeps current Darknet flow.
        _DETECTOR_SINGLETON = ObjectDetection(
            yolo_weights=_YOLO_WEIGHTS,
            yolo_cfg=_YOLO_CFG,
            coco_names=_COCO_NAMES,
        )
    return _DETECTOR_SINGLETON

def detect_objects(frame):
    """
    Module-level wrapper so callers can do:
      from computer_vision.object_detection import detect_objects
    """
    det = _get_detector()
    return det.detect_objects(frame)


