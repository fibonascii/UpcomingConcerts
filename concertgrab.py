from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import pandas
import re
from datetime import datetime, timedelta
import json
#Import for google calendar api
import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try: 
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Itzel Google Music Calendar'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'concert-calendar.jon')
    
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print("Storing credentials to " + credential_path)
    
    return credentials


def make_request(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    return soup

def get_table_rows(soup):
    table = soup.find('table', {'id': 'shTable'}).find('tbody')
    rows = table.find_all('tr')
   
    concerts = []
    for row in rows:
        event = {
                 'start': {
                       'dateTime': None 
                          },
                 'end': {
                       'dateTime': None
                        }   
                 }
        cols = row.find_all('td')
        date = cols[1].get_text()
        remove_characters = re.sub('[a-zA-Z]{0,}', '', str(date))
        format_date = re.sub(r"-([2017]{0,4})([0-9]{0,2}:)", r"-\1 \2", str(remove_characters))
        
        event['summary'] = cols[0].get_text()
        event['start']['dateTime'] = format_date 
        event['location'] = cols[2].get_text()
        
        if ':' not in format_date:
            event['start']['dateTime'] = datetime.strptime(format_date, '%m-%d-%Y')
        else:
            event['start']['dateTime'] = datetime.strptime(format_date, '%m-%d-%Y %H:%M ')
        event['end']['dateTime'] = event['start']['dateTime'] + timedelta(hours=4)
    
        concerts.append(event) 

 
    return concerts

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    request = make_request('http://concertsdallas.com/')
    rows = get_table_rows(request)
    #events = build_calendar_events(rows)
  
    for row in rows:
        print(row) 
       
 #   for event in rows.values():
 #       print('Event is being created: ')
 #       concert = service.events().insert(calendarId='primary', body=event).execute()


if __name__ == '__main__':
    main() 
