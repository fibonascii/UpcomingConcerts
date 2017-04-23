from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import pandas
import re
from datetime import datetime
from dateutil.parser import *

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
    table = soup.find('table', {'id': 'shTable'})
    rows = table.find_all('tr')
    
    concert = {
           'id' : [],
           'name' : [],
           'date' : [],
           'venue': []
           }
    
    for id_number, row in enumerate(rows):
        cols = row.find_all('td')
        date = cols[1].get_text()
        remove_characters = re.sub('[a-zA-Z]{0,}', '', str(date))
        format_date = re.sub(r"-([2017]{0,4})([0-9]{0,2}:)", r"-\1 \2", str(remove_characters))        
      
        concert['id'].append(id_number) 
        concert['name'].append( cols[0].get_text())
        concert['date'].append( format_date)
        concert['venue'].append( cols[2].get_text())

# This needs to be refactored. At some point the when I'm grabbing the tables rows, the first index is empty. 
# This section removes that empty list

    concert['id'].pop(0)
    concert['name'].pop(0)
    concert['date'].pop(0)
    concert['venue'].pop(0)



# This portion loops through the new dictionary of lists and updates the values with a datetime format from string
# Not all concerts on the website have an announced time so check to see if it does or not
   
    for i, date  in enumerate(concert['date']):
        if ':' not in date:
            concert['date'][i] = datetime.strptime(date, '%m-%d-%Y')        
        else:
            concert['date'][i] = datetime.strptime(date, '%m-%d-%Y %H:%M ')

    concertTable = pandas.DataFrame( concert )
    concerts = concertTable.set_index('id').T.to_dict('list')
 
    return concerts


def format_events(concerts):
    events = {
     'summary': [],
     'location': [],
     'start': {
     'datetime': [] },
     'end': {
     'datetime': [] },
          
    }

    for concert in concerts.values():
        events['location'] = concert[2]
        events['summary'] = concert[1]
        events['start']['datetime'] = concert[0]
        events['end']['datetime'] = concert[0]

    return events

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    request = make_request('http://concertsdallas.com/')
    rows = get_table_rows(request)
    events = format_events(rows)

    for event in events.values():
        concert = service.events().insert(calendarId='primary', body=event).execute()
        print('Event is being created: {}'.format(event['summary']))


if __name__ == '__main__':
    main() 
