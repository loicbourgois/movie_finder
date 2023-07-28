import logging
logging.basicConfig(level=logging.INFO)
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


def force_write(path, content):
    mkdir_parent(path)
    with open(path, 'w') as f:
            f.write(content)


def mkdir_parent(path):
    parent_path = os.path.dirname(path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)


def get_image(url, path, force=False):
    full_path = cache_path + path
    if not os.path.exists(full_path) or force:
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
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:107.0) Gecko/20100101 Firefox/107.0',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        })
        if r.status_code == 200:
            content = r.text
        else:
            content = r.text
            logging.warn(f" {url} : {r.status_code}")
        force_write(full_path, content)
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
        raw = get_or_pull_and_save(url, path, force)
        x = re.findall('<script type="application\/ld\+json">({.*})<\/script><meta', raw)
        if len(x) == 1:
            short = json.dumps(json.loads(x[0]))
        else:
            short = json.dumps({})
        force_write(full_path, short)
    else:
        with open(full_path, 'r') as f:
            short = f.read()
    short = json.loads(short)
    if short and short.get('image'):
        image_path = get_image(
            short.get('image'), 
            f"imdb/{imdb_id}/image.{short.get('image').split('.')[-1]}",
            force
        )
    else:
        image_path = None
    return {
        'short':short, 
        'image_path': image_path,
    }


def get_omdb_info(id, force=False):
    path_raw = f"omdb/{id}/raw.html"
    path_description = f"omdb/{id}/description.json"
    url_raw = f"https://www.omdb.org/movie/{id}"
    full_path_raw = cache_path + path_raw
    if (not os.path.exists(full_path_raw)) or force:
        raw = get_or_pull_and_save(url_raw, path_raw, force)
        x = re.findall('<meta property="og:image" content="https:\/\/www.omdb.org\/image\/default\/(.*)\.jpeg', raw)
        if len(x) == 1:
            image_id = x[0]
        else:
            image_id = None
        description = {
            'image_id':image_id,
        }
        if image_id:
            description['image_url'] = f'https://www.omdb.org/image/default/{image_id}.jpeg'
        force_write(path_description, json.dumps(description, indent=2))
    else:
        try:
            with open(path_description, 'r') as f:
                description = json.loads(f.read())
        except Exception:
            description = {}
            logging.error(f"error opening file {path_description}")
            if not force:
                return get_omdb_info(id, True)
    if description and description.get('image_url'):
        image_path = get_image(
            description.get('image_url'), 
            f"omdb/{id}/image.{description.get('image_url').split('.')[-1]}",
            force,
        )
    else:
        image_path = None
    return { 
        'description': description,
        'image_path': image_path
    }


def test():
    url = "http://www.impawards.com/2004/posters/kill_bill_vol_two.jpg"
    r = get_image_impawards(url)
    r = get_imdb_info('tt0105236')
    r = get_omdb_info('8392', True)


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


@app.route('/omdb', methods = ['GET','POST'])
def api_omdb():
    r = jsonify(get_omdb_info(request.json['omdb_id']))
    r.headers.add("Access-Control-Allow-Origin", "*")
    return r