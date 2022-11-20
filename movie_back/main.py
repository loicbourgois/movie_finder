import logging
logging.basicConfig(level=logging.DEBUG)
import os
from flask import (
    Flask,
    request,
    send_from_directory,
    jsonify,
)
import requests
from flask_cors import CORS
import shutil
import re
import json


cache_path = "/root/github.com/loicbourgois/downtowhat_local/cache/"


def get_image_impawards(url):
    assert url.startswith("http://www.impawards.com/")
    path = "/root/github.com/loicbourgois/downtowhat_local/cache/" + url.split("://")[1]
    small_path = path.replace('/root/github.com/loicbourgois/downtowhat_local/', '')
    if not os.path.exists(path):
        folder_path = "/".join(path.split("/")[:-1])
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            with open(path, 'w') as f:
                f.write("null")
            return None
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    if os.path.getsize(path) > 1000:
        return small_path
    else:
        return None


def mkdir_parent(path):
    parent_path = os.path.dirname(path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)


def get_image(url, path):
    full_path = cache_path + path
    if not os.path.exists(full_path):
        mkdir_parent(full_path)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(full_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            with open(full_path, 'w') as f:
                f.write("")
    if os.path.getsize(full_path) > 1000:
        return path
    else:
        return None


def get_or_pull_and_save(url, path, force=False):
    full_path = cache_path + path
    if (not os.path.exists(full_path)) or force:
        r = requests.get(url, {
            'headers': {
                'Accept-Language': 'en'
            }
        })
        if r.status_code == 200:
            content = r.text
        else:
            content = ""
        mkdir_parent(full_path)
        with open(full_path, 'w') as f:
            f.write(content)
    else:
        with open(full_path, 'r') as f:
            content = f.read()
    return content


def get_imdb_info(imdb_id, force=False):
    path_2 = f"imdb/{imdb_id}/short.json"
    path = f"imdb/{imdb_id}/raw.html"
    url = f"https://www.imdb.com/title/{imdb_id}/"
    full_path = cache_path + path_2
    if (not os.path.exists(full_path)) or force:
        raw = get_or_pull_and_save(url, path)
        x = re.findall('<script type="application\/ld\+json">({.*})<\/script><meta', raw)
        if len(x) == 1:
            short = json.dumps(json.loads(x[0]))
        else:
            short = json.dumps({})
        parent_path = os.path.dirname(full_path)
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)
        with open(full_path, 'w') as f:
            f.write(short)
    else:
        with open(full_path, 'r') as f:
            short = f.read()
    short = json.loads(short)
    if short and short.get('image'):
        image_path = get_image(short.get('image'), f"imdb/{imdb_id}/image.{short.get('image').split('.')[-1]}")
    else:
        image_path = None
    return {
        'short':short, 
        'image_path': image_path,
    }


def test():
    url = "http://www.impawards.com/2004/posters/kill_bill_vol_two.jpg"
    r = get_image_impawards(url)
    # Q72962
    r = get_imdb_info('tt0105236')


test()


app = Flask(
    __name__,
)
CORS(app)


@app.route('/about', methods = ['GET', 'POST'])
def api_about():
    r = jsonify({
        'version': 'dev',
    })
    r.headers.add("Access-Control-Allow-Origin", "*")
    return r


@app.route('/impawards', methods = ['GET','POST'])
def api_impawards():
    r = jsonify({
        'path': get_image_impawards(request.json['url']),
    })
    r.headers.add("Access-Control-Allow-Origin", "*")
    return r


@app.route('/imdb', methods = ['GET','POST'])
def api_imdb():
    r = jsonify(get_imdb_info(request.json['imdb_id']))
    r.headers.add("Access-Control-Allow-Origin", "*")
    return r