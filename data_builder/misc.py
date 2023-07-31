import json
import os
import csv
import requests
import logging
import urllib
logging.basicConfig(level=logging.DEBUG)


endpoint_url = "https://query.wikidata.org/sparql"
data = f"{os.environ['HOME']}/github.com/loicbourgois/downtowhat_local/data"


def pull_data(data_builders):
    for i_data_builder, data_builder in enumerate(data_builders):
        logging.info(f"{i_data_builder+1}/{len(data_builders)} - fetch {data_builder.name}")
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


def convert_data(data_builders):
    for i_data_builder, data_builder in enumerate(data_builders):
        logging.info(f"{i_data_builder+1}/{len(data_builders)} - converting {data_builder.name}")
        partial_path = f"{data}/{data_builder.name}"
        path_in = f"{partial_path}.raw"
        path_out = f"{partial_path}.csv"
        logging.info(f"  reading")
        with open(path_in, "r") as file:
            str_ = file.read()
        d = json.loads(str_)
        l = [ d['head']['vars'] ]
        logging.info(f"  converting")
        for x in d['results']['bindings']:
            l.append( [ 
                x[aa]['value']
                for aa in l[0]
            ] )
        logging.info(f"  writing")
        with open(path_out, "w") as file:
            writer = csv.writer(file)
            writer.writerows(l)
        logging.info(f"  {data_builder.name} -> {path_out}")


def build_mappings(data_builders):
    for i_data_builder, data_builder in enumerate(data_builders):
        logging.info(f"{i_data_builder+1}/{len(data_builders)} - building map {data_builder.name}")
        path_in = f"{data}/{data_builder.name}.raw"
        path_out = f"{data}/map/{data_builder.name}.json"
        path_out_2 = f"{data}/map/{data_builder.name}_inverted.json"
        path_out_3 = f"{data}/map/{data_builder.name}_by_language.json"
        logging.info(f"  opening")
        with open(path_in, "r") as file:
            str_ = file.read()
        logging.info(f"  loading")
        d = json.loads(str_)
        l = {}
        l2 = {}
        l3 = {}
        length = len(d['results']['bindings'])
        length_100 = int(length/100)
        logging.info(f"  converting")
        for i,x in enumerate(d['results']['bindings']):
            # if i % max(length_100, 1) == 0:
            #     logging.info(f'    {int(i/length*100)}%')
            k = x[d['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')
            v = x[d['head']['vars'][1]]['value'].replace('http://www.wikidata.org/entity/','')
            if len(d['head']['vars']) >= 3:
                lang = x[d['head']['vars'][2]]['value'].replace('http://www.wikidata.org/entity/','')
            else:
                lang = ""
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
        with open(path_out, "w", encoding='utf-8') as file:
            json.dump(l, file, indent=2,ensure_ascii=False)
        with open(path_out_2, "w", encoding='utf-8') as file:
            json.dump(l2, file, indent=2,ensure_ascii=False)
        with open(path_out_3, "w", encoding='utf-8') as file:
            json.dump(l3, file, indent=2,ensure_ascii=False)
        logging.info(f"  {data_builder.name} -> {path_out}")


def build_impawards():
    logging.info(f"building impawards")
    path_in = f"{data}/film_label.raw"
    path_in_2 = f"{data}/film_publication.raw"
    path_out = f"{data}/map/impawards.json"
    with open(path_in, "r") as file:
        d = json.loads(file.read())
    with open(path_in_2, "r") as file:
        d2 = json.loads(file.read())
    l = {}
    l2 = {}
    for x in d['results']['bindings']:
        v = x[d['head']['vars'][1]]['value']
        v = "_".join(v.lower().split(" ")) + ".jpg"
        l[x[d['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')] = v
    for x in d2['results']['bindings']:
        k = x[d2['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')
        v2 = x[d2['head']['vars'][1]]['value'].split("-")[0]
        v = l.get(k)
        v_ =  "http://www.impawards.com/" + v2 + "/posters/" + v
        if l2.get(k):
            l2[k].append(v_)
        else:
            l2[k] = [v_]
    with open(path_out, "w") as file:
        file.write(json.dumps(l2, indent=2))