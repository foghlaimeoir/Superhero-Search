import hashlib
import math
import sqlite3
import time
import requests
from config import priv_key, pub_key

CHARACTER_URL = 'http://gateway.marvel.com/v1/public/characters'
COMIC_URL = 'http://gateway.marvel.com/v1/public/comics'
CREATORS_URL = 'http://gateway.marvel.com/v1/public/creators'
EVENTS_URL = 'http://gateway.marvel.com/v1/public/events'
SERIES_URL = 'http://gateway.marvel.com/v1/public/series'
STORIES_URL = 'http://gateway.marvel.com/v1/public/stories'


conn = sqlite3.connect('marvel.db')
c = conn.cursor()


def generate_hash_and_ts_params():

    timestamp = str(time.time())
    hash_value = hashlib.md5(f'{timestamp}{priv_key}{pub_key}'.encode('utf-8')).hexdigest()

    return {'ts': timestamp, 'hash': hash_value}


results = []

def paged_request(url, page_size = 100):
    params = {'apikey': pub_key, 'limit': page_size} #100 is maximum page size allowed for API requests
    total = 1
    i = 0
    while i <= total:
        hash_params = generate_hash_and_ts_params()
        params.update(hash_params)
        params.update({'offset': page_size * i})
        response = requests.get(url, params)
        results.append(response.json())
        if i == 0:
            total = math.ceil(int(results[0]['data']['total'])/100)     #while loop will repeat until the total data from specified API url is requested
        i += 1
        print(response.json())


# load characters into database
paged_request(CHARACTER_URL, 100)

ids = []
names = []
thumbnails = []
descriptions = []
comics = []
stories = []
events = []
series = []

def data_entry():
    for request in results:
        for character in request['data']['results']:

            name = character['name']
            id = character['id']
            thumbnail = character['thumbnail']['path'] + '.' + character['thumbnail']['extension']
            description = character['description']
            comic_no = character['comics']['available']
            story_no = character['stories']['available']
            event_no = character['events']['available']
            series_no = character['series']['available']

            c.execute("""INSERT INTO characters (char_id, char_name, char_thumbnail, char_description, comics_no, stories_no, events_no, series_no)
                      VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (id, name, thumbnail, description, comic_no, story_no, event_no, series_no))

# load comics into database
paged_request(COMIC_URL, 100)




def data_entry():
    for request in results:
        print(request)
        for character in request['data']['results']:

            name = character['name']
            id = character['id']
            thumbnail = character['thumbnail']['path'] + '.' + character['thumbnail']['extension']
            description = character['description']
            comic_no = character['comics']['available']
            story_no = character['stories']['available']
            event_no = character['events']['available']
            series_no = character['series']['available']

            c.execute("""INSERT INTO characters (char_id, char_name, char_thumbnail, char_description, comics_no, stories_no, events_no, series_no)
                      VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (id, name, thumbnail, description, comic_no, story_no, event_no, series_no))

data_entry()
conn.commit()
conn.close()
