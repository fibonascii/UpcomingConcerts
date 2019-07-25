from __future__ import print_function
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():
    """Authenticate to google calendar api"""

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def format_datetime(event_date):
    """formats data given from Concerts and converts it into manageable """
    remove_day = re.sub(r'[A-Za-z]{0,}', '', event_date)
    add_space = re.sub(r"([0-9]-[0-9]{0,2}-[0-9]{0,4})([0-9]{0,2}:\d\d)", r"\1 \2", remove_day)
    formatted_date = datetime.strptime(add_space, '%m-%d-%Y %H:%M ').isoformat()

    return formatted_date


def get_events():
    """Get all the concerts from the event table on concertsdallas.com
    and store those events in a list of dictionaries"""

    response = requests.get("http://concertsdallas.com")
    soup = BeautifulSoup(response.text, 'lxml')

    table = soup.find("table", {"id": "shTable"}).find("tbody").find_all("tr")

    event_list = []
    for event in table:
        try:
            event_date = event.find("td", {"class": "shDateCol"}).text
            start_time = format_datetime(event_date)
            end_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=4)
            end = end_time.isoformat()

            event_dict = {
                'summary': event.find("td", {"class": "shEventCol"}).text,
                'location': event.find("td", {"class": "shVenueCol"}).text,
                'start': {
                    'dateTime': format_datetime(event_date),
                    'timeZone': 'America/Chicago'
                },
                'end': {
                    'dateTime': end,
                    'timeZone': 'America/Chicago'
                }
            }

            event_list.append(event_dict)

        except ValueError:
            pass

    return event_list


def main():
    creds = get_credentials()

    service = build('calendar', 'v3', credentials=creds)
    events = get_events()

    for event in events:
        jobj = json.dumps(event)
        concert = json.loads(jobj)
        print("Adding concert to calendar: {}".format(concert))
        service.events().insert(calendarId='mycalendarId@group.calendar.google.com',
                                body=concert).execute()


if __name__ == '__main__':
    main()
