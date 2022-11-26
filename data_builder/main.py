import logging

logging.basicConfig(level=logging.DEBUG)
logging.info("start")
import json
import os
import csv
import requests
from qwikidata.sparql import (
    get_subclasses_of_item,
    return_sparql_query_results
)
import urllib

import xmltodict
from SPARQLWrapper import XML, SPARQLWrapper

from . import (  # human_activity,; action,; activity,; professions,; social_status,
    # cat, 
    film_cast_member, 
    film_label,
    # film_label_2,
    film_director,
    film_publication,
    # occupation,
    # film_cast_member_2,
    # film_cast_member_3,
    # film_cast_member_4,
    film_image,
    film_imdb,
    film_omdb,
    film_screenwriter,
    film_voice_actor,
    voice_actor_label,
    screenwriter_label,
    cast_member_label,
    director_label,
)

data_builders = (
    # film_label,
    # film_cast_member,
    # film_director,
    # film_publication,
    # film_image,
    # film_imdb,
    # film_omdb,
    # film_screenwriter,
    # film_voice_actor,
    voice_actor_label,
    screenwriter_label,
    cast_member_label,
    # director_label,
    # film_label_old,
    # film_cast_member_2,
    # film_cast_member_3,
    # film_cast_member_4,
    # human_activity,
    # action,
    # activity,
    # occupation,
    # cat,
    #professions,
    # social_status,
) 

endpoint_url = "https://query.wikidata.org/sparql"
data = f"{os.environ['HOME']}/github.com/loicbourgois/downtowhat_local/data"


for data_builder in data_builders:
    logging.info(f"fetch {data_builder.name}")
    partial_path = f"{data}/{data_builder.name}"
    path = f"{partial_path}.raw"
    args = urllib.parse.urlencode({
        'query': data_builder.query,
        'format': 'json'
    })
    r = requests.get(f"{endpoint_url}?{args}")
    with open(path, "w") as file:
        file.write(r.text)
    logging.info(f"  {data_builder.name} -> {path}")


for data_builder in data_builders:
    logging.info(f"converting {data_builder.name}")
    partial_path = f"{data}/{data_builder.name}"
    path_in = f"{partial_path}.raw"
    path_out = f"{partial_path}.csv"
    with open(path_in, "r") as file:
        str_ = file.read()
    d = json.loads(str_)
    l = [ d['head']['vars'] ]
    for x in d['results']['bindings']:
        l.append( [ 
            x[aa]['value']
            for aa in l[0]
        ] )
    with open(path_out, "w") as file:
        writer = csv.writer(file)
        writer.writerows(l)
    logging.info(f"  {data_builder.name} -> {path_out}")


for data_builder in data_builders:
    logging.info(f"building map {data_builder.name}")
    path_in = f"{data}/{data_builder.name}.raw"
    path_out = f"{data}/map/{data_builder.name}.json"
    path_out_2 = f"{data}/map/{data_builder.name}_inverted.json"
    logging.info(f"  opening")
    with open(path_in, "r") as file:
        str_ = file.read()
    logging.info(f"  loading")
    d = json.loads(str_)
    l = {}
    l2 = {}
    length = len(d['results']['bindings'])
    length_100 = int(length/100)
    logging.info(f"  converting")
    for i,x in enumerate(d['results']['bindings']):
        if i % max(length_100, 1) == 0:
            logging.info(f'    {int(i/length*100)}%')
        k = x[d['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')
        v = x[d['head']['vars'][1]]['value'].replace('http://www.wikidata.org/entity/','')
        if l.get(k):
            l[k][v] = ''
        else:
            l[k] = {v:''}
        if l2.get(v):
            l2[v][k] = ''
        else:
            l2[v] = {k:''}
    with open(path_out, "w", encoding='utf-8') as file:
        json.dump(l, file, indent=2,ensure_ascii=False)
    with open(path_out_2, "w", encoding='utf-8') as file:
        json.dump(l2, file, indent=2,ensure_ascii=False)
    logging.info(f"  {data_builder.name} -> {path_out}")


# logging.info(f"building impawards")
# path_in = f"{data}/film_label.raw"
# path_in_2 = f"{data}/film_publication.raw"
# path_out = f"{data}/map/impawards.json"
# with open(path_in, "r") as file:
#     d = json.loads(file.read())
# with open(path_in_2, "r") as file:
#     d2 = json.loads(file.read())
# l = {}
# l2 = {}
# for x in d['results']['bindings']:
#     v = x[d['head']['vars'][1]]['value']
#     v = "_".join(v.lower().split(" ")) + ".jpg"
#     l[x[d['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')] = v
# for x in d2['results']['bindings']:
#     k = x[d2['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')
#     v2 = x[d2['head']['vars'][1]]['value'].split("-")[0]
#     v = l.get(k)
#     v_ =  "http://www.impawards.com/" + v2 + "/posters/" + v
#     if l2.get(k):
#         l2[k].append(v_)
#     else:
#         l2[k] = [v_]
# with open(path_out, "w") as file:
#     file.write(json.dumps(l2, indent=2))
