import unittest
import cv2
from computer_vision.object_detection import ObjectDetection

class TestObjectDetection(unittest.TestCase):
    def test_detect_objects(self):
        """
        Test object detection on a sample image.
        """
        # Load sample image
        frame = cv2.imread('samples/person.jpg')

        # Initialize object detection model
        od = ObjectDetection(
            yolo_weights='computer_vision/yolov7.weights',
            yolo_cfg='computer_vision/yolov7.cfg',
            coco_names='computer_vision/coco.names'
        )

        # Detect objects
        boxes, confidences, class_ids = od.detect_objects(frame)

        # Assert at least one object is detected
        self.assertGreaterEqual(len(boxes), 1)

        # Assert the detected object is a person (COCO class ID for 'person' is 0)
        self.assertEqual(class_ids[0], 0)

        # Assert the confidence is high
        self.assertGreaterEqual(confidences[0], 0.8)

        # Assert the bounding box is within the frame
        x, y, w, h = boxes[0]
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertLessEqual(x + w, frame.shape[1])
        self.assertLessEqual(y + h, frame.shape[0])

if __name__ == '__main__':
    unittest.main()
