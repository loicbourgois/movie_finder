import logging
logging.basicConfig(level=logging.INFO)
logging.info("start")
import sys
import os
import hashlib
import pathlib
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from .sparqle_query import (
    query,
    root
)
endpoint_url = "https://query.wikidata.org/sparql"
data = f"{os.environ['HOME']}/github.com/loicbourgois/downtowhat_local/data"
def get_response(endpoint_url, query):
    # TODO better user agent; see https://w.wiki/CX6
    user_agent = "downtowhat/latest (downtowhat.com)"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
query_hash = hashlib.sha256(query.replace(" ","").strip().encode('utf-8')).hexdigest()

query_path = f"{data}/sparqle/{query_hash}"
pathlib.Path(query_path).mkdir(parents=True, exist_ok=True)

with open(f"{query_path}/query.txt", "w") as file:
    file.write(query)

response_path = f"{query_path}/response.json"
logging.info(f"running query: {query}")
response = get_response(endpoint_url, query)
with open(response_path, "w") as file:
    file.write(json.dumps(response))
with open(response_path, "r") as file:
    response = json.load(file)


subclass_lines = ["parent_id|child_id"]
label_lines = ["item_id|language|label"]
item_lines = {}


for (i, result) in enumerate(response["results"]["bindings"]):
    item_uri = result["item"]['value']
    item = item_uri.replace("http://www.wikidata.org/entity/Q", "")
    default_label = result["itemLabel"]['value']
    label_lines.append(f"{item}|default|{default_label}")
    item_lines[item] = True
    for lang in ['en','es','it','fr']:
        if result.get(f'label_{lang}'):
            label_lines.append(f"{item}|{lang}|{result[f'label_{lang}']['value']}")
    try:
        pc_u1_uri = result['parent_class_up']['value']
        pc_u1 = pc_u1_uri.replace("http://www.wikidata.org/entity/Q","")
        subclass_lines.append(f"{pc_u1}|{item}")
    except:
        pc_u1_uri = None
        pc_u1 = None
        subclass_lines.append(f"{root.replace('Q','')}|{item}")
    # try:
    #     pc_u2_uri = result['parent_class_up_up']['value']
    #     pc_u2 = pc_u2_uri.replace("http://www.wikidata.org/entity/Q","")
    # except:
    #     pc_u2_uri = None
    #     pc_u2 = None
    # try:
    #     pc_u3_uri = result['parent_class_up_up_up']['value']
    #     pc_u3 = pc_u3_uri.replace("http://www.wikidata.org/entity/Q","")
    # except:
    #     pc_u3_uri = None
    #     pc_u3 = None
    # try:
    #     pc_u4_uri = result['parent_class_up_up_up_up']['value']
    #     pc_u4 = pc_u4_uri.replace("http://www.wikidata.org/entity/","")
    # except:
    #     pc_u4_uri = None
    #     pc_u4 = None


with open(f"{query_path}/subclass.csv", "w") as file:
    file.write("\n".join(subclass_lines))


with open(f"{query_path}/label.csv", "w") as file:
    file.write("\n".join(label_lines))


lines = ["item", root.replace('Q','')] + list(item_lines.keys())
with open(f"{query_path}/item.csv", "w") as file:
    file.write("\n".join(lines))


logging.info(f"{query_hash=}")
