import os, csv
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CALENDAR_FILE = "data/calendar_data.csv"
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.service = None
        self.use_google = self._init_google()

        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(CALENDAR_FILE):
            with open(CALENDAR_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "DateTime"])

    def _init_google(self):
        try:
            creds = None
            if os.path.exists("config/token.json"):
                creds = Credentials.from_authorized_user_file("config/token.json", SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("config/credentials.json", SCOPES)
                    creds = flow.run_local_server(port=0)
                with open("config/token.json", "w") as token:
                    token.write(creds.to_json())
            self.service = build("calendar", "v3", credentials=creds)
            return True
        except Exception as e:
            print(f"[calendar] Google Calendar disabled: {e}")
            return False

    def add_event(self, title, dt_str):
        if self.use_google:
            dt = datetime.fromisoformat(dt_str)
            event = {
                'summary': title,
                'start': {'dateTime': dt.isoformat(), 'timeZone': 'Europe/London'},
                'end': {'dateTime': (dt.replace(minute=dt.minute+30)).isoformat(), 'timeZone': 'Europe/London'},
            }
            self.service.events().insert(calendarId='primary', body=event).execute()
            return f"[Google] Event '{title}' scheduled."

        # Fallback to CSV
        with open(CALENDAR_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([title, dt_str])
        return f"[Local] Event '{title}' scheduled."

    def get_events(self):
        if self.use_google:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                       maxResults=10, singleEvents=True,
                                                       orderBy='startTime').execute()
            return [{"Title": e['summary'], "DateTime": e['start']['dateTime']} for e in events_result.get('items', [])]

        with open(CALENDAR_FILE, "r") as f:
            return list(csv.DictReader(f))

    def delete_event(self, title):
        if self.use_google:
            # Not implemented yet — optional future
            return "[Google] Delete not supported yet."
        events = self.get_events()
        with open(CALENDAR_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "DateTime"])
            for e in events:
                if e["Title"].lower() != title.lower():
                    writer.writerow([e["Title"], e["DateTime"]])
        return f"[Local] Event '{title}' deleted."
