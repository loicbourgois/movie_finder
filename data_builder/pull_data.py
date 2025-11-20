import json
import time
import urllib

import requests

from .logger import get_logger
from .shared import aligned_advancement, path_local, read, write_force

endpoint_url = "https://query.wikidata.org/sparql"
logger = get_logger()


def query_to_file(path, query):
    start = time.time()
    args = urllib.parse.urlencode({
        'query': query,
        'format': 'json'
    })
    headers = {
        'User-Agent': 'movie_finder/v2'
    }
    try:
        r = requests.get(
            f"{endpoint_url}?{args}",
            timeout=60*5,
            headers= headers,
        )
        logger.info(f"  {r.status_code} - {path_local(path)} - {int(time.time()-start)}")
        if r.status_code != 200:
            logger.info(r.text)
        write_force(path, r.text)
    except:
        logger.exception(f"  failed - {path_local(path)}")
    end = time.time()
    time.sleep( max(0, 3 - (end - start)) )


def pull_data(config, queries):
    remaining_queries = {}
    for i, (k, v) in enumerate(queries.items()):
        path_json = "/root/github.com/loicbourgois/movie_finder_local/data_v3/json/" + k + ".json"
        try:
            c = json.loads(read(path_json))
            logger.info(f"(skip) {aligned_advancement(i,len(queries))} - {path_local(path_json)} - {len(c['results']['bindings'])}")
        except Exception:
            logger.info(f"(todo) {aligned_advancement(i,len(queries))} - {path_local(path_json)}")
            remaining_queries[k] = v
    for i, (k, v) in enumerate(remaining_queries.items()):
        path_json = "/root/github.com/loicbourgois/movie_finder_local/data_v3/json/" + k + ".json"
        if k in config['custom']:
            logger.info(f"(skip) {aligned_advancement(i,len(remaining_queries))} - {path_local(path_json)}")
        else:
            logger.info(f"(pull) {aligned_advancement(i,len(remaining_queries))} - {path_local(path_json)}")
            query_to_file(path_json, v)
