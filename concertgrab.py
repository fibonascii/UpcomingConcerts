import requests
from bs4 import BeautifulSoup
import pandas
import re
from datetime import datetime

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
        format_date = re.sub(r"-([2017]{0,4})([0-9]{0,1}:)", r"-\1 \2", str(remove_characters))        
        #dateTime = datetime.strptime(format_date, '%m-%d-%Y %H:%M:%S') 
         
        concert['id'].append(id_number)  
        concert['name'].append( cols[0].get_text())
        concert['date'].append( format_date)
        concert['venue'].append( cols[2].get_text())

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
        print(events)

    return events

 
request = make_request('http://concertsdallas.com/')
rows = get_table_rows(request)
build_formatting = format_events(rows)
