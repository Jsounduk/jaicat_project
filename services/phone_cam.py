# services/phone_cam.py
import cv2

class PhoneCamera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)  # Initialize the camera

    def capture_image(self):
        """Capture an image from the phone camera."""
        ret, frame = self.camera.read()
        if ret:
            image_path = "captured_image.png"  # Save the captured image
            cv2.imwrite(image_path, frame)
            return f"Image captured and saved as {image_path}."
        else:
            return "Failed to capture image."

    def release_camera(self):
        """Release the camera resource."""
        self.camera.release()
        cv2.destroyAllWindows()
