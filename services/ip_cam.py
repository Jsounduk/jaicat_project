# services/ip_cam.py

import cv2
import requests

class IPCamera:
    def __init__(self, camera_url):
        self.camera_url = camera_url

    def get_stream(self):
        """Start streaming from the IP camera."""
        cap = cv2.VideoCapture(self.camera_url)
        if not cap.isOpened():
            return {"error": "Could not open video stream."}
        return cap

    def capture_snapshot(self):
        """Capture a snapshot from the IP camera."""
        cap = self.get_stream()
        if isinstance(cap, dict):  # If there's an error
            return cap
        
        ret, frame = cap.read()
        cap.release()
        if ret:
            snapshot_path = 'snapshot.jpg'
            cv2.imwrite(snapshot_path, frame)  # Save the snapshot
            return {"success": True, "snapshot_path": snapshot_path}
        else:
            return {"error": "Failed to capture snapshot."}

    def start_recording(self):
        """Start recording video from the IP camera."""
        cap = self.get_stream()
        if isinstance(cap, dict):  # If there's an error
            return cap
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)  # Write frame to the video file

        cap.release()
        out.release()
        return {"success": True, "message": "Recording stopped."}

    def stop_recording(self):
        """Stop recording video from the IP camera."""
        # In a real-world application, you'd likely manage the recording state with a flag
        # Here we'll just simulate stopping the recording.
        return {"success": True, "message": "Recording stopped."}
    

import cv2

def get_video_stream(url_or_index):
    cap = cv2.VideoCapture(url_or_index)
    if not cap.isOpened():
        raise RuntimeError("Failed to open video stream.")
    return cap
