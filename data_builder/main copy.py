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
    cat, film_cast_member, 
    film_label,
    film_director,
    film_publication,
    occupation,
    film_cast_member_2,
    film_cast_member_3,
    film_cast_member_4,
)

data_builders = (
    film_label,
    film_cast_member,
    film_director,
    film_publication,
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


# def get_results(endpoint_url, query):
#     # TODO better user agent; see https://w.wiki/CX6
#     user_agent = "downtowhat/latest (downtowhat.com)"
#     sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
#     sparql.setQuery(query)
#     # sparql.setReturnFormat(XML)
#     logging.info(sparql)
#     return a
#     return sparql.query()


# for data_builder in data_builders:
#     logging.info(f"fetch {data_builder.name}")
#     partial_path = f"{data}/{data_builder.name}"
#     path = f"{partial_path}.raw"
#     args = urllib.parse.urlencode({
#         'query': data_builder.query,
#         'format': 'json'
#     })
#     r = requests.get(f"https://query.wikidata.org:443/sparql?{args}")
#     with open(f"{path}", "w") as file:
#         file.write(r.text)
#     logging.info(f"  {data_builder.name} -> {path}")


for data_builder in data_builders:
    logging.info(f"convert {data_builder.name}")
    partial_path = f"{data}/{data_builder.name}"
    path_in = f"{partial_path}.raw"
    path_out = f"{partial_path}.csv"
    with open(f"{path}", "r") as file:
        str_ = file.read()
    d = json.loads(str_)
    list_ = [ [ d['head']['vars'] ] ]
    for x in d['results']['bindings']:
        list_.append( [ x[x[0][0]]['value'], x[x[0][1]]['value']  ] )
    
    logging.info(f"  {data_builder.name} -> {path_out}")