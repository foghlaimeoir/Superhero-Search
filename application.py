import hashlib

import requests
import time
from config import pub_key, priv_key
import sqlite3
from flask import Flask, render_template, request, jsonify

CHARACTER_URL = 'http://gateway.marvel.com/v1/public/characters'
COMIC_URL = 'http://gateway.marvel.com/v1/public/comics'
CREATORS_URL = 'http://gateway.marvel.com/v1/public/creators'
EVENTS_URL = 'http://gateway.marvel.com/v1/public/events'
SERIES_URL = 'http://gateway.marvel.com/v1/public/series'
STORIES_URL = 'http://gateway.marvel.com/v1/public/stories'


def generate_hash_and_ts_params(): #generate hash required for API request

    timestamp = str(time.time())
    hash_value = hashlib.md5(f'{timestamp}{priv_key}{pub_key}'.encode('utf-8')).hexdigest()

    return {'ts': timestamp, 'hash': hash_value}


results = []

def paged_request(url, *args, page_size = 100, offset = 0): #make a request to Marvel's API
    params = {'apikey': pub_key, 'limit': page_size} #100 is maximum page size allowed for API requests
    for arg in args:
        params.update(arg)

    hash_params = generate_hash_and_ts_params()
    params.update(hash_params)
    params.update({'offset': offset})
    response = requests.get(url, params).json()

    results.append(response)

    return response


app = Flask(__name__)

characters =[]

@app.route('/') #on page load, retrieve character details from database
def index():
    db = sqlite3.connect('marvel.db')
    rows = db.execute("SELECT char_id, char_name, char_thumbnail FROM characters")
    for row in rows:
        id = row[0]
        name = row[1]
        thumbnail = row[2]
        characters.append({'id':id, 'name':name, 'thumbnail':thumbnail})
    db.commit()
    return render_template("index.html", characters=characters)
    if request.method == 'POST':
        print(request.form.getlist('character(s)'))
        render_template("index.html", **characters)


@app.route("/load", methods=["POST"])
def load():
    offset = request.get_json(force=True)[-1];
    names = ','.join(request.get_json(force=True)[0:-1])
    args = {'sharedAppearances': names}
    return jsonify(paged_request(COMIC_URL, args, offset=offset))



if __name__ == '__main__':
    app.run()




