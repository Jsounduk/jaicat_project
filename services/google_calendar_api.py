def get_events(calendar_id, start_date, end_date):
    api_key = "YOUR_GOOGLE_CALENDAR_API_KEY"
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?start={start_date}&end={end_date}&key={api_key}"
    response = requests.get(url)
    events_data = json.loads(response.text)
    return events_data["items"]