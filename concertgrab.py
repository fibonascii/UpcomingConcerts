import requests
from bs4 import BeautifulSoup
import pandas

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
        concert['id'].append(id_number)  
        concert['name'].append( cols[0].get_text())
        concert['date'].append( cols[1].get_text())
        concert['venue'].append( cols[2].get_text())

    concertTable = pandas.DataFrame( concert )
    concerts = concertTable.set_index('id').T.to_dict('list')
    
    return concerts

request = make_request('http://concertsdallas.com/')
rows = get_table_rows(request)
