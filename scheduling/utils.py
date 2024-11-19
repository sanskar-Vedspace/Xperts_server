from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

def create_google_meet_event(mentor_credentials, mentee_email, start_time, end_time):
    try:
        service = build('calendar', 'v3', credentials=mentor_credentials)
        
        event = {
            'summary': 'Mentorship Session',
            'description': 'Google Meet session between mentor and mentee.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata',  # Set your time zone here
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [
                {'email': mentee_email},  # Mentee's email
            ],
            'conferenceData': {
                'createRequest': {
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet',
                    },
                    'requestId': 'random-string-' + str(datetime.now().timestamp()).replace('.', ''),
                },
            },
        }

        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        return event.get('hangoutLink')

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
