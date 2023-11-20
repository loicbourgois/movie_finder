import logging
logging.basicConfig(level=logging.INFO)
logging.info("start")
import requests
from .misc import (
    endpoint_url,
)
import csv
import urllib
import os
import json
from .builder import common
import time
limit = "limit 100"
limit = ""

# SELECT ?item ?item_label (lang(?item_label) as ?lang)
#                  WHERE {
#                     ?item wdt:P279 wd:Q2431196 .
#                   ?item rdfs:label ?item_label filter (lang(?item_label) = "en").
#              }
#                limit 100


base_data_path = f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder_local/data_v2"
withs = {
    # "director": common.with_director,
    # "creator": common.with_creator,
    # "producer": common.with_producer,
    # "voice_actor": common.with_voice_actor,
    # "screenwriter": common.with_screenwriter,
    # "composer": common.with_composer,
    # "cast_member": common.with_cast_member,
    "omdb_id": "wdt:P3302",
}
media_types = {
    "film": common.film,
    "television_series": common.television_series,
    "anime": "wd:Q1107",
    "film_series": "wd:Q24856",
    "western_animation": "wd:Q83646243",
    "documentary": "wd:Q4164344",
}
folders = ['label', 'relation']


def query_to_file(path, query):
    # logging.info(query)
    args = urllib.parse.urlencode({
        'query': query,
        'format': 'json'
    })
    r = requests.get(f"{endpoint_url}?{args}")
    logging.info(f"CODE: {r.status_code}")
    write_force(path, r.text)


def pull_data_v2():
    count_total = len(withs) * len(media_types)
    counter = 0
    for media_types_k, media_types_v in media_types.items():
        # query_to_file(
        #     f"{base_data_path}/raw/label/{media_types_k}/{media_types_k}.raw",
        #     f"""
        #         SELECT ?{media_types_k} ?{media_types_k}_label (lang(?{media_types_k}_label) as ?lang)
        #         WHERE {{
        #             ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
        #             ?{media_types_k} rdfs:label ?{media_types_k}_label filter (lang(?{media_types_k}_label) = "en").
        #         }}
        #         {limit}
        #     """
        # )
        for wk, wv in withs.items():
            logging.info(f"{counter}/{count_total}")
            counter+=1
            query_to_file(
                f"{base_data_path}/raw/label/{media_types_k}/{wk}.raw",
                f"""
                    SELECT ?{wk} ?{wk}_label (lang(?{wk}_label) as ?lang)
                    WHERE {{
                        ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
                        ?{media_types_k} {wv} ?{wk} .
                        ?{wk} rdfs:label ?{wk}_label filter (lang(?{wk}_label) = "en").
                    }}
                    {limit}
                """
            )
            query_to_file(
                f"{base_data_path}/raw/relation/{media_types_k}/{wk}.raw",
                f"""
                    SELECT ?{media_types_k} ?{wk}
                        WHERE {{
                            ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
                            ?{media_types_k} {wv} ?{wk} .
                        }}
                    {limit}
                """
            )


def write_force(path, content):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, 'w') as f:
        f.write(content)


def read(path):
    with open(path, "r") as file:
        return file.read()


def write_force_csv(path, rows):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def convert_data_v2():
    for wk, wv in withs.items():
        for media_types_k, media_types_v in media_types.items():
            for xx in folders:
                path_in = f"{base_data_path}/raw/{xx}/{media_types_k}/{wk}.raw"
                path_out = f"{base_data_path}/csv/{xx}/{media_types_k}/{wk}.csv"
                try:
                    logging.info(f"  reading {path_in}")
                    str_ = read(path_in)
                    d = json.loads(str_)
                    rows = [ d['head']['vars'] ]
                    logging.info(f"    converting")
                    for x in d['results']['bindings']:
                        rows.append( [ 
                            x[aa]['value']
                            for aa in rows[0]
                        ] )
                    logging.info(f"    writing")
                    write_force_csv(path_out, rows)
                except:
                    logging.info(f"    ERROR")


def build_mapping(path_in, path_out, path_out_2, path_out_3):
    logging.info(f"  opening")
    str_ = read(path_in)
    logging.info(f"  loading")
    d = json.loads(str_)
    l = {}
    l2 = {}
    l3 = {}
    logging.info(f"  converting")
    for i,x in enumerate(d['results']['bindings']):
        k = x[d['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')
        v = x[d['head']['vars'][1]]['value'].replace('http://www.wikidata.org/entity/','')
        if len(d['head']['vars']) == 3:
            lang = x[d['head']['vars'][2]]['value'].replace('http://www.wikidata.org/entity/','')
        elif len(d['head']['vars']) == 2:
            lang = ""
        else:
            raise "error"
        if l.get(k):
            l[k][v] = ''
        else:
            l[k] = {v:''}
        if l2.get(v):
            l2[v][k] = ''
        else:
            l2[v] = {k:''}
        if l3.get(k):
            l3[k][lang] = v
        else:
            l3[k] = {lang:v}
    logging.info(f"  writing")
    write_force(path_out, "")
    write_force(path_out_2, "")
    write_force(path_out_3, "")
    with open(path_out, "w", encoding='utf-8') as file:
        json.dump(l, file, indent=2, ensure_ascii=False)
    with open(path_out_2, "w", encoding='utf-8') as file:
        json.dump(l2, file, indent=2, ensure_ascii=False)
    with open(path_out_3, "w", encoding='utf-8') as file:
        json.dump(l3, file, indent=2, ensure_ascii=False)


def build_mappings_v2():
    for media_types_k, media_types_v in media_types.items():
        xx = "label"
        build_mapping(
            f"{base_data_path}/raw/{xx}/{media_types_k}/{media_types_k}.raw",
            f"{base_data_path}/json/base/{xx}/{media_types_k}/{media_types_k}.json",
            f"{base_data_path}/json/inverted/{xx}/{media_types_k}/{media_types_k}.json",
            f"{base_data_path}/json/by_language/{xx}/{media_types_k}/{media_types_k}.json",
        )
        for wk, wv in withs.items():
            for xx in folders:
                try:
                    build_mapping(
                        f"{base_data_path}/raw/{xx}/{media_types_k}/{wk}.raw",
                        f"{base_data_path}/json/base/{xx}/{media_types_k}/{wk}.json",
                        f"{base_data_path}/json/inverted/{xx}/{media_types_k}/{wk}.json",
                        f"{base_data_path}/json/by_language/{xx}/{media_types_k}/{wk}.json",
                    )
                except Exception as e:
                    logging.info(f"    ERROR: {e}")
                    pass

# pull_data_v2()
# convert_data_v2()
build_mappings_v2()
