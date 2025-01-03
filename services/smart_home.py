import requests

class SmartHomeService:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def control_device(self, device_id, action):
        url = f"{self.base_url}/devices/{device_id}/{action}?api_key={self.api_key}"
        response = requests.post(url)
        if response.status_code == 200:
            return f"{action.capitalize()} command sent to device {device_id}."
        else:
            return "Failed to control the device."
