# computer_vision/home_surveillance.py

import cv2
import time

class HomeSurveillance:
    def __init__(self, camera_index=0):
        # Initialize the camera
        self.camera_index = camera_index
        self.video_capture = cv2.VideoCapture(self.camera_index)
        self.prev_frame = None

    def detect_motion(self, frame):
        """Detect motion in the current frame compared to the previous frame."""
        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

        # If the previous frame is None, initialize it
        if self.prev_frame is None:
            self.prev_frame = gray_frame
            return False

        # Compute the absolute difference between the current frame and previous frame
        frame_delta = cv2.absdiff(self.prev_frame, gray_frame)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Dilate the thresholded image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours of the thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 500:  # Minimum area to consider for motion
                continue
            return True  # Motion detected

        self.prev_frame = gray_frame
        return False

    def start_surveillance(self):
        """Start the home surveillance system."""
        print("Starting home surveillance...")
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Error: Unable to capture video.")
                break

            motion_detected = self.detect_motion(frame)
            if motion_detected:
                cv2.putText(frame, "Motion Detected!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                print("Motion detected!")

            # Display the resulting frame
            cv2.imshow("Home Surveillance", frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture and close windows
        self.video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    surveillance_system = HomeSurveillance()
    surveillance_system.start_surveillance()

# computer_vision/home_surveillance.py

import cv2
from computer_vision.face_recognition import face_recognition as FaceRecognition
from computer_vision.object_detection import detect_objects

def monitor_stream(cam_index_or_url):
    cap = cv2.VideoCapture(cam_index_or_url)
    face_rec = FaceRecognition()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_faces = face_rec.detect_and_label_faces(frame)
        objects = detect_objects(frame)

        for name, (x, y, w, h) in detected_faces.items():
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        for obj in objects:
            cv2.rectangle(frame, obj["bbox"][:2], obj["bbox"][2:], (255, 255, 0), 2)
            cv2.putText(frame, obj["label"], obj["bbox"][:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        cv2.imshow("Jaicat Surveillance", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

