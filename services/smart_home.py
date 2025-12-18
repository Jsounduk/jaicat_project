import requests

# services/smart_home.py

def toggle_lights(room: str, state: str):
    # Placeholder for real control (like Home Assistant, MQTT, etc.)
    print(f"[smart_home] Turning {state} the lights in {room}")
    return f"The lights in {room} are now {state}."

def adjust_thermostat(temp: int):
    print(f"[smart_home] Setting temperature to {temp}°C")
    return f"Thermostat set to {temp} degrees."


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
        


