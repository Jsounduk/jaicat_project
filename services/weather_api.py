def get_weather(city):
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    weather_data = json.loads(response.text)
    return weather_data["weather"][0]["description"]