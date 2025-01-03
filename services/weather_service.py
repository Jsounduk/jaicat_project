import requests
import os

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("VXy1cHjASsehJvfOVB5mf38pthgg71ix")  # Ensure your API key is loaded from the environment
        self.base_url = "https://api.tomorrow.io/v4/weather/forecast"  # Update to forecast endpoint


    def get_weather(self, lat, lon):
        """Fetch weather data for given latitude and longitude."""
        params = {
            'location': f"{lat},{lon}",
            'apikey': self.api_key,
            'units': 'imperial',  # or 'metric'
            'timesteps': '1d'
        }
        
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            # Extract necessary values
            daily_data = data.get("timelines", {}).get("daily", [])
            if daily_data:
                # You can modify this part to handle multiple days of data as needed
                latest_day = daily_data[0]  # Get the most recent day
                description = latest_day["values"].get("weatherCodeMax", "Unknown Weather Code")
                temperature = latest_day["values"].get("temperatureMax", "Unknown Temperature")
                return {
                    "description": description,
                    "temperature": f"{temperature}°F"  # or °C based on your preference
                }
            else:
                return {"error": "No daily data found."}
        else:
            return {"error": f"Error fetching weather data: {response.status_code}"}
