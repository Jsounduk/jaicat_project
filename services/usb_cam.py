# services/usb_cam.py

import cv2

class USBCam:
    def __init__(self):
        """Initialize the USB camera."""
        self.camera = None

    def start_camera(self):
        """Start the USB camera."""
        self.camera = cv2.VideoCapture(0)  # 0 is usually the default camera index

        if not self.camera.isOpened():
            raise Exception("Could not open the USB camera.")

    def capture_image(self, filename='captured_image.png'):
        """Capture an image from the camera and save it to a file."""
        if self.camera is None:
            raise Exception("Camera is not started. Call start_camera() first.")

        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture image.")

        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")

    def release_camera(self):
        """Release the camera resource."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("Camera released.")

# Example usage:
if __name__ == "__main__":
    usb_cam = USBCam()
    try:
        usb_cam.start_camera()
        usb_cam.capture_image("test_image.png")  # Change the filename as needed
    finally:
        usb_cam.release_camera()
