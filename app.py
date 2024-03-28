from http import client
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URL = os.environ.get('MONGODB_URL')
DB_NAME = os.environ.get('DB_NAME')


client = MongoClient(MONGODB_URL)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/movie', methods=['POST'])
def movie_post():
    url_req = request.form['url']
    star_req = request.form['star']
    comment_req = request.form['comment']
    
    url = url_req

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    data = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')['content'].split(' ')
    desc = soup.select_one('meta[property="og:description"]')['content']
    image = soup.select_one('meta[property="og:image"]')['content']
    
    movie_data = {
        'image': image,
        'title': f'{title[0]} {title[1]}',
        'desc': desc,
        'star': star_req,
        'comment': comment_req
    }
    
    db.movie.insert_one(movie_data)
    
    return jsonify({'msg': 'Data Posted Succesfully!'})

@app.route('/movie', methods=['GET'])
def movie_get():
    movies = list(db.movie.find({}, {'_id': False}))
    return jsonify({'movies': movies})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)