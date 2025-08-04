import requests
import os
import geocoder
import json

class WeatherService:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.api_key = self.load_api_key_from_json()
        self.base_url = "https://api.tomorrow.io/v4/weather/forecast"

    def load_api_key_from_json(self):
        try:
            if self.user_id:
                filepath = f"jaicat_project/enrollment_json/{self.user_id}.json"
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data.get("api_key") or os.getenv("TOMORROW_API_KEY")
            return os.getenv("TOMORROW_API_KEY")
        except Exception as e:
            print(f"Error loading API key: {e}")
            return os.getenv("TOMORROW_API_KEY")

    def get_google_location(self):
        # Placeholder – this will use Google OAuth/location API once integrated
        print("[TODO] Fetching location from Google Account...")
        return None, None

    def get_manual_location_from_json(self):
        try:
            filepath = f"jaicat_project/enrollment_json/{self.user_id}.json"
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get("lat"), data.get("lon")
        except Exception as e:
            print(f"Error loading manual location: {e}")
            return None, None

    def get_weather(self, lat=None, lon=None, use_google=False):
        if use_google:
            lat, lon = self.get_google_location()
        if not lat or not lon:
            lat, lon = self.get_manual_location_from_json()
        if not lat or not lon:
            g = geocoder.ip('me')
            latlng = g.latlng if g.latlng else (None, None)
            lat, lon = latlng
        if not lat or not lon:
            return "Location unknown. Please enter it manually."

        params = {
            "location": f"{lat},{lon}",
            "apikey": self.api_key,
            "timesteps": "1d",
            "fields": "temperatureMax,weatherCodeMax",
            "units": "metric"
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            daily_data = data.get("timelines", {}).get("daily", [])
            if daily_data:
                today = daily_data[0]
                weather_code = today["values"].get("weatherCodeMax", "Unknown")
                temp = today["values"].get("temperatureMax", "Unknown")
                return f"{weather_code} – {temp}°C"
            else:
                return "No weather data found 🫤"
        else:
            return f"Weather fetch failed [{response.status_code}] 😢"
