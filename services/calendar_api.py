import datetime
import os
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from outlook import Outlook

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path/to/service_account_key.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, SCOPES)

calendar_service = build('calendar', 'v3', credentials=credentials)

# Outlook API setup
outlook_client_id = 'your_outlook_client_id'
outlook_client_secret = 'your_outlook_client_secret'
outlook_username = 'your_outlook_username'
outlook_password = 'your_outlook_password'

outlook = Outlook(outlook_client_id, outlook_client_secret, outlook_username, outlook_password)

# Integrate Google Calendar and Outlook APIs
def sync_calendars():
    # Get events from Google Calendar
    events_result = calendar_service.events().list(calendarId='primary').execute()
    events = events_result.get('items', [])

    # Get events from Outlook
    outlook_events = outlook.get_events()

    # Sync events between Google Calendar and Outlook
    for event in events:
        outlook_event = outlook.create_event(event['summary'], event['location'], event['start']['dateTime'], event['end']['dateTime'])
        print(f"Created event in Outlook: {outlook_event['subject']}")

    for outlook_event in outlook_events:
        google_event = {
            'summary': outlook_event['subject'],
            'location': outlook_event['location'],
            'start': {'dateTime': outlook_event['start']},
            'end': {'dateTime': outlook_event['end']}
        }
        calendar_service.events().insert(calendarId='primary', body=google_event).execute()
        print(f"Created event in Google Calendar: {google_event['summary']}")

# Run the sync function periodically
while True:
    sync_calendars()
    datetime.time.sleep(60)  # Run every 1 minute




import google.auth
from googleapiclient.discovery import build
import datetime
import msal

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
if creds is None or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        creds = Credentials.from_service_account_file(
            'path/to/service_account_key.json', scopes=SCOPES)

service = build('calendar', 'v3', credentials=creds)

def create_google_calendar_event(summary, location, description, start_time, end_time):
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def update_google_calendar_event(event_id, summary, location, description, start_time, end_time):
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['summary'] = summary
    event['location'] = location
    event['description'] = description
    event['start'] = {'dateTime': start_time, 'timeZone': 'America/New_York'}
    event['end'] = {'dateTime': end_time, 'timeZone': 'America/New_York'}
    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print('Event updated: %s' % (updated_event.get('htmlLink')))

def delete_google_calendar_event(event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    print('Event deleted: %s' % (event_id))

# Outlook API setup
app = msal.ConfidentialClientApplication(
    client_id='your_client_id',
    client_credential='your_client_secret',
    authority='https://login.microsoftonline.com/your_tenant_id'
)

def create_outlook_calendar_event(summary, location, description, start_time, end_time):
    event = {
        'subject': summary,
        'body': {
            'contentType': 'HTML',
            'content': description
        },
        'start': {
            'dateTime': start_time,
            'timeZone': 'Eastern Standard Time'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Eastern Standard Time'
        },
        'location': {
            'displayName': location
        }
    }
    result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
    token = result.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('https://graph.microsoft.com/v1.0/me/events', headers=headers, json=event)
    print('Event created: %s' % (response.json()['id']))

def update_outlook_calendar_event(event_id, summary, location, description, start_time, end_time):
    event = {
        'subject': summary,
        'body': {
            'contentType': 'HTML',
            'content': description
        },
        'start': {
            'dateTime': start_time,
            'timeZone': 'Eastern Standard Time'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Eastern Standard Time'
        },
        'location': {
            'displayName': location
        }
    }
    result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
    token = result.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.patch(f'https://graph.microsoft.com/v1.0/me/events/{event_id}', headers=headers, json=event)
    print('Event updated: %s' % (response.json()['id']))

def delete_outlook_calendar_event(event_id):
    result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
    token = result.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(f'https://graph.microsoft.com/v1.0/me/events/{event_id}', headers=headers)
    print('Event deleted: %s' % (event_id))
# Note that you'll need to replace the placeholders (your_client_id, your_client_secret, your_tenant_id) with your actual Outlook API credentials. Additionally, you'll need to install the msal and requests libraries using pip.
