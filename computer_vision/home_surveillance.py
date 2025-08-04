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
