# services/swann_cctv.py

import requests
import json

class SwannCCTV:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def get_camera_status(self):
        """Get the status of all connected Swann cameras."""
        response = requests.get(f"{self.base_url}/cameras/status", headers={"Authorization": f"Bearer {self.api_key}"})
        if response.status_code == 200:
            return response.json()  # Returns JSON response with camera status
        else:
            return {"error": "Failed to retrieve camera status."}

    def capture_snapshot(self, camera_id):
        """Capture a snapshot from a specific camera."""
        response = requests.post(f"{self.base_url}/cameras/{camera_id}/snapshot", headers={"Authorization": f"Bearer {self.api_key}"})
        if response.status_code == 200:
            # Save snapshot if necessary
            return response.json()  # URL or path of the snapshot
        else:
            return {"error": "Failed to capture snapshot."}

    def start_recording(self, camera_id):
        """Start recording from a specific camera."""
        response = requests.post(f"{self.base_url}/cameras/{camera_id}/start-recording", headers={"Authorization": f"Bearer {self.api_key}"})
        return response.status_code == 200

    def stop_recording(self, camera_id):
        """Stop recording from a specific camera."""
        response = requests.post(f"{self.base_url}/cameras/{camera_id}/stop-recording", headers={"Authorization": f"Bearer {self.api_key}"})
        return response.status_code == 200
