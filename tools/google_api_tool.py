import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
import datetime

# NOTE: You will need to set these environment variables
# GOOGLE_CLIENT_ID
# GOOGLE_CLIENT_SECRET
# GOOGLE_REDIRECT_URI

class GoogleAPITool:
    def __init__(self):
        # In a real application, you might load credentials differently
        pass

    def get_google_auth_url(self):
        # The client_secret.json should be downloaded from Google Cloud Console
        # and placed in the root of the project, or handled securely.
        SCOPES = [
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/tasks'
        ]
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        flow.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        return authorization_url, state

    def exchange_code_for_token(self, authorization_response):
        SCOPES = [
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/tasks'
        ]
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        flow.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        flow.fetch_token(authorization_response=authorization_response)
        return flow.credentials

    def refresh_token_if_needed(self, credentials):
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
        return credentials

    def get_calendar_service(self, credentials):
        creds = self.refresh_token_if_needed(credentials)
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
        return service

    def get_tasks_service(self, credentials):
        creds = self.refresh_token_if_needed(credentials)
        service = googleapiclient.discovery.build('tasks', 'v1', credentials=creds)
        return service

    def get_calendar_events(self, credentials, max_results=10):
        service = self.get_calendar_service(credentials)
        events_result = service.events().list(calendarId='primary', timeMin=datetime.datetime.utcnow().isoformat() + 'Z',
                                            maxResults=max_results, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def create_calendar_event(self, credentials, summary, description, start_time, end_time):
        service = self.get_calendar_service(credentials)
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event

    def get_task_lists(self, credentials):
        service = self.get_tasks_service(credentials)
        results = service.tasklists().list().execute()
        items = results.get('items', [])
        return items

    def get_tasks(self, credentials, tasklist_id='@default', max_results=10):
        service = self.get_tasks_service(credentials)
        results = service.tasks().list(tasklist=tasklist_id, maxResults=max_results, showCompleted=False).execute()
        items = results.get('items', [])
        return items

    def create_task(self, credentials, title, tasklist_id='@default'):
        service = self.get_tasks_service(credentials)
        task = {'title': title}
        result = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
        return result