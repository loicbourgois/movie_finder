import logging
logging.basicConfig(level=logging.INFO)
logging.info("start")
import requests
import pandas
from .misc import (
    endpoint_url,
)
import functools
import csv
import urllib
import os
import json
from .builder import common
import time
limit = "limit 100"
limit = ""


base_data_path = f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder_local/data_v2"
withs = {
    "director": "wdt:P57",
    # "creator": common.with_creator,
    # "producer": common.with_producer,
    # "voice_actor": common.with_voice_actor,
    # "screenwriter": common.with_screenwriter,
    # "composer": common.with_composer,
    # "cast_member": common.with_cast_member,
    # "omdb_id": "wdt:P3302",
    # "imdb_id": "wdt:P345",
    # "genre": "wdt:P136",
    # "review_score": "wdt:P444", -- deprecated
}
media_types = {
    "film": common.film,
    # "television_series": common.television_series,
    # "anime": "wd:Q1107",
    # "film_series": "wd:Q24856",
    # "western_animation": "wd:Q83646243",
    # "documentary": "wd:Q4164344",
}
languages = {
    'en',
    'fr',
    'ja',
}
folders = ['label', 'relation']


subject_predicate_object = {
    "film": {
        "director",
    }
}


def query_to_file(path, query):
    logging.info(path)
    logging.info(query)
    try:
        c = json.loads(read(path))
        logging.info("  file already exists")
    except Exception as e:
        logging.error(e)
        args = urllib.parse.urlencode({
            'query': query,
            'format': 'json'
        })
        r = requests.get(f"{endpoint_url}?{args}")
        logging.info(f"CODE: {r.status_code}")
        write_force(path, r.text)


def pull_data_relations():
    count_total = len(withs) * len(media_types)
    counter = 0
    for media_types_k, media_types_v in media_types.items():
        for wk, wv in withs.items():
            logging.info(f"{counter}/{count_total}")
            counter+=1
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


def pull_data_labels():
    count_total = (len(withs) + 1) * len(media_types) * len(languages)
    counter = 0
    for lang in languages:
        for media_types_k, media_types_v in media_types.items():
            logging.info(f"{counter}/{count_total}")
            counter+=1
            query_to_file(
                f"{base_data_path}/raw/label/{lang}/{media_types_k}/{media_types_k}.raw",
                f"""
                    SELECT ?{media_types_k} ?{media_types_k}_label (lang(?{media_types_k}_label) as ?lang)
                    WHERE {{
                        ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
                        ?{media_types_k} rdfs:label ?{media_types_k}_label filter (lang(?{media_types_k}_label) = "{lang}").
                    }}
                    {limit}
                """
            )
            for wk, wv in withs.items():
                logging.info(f"{counter}/{count_total}")
                counter+=1
                query_to_file(
                    f"{base_data_path}/raw/label/{lang}/{media_types_k}/{wk}.raw",
                    f"""
                        SELECT ?{wk} ?{wk}_label (lang(?{wk}_label) as ?lang)
                        with {{
                            SELECT distinct ?{wk}
                            WHERE {{
                                ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
                                ?{media_types_k} {wv} ?{wk} .
                            }}
                        }} as %i
                        where {{
                            include %i
                            ?{wk} rdfs:label ?{wk}_label filter (lang(?{wk}_label) = "{lang}").
                        }}
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


# def convert_data_v2():
#     for wk, wv in withs.items():
#         for media_types_k, media_types_v in media_types.items():
#             for xx in folders:
#                 path_in = f"{base_data_path}/raw/{xx}/{media_types_k}/{wk}.raw"
#                 path_out = f"{base_data_path}/csv/{xx}/{media_types_k}/{wk}.csv"
#                 try:
#                     logging.info(f"  reading {path_in}")
#                     str_ = read(path_in)
#                     d = json.loads(str_)
#                     rows = [ d['head']['vars'] ]
#                     logging.info(f"    converting")
#                     for x in d['results']['bindings']:
#                         rows.append( [ 
#                             x[aa]['value']
#                             for aa in rows[0]
#                         ] )
#                     logging.info(f"    writing")
#                     write_force_csv(path_out, rows)
#                 except:
#                     logging.info(f"    ERROR")


def build_mapping(path_in, path_out, path_out_2, path_out_3, path_out_4):
    try:
        logging.info(f"{path_in}")
        logging.info(f"  opening")
        str_ = read(path_in)
        logging.info(f"  loading")
        d = json.loads(str_)
        l = {}
        l2 = {}
        l3 = {}
        l4 = {}
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
            if l4.get(k):
                l4[k][i] = v
            else:
                l4[k] = {i:v}
        logging.info(f"  writing")
        logging.info(f"      {path_out}")
        logging.info(f"      {path_out_2}")
        logging.info(f"      {path_out_3}")
        logging.info(f"      {path_out_4}")
        write_force(path_out, "")
        write_force(path_out_2, "")
        write_force(path_out_3, "")
        write_force(path_out_4, "")
        with open(path_out, "w", encoding='utf-8') as file:
            json.dump(l, file, indent=2, ensure_ascii=False)
        with open(path_out_2, "w", encoding='utf-8') as file:
            json.dump(l2, file, indent=2, ensure_ascii=False)
        with open(path_out_3, "w", encoding='utf-8') as file:
            json.dump(l3, file, indent=2, ensure_ascii=False)
        with open(path_out_4, "w", encoding='utf-8') as file:
            json.dump(l4, file, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.info(f"    ERROR: {e}")


def build_mappings_v2():
    folder = "label"
    for lang in languages:
        for media_types_k, media_types_v in media_types.items():
            build_mapping(
                f"{base_data_path}/raw/{folder}/{lang}/{media_types_k}/{media_types_k}.raw",
                f"{base_data_path}/json/base/{folder}/{lang}/{media_types_k}/{media_types_k}.json",
                f"{base_data_path}/json/inverted/{folder}/{lang}/{media_types_k}/{media_types_k}.json",
                f"{base_data_path}/json/by_language/{folder}/{lang}/{media_types_k}/{media_types_k}.json",
                f"{base_data_path}/json/4/{folder}/{lang}/{media_types_k}/{media_types_k}.json",
            )
            for wk, wv in withs.items():
                build_mapping(
                    f"{base_data_path}/raw/{folder}/{lang}/{media_types_k}/{wk}.raw",
                    f"{base_data_path}/json/base/{folder}/{lang}/{media_types_k}/{wk}.json",
                    f"{base_data_path}/json/inverted/{folder}/{lang}/{media_types_k}/{wk}.json",
                    f"{base_data_path}/json/by_language/{folder}/{lang}/{media_types_k}/{wk}.json",
                    f"{base_data_path}/json/4/{folder}/{lang}/{media_types_k}/{wk}.json",
                )
    folder = "relation"
    for media_types_k, media_types_v in media_types.items():
        for wk, wv in withs.items():
            build_mapping(
                f"{base_data_path}/raw/{folder}/{media_types_k}/{wk}.raw",
                f"{base_data_path}/json/base/{folder}/{media_types_k}/{wk}.json",
                f"{base_data_path}/json/inverted/{folder}/{media_types_k}/{wk}.json",
                f"{base_data_path}/json/by_language/{folder}/{media_types_k}/{wk}.json",
                f"{base_data_path}/json/4/{folder}/{media_types_k}/{wk}.json",
            )


def transform_omdb_data_2():
    df = pandas.read_csv(
        f"{base_data_path}/movie_links.csv",
        escapechar= "\\"
    )
    logging.info(df.head())
    logging.info(df.source.unique())
    data = {}
    df_2 = df[df['source']=="wikidata"]
    for key in df_2.key.unique():
        data[key] = {}
        for _, x in df_2[ df_2['key']==key ].iterrows():
            data[key][ x['movie_id'] ] = ""
    write_force(
        f"{base_data_path}/json/wikidata_id/omdb_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def transform_omdb_data_3():
    df = pandas.read_csv(
        f"{base_data_path}/movie_links.csv",
        escapechar= "\\"
    )
    logging.info(df.head())
    logging.info(df.source.unique())
    data = {}
    df_2 = df[df['source']=="imdbmovie"]
    for key in df_2.key.unique():
        data[key] = {}
        for _, x in df_2[ df_2['key']==key ].iterrows():
            data[key][ x['movie_id'] ] = ""
    write_force(
        f"{base_data_path}/json/imdb_id/omdb_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def omdb_id__omdb_image_id__omdb_image_version():
    df = pandas.read_csv(f"{base_data_path}/image_ids.csv")
    logging.info(df.head())
    data = {}
    df_2 = df[df['object_type']=="Movie"]
    for object_id in df_2.object_id.unique():
        data[object_id] = {}
        for _, x in df_2[df_2['object_id']==object_id].iterrows():
            data[object_id][x['image_id']] = x['image_version'].replace("\\N", "")
    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    write_force(
        f"{base_data_path}/proper/omdb_id__omdb_image_id__omdb_image_version.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_id__omdb_id():
    data = {}
    zoop = json.loads(read(f"{base_data_path}/json/imdb_id/omdb_id.json"))
    for media in media_types:
        logging.info(len(data))
        path_in = f"{base_data_path}/json/base/relation/{media}/omdb_id.json"
        for k, v in json.loads(read(path_in)).items():
            if not data.get(k):
                data[k] = {}
            for k2 in v:
                data[k][k2] = ""
    logging.info(len(data))
    for k, v in json.loads(read(f"{base_data_path}/json/wikidata_id/omdb_id.json")).items():
        if not data.get(k):
            data[k] = {}
        for k2 in v:
            data[k][k2] = ""
    logging.info(len(data))
    for media in media_types:
        for k, v in json.loads(read(f"{base_data_path}/json/base/relation/{media}/imdb_id.json")).items():
            if not data.get(k):
                data[k] = {}
            for k2 in v:
                wikidata_id = k
                imdb_id = k2
                omdb_ids = zoop.get(imdb_id,{})
                for omdb_id in omdb_ids:
                    data[wikidata_id][omdb_id] = ""
    logging.info(len(data))
    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    logging.info(len(data))
    write_force(
        f"{base_data_path}/proper/wikidata_id__omdb_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_id__omdb_image_id__omdb_image_version():
    zoop = json.loads(read(f"{base_data_path}/json/omdb_id/omdb_image_id/omdb_image_version.json"))
    data = {}
    for k, v in json.loads(read(f"{base_data_path}/proper/wikidata_id__omdb_id.json")).items():
        if not data.get(k):
            data[k] = {}
        for k2 in v:
            for k3, v3 in zoop.get(k2, {}).items():
                data[k][k3] = v3
    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    logging.info(len(data))
    write_force(
        f"{base_data_path}/proper/wikidata_id__omdb_image_id__omdb_image_version.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_label__omdb_image_id__omdb_image_version():
    zoop = json.loads(read(f"{base_data_path}/proper/wikidata_id__omdb_image_id__omdb_image_version.json"))
    logging.info(len(zoop))
    data = {}
    for x in media_types:
        for k, v in json.loads(read(f"{base_data_path}/json/inverted/label/{x}/{x}.json")).items():
            for k2 in v:
                label = k
                wikidata_id = k2
                for k3, v3 in zoop.get(wikidata_id,{}).items():
                    if not data.get(label):
                        data[label] = {}
                    data[label][k3] = v3
        logging.info(len(data))
    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    logging.info(len(data))
    write_force(
        f"{base_data_path}/proper/wikidata_label__omdb_image_id__omdb_image_version.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_label__wikidata_id():
    data = {}
    for x in media_types:
        path = f"{base_data_path}/json/inverted/label/{x}/{x}.json"
        try:
            for k, v in json.loads(read(path)).items():
                for k2 in v:
                    label = k
                    wikidata_id = k2
                    if not data.get(label):
                        data[label] = {}
                    data[label][wikidata_id] = ""
        except:
            logging.error(f"Error: {path}")
        for y in withs:
            try:
                path = f"{base_data_path}/json/inverted/label/{x}/{y}.json"
                for k, v in json.loads(read(path)).items():
                    for k2 in v:
                        label = k
                        wikidata_id = k2
                        if not data.get(label):
                            data[label] = {}
                        data[label][wikidata_id] = ""
            except:
                logging.error(f"Error: {path}")
    logging.info(len(data))
    write_force(
        f"{base_data_path}/proper/wikidata_label__wikidata_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def find_by_label(value):
    data = json.loads(read(f"{base_data_path}/proper/wikidata_label__omdb_image_id__omdb_image_version.json"))
    for k, v in data.items():
        if value.lower() in k.lower():
            for k2, v2 in v.items():
                logging.info(f"{k}: https://www.omdb.org/image/default/{k2}.jpeg?v={v2}")


def find_by_label_2(value):
    data = json.loads(read(f"{base_data_path}/proper/wikidata_label__wikidata_id.json"))
    for k, v in data.items():
        if value.lower() in k.lower():
            for k2, v2 in v.items():
                logging.info(f"{k}: {k2}")


def omdb_id__omdb_image_id():
    df = pandas.read_csv(f"{base_data_path}/image_ids.csv")
    logging.info(df.head())
    data = {}
    df_2 = df[df['object_type']=="Movie"]
    for object_id in df_2.object_id.unique():
        data[object_id] = {}
        for _, x in df_2[df_2['object_id']==object_id].iterrows():
            data[object_id][x['image_id']] = ""
    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    write_force(
        f"{base_data_path}/proper/omdb_id__omdb_image_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_id__genre():
    data = {}
    for m in media_types:
        path = f"{base_data_path}/json/base/relation/{m}/genre.json"
        a = json.loads(read(path))
        for k, v in a.items():
            for k2 in v:
                if not data.get(k):
                    data[k] = {}
                data[k][k2] = ""
    write_force(
        f"{base_data_path}/proper/wikidata_id__genre.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_id__imdb_id():
    data = {}
    for m in media_types:
        path = f"{base_data_path}/json/base/relation/{m}/imdb_id.json"
        a = json.loads(read(path))
        for k, v in a.items():
            for k2 in v:
                if not data.get(k):
                    data[k] = {}
                data[k][k2] = ""
    write_force(
        f"{base_data_path}/proper/wikidata_id__imdb_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )

def wikidata_id__review():
    # for media_types_k, media_types_v in media_types.items():
    #     query_to_file(
    #         f"{base_data_path}/raw/relation/{media_types_k}/review.raw",
    #         f"""
    #             SELECT ?item ?review_score ?reviewer WHERE {{
    #                 ?item {common.instance_of_any_subclass_of} {media_types_v} .
    #                 {{ ?item p:P444 ?review . ?review pq:P447 ?reviewer ; ps:P444 ?review_score }}
    #             }}
    #         """
    #     )
    data = {}
    for m in media_types:
        d = json.loads(read(f"{base_data_path}/raw/relation/{m}/review.raw"))
        for i,x in enumerate(d['results']['bindings']):
            a = x[d['head']['vars'][0]]['value'].replace('http://www.wikidata.org/entity/','')
            b = x[d['head']['vars'][1]]['value'].replace('http://www.wikidata.org/entity/','')
            c = x[d['head']['vars'][2]]['value'].replace('http://www.wikidata.org/entity/','')
            if not data.get(a):
                data[a] = {"scores":[]}
            score = None
            b_ = b.replace(",", ".") 
            if b[-1] == "%":
                score = float(b_[0:-1]) / 100
            elif len(b.split("/")) == 2:
                if b_.split("/")[0] == "tbd":
                    continue
                if " " in b:
                    continue
                score = float(b_.split("/")[0]) / float(b_.split("/")[1])
            else:
                try:
                    aa = float(b.replace(",","."))
                    if aa > 10:
                        score = aa / 100
                    else:
                        score = aa / 10
                except:
                    logging.error(f"invalid score: {b}")
            data[a]['scores'].append({
                'score_str': b,
                'reviewer': c,
                'score': score,
            })
            sum_ = 0
            c = 0
            for s in data[a]['scores']:
                if s['score'] is not None:
                    c +=1
                    sum_ += s['score']
            if c > 0:
                data[a]['mean_score'] = sum_ / c
            else:
                data[a]['mean_score'] = None
    write_force(
        f"{base_data_path}/proper/wikidata_id__review.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wikidata_id__language__label():
    data = {}
    for l in languages:
        for m in media_types:
            path = f"{base_data_path}/json/base/label/{l}/{m}/{m}.json"
            a = json.loads(read(path))
            for k, v in a.items():
                for k2 in v:
                    if not data.get(k):
                        data[k] = {}
                    data[k][l] = k2
    write_force(
        f"{base_data_path}/proper/wikidata_id__language__label.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def director__language__label():
    data = {}
    for l in languages:
        for m in media_types:
            try:
                path = f"{base_data_path}/json/base/label/{l}/{m}/director.json"
                a = json.loads(read(path))
                for k, v in a.items():
                    for k2 in v:
                        if not data.get(k):
                            data[k] = {}
                        data[k][l] = k2
            except:
                pass
    write_force(
        f"{base_data_path}/proper/director__language__label.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def wmedia_id__wdirector_id():
    data = {}
    for m in media_types:
        path = f"{base_data_path}/json/base/relation/{m}/director.json"
        a = json.loads(read(path))
        for k, v in a.items():
            for k2 in v:
                if not data.get(k):
                    data[k] = {}
                data[k][k2] = ""
    write_force(
        f"{base_data_path}/proper/wmedia_id__wdirector_id.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def media_wikidata_id__media_with_image():
    a = json.loads(read(f"{base_data_path}/proper/wikidata_id__omdb_id.json"))
    b = json.loads(read(f"{base_data_path}/proper/omdb_id__omdb_image_id__omdb_image_version.json"))
    c = json.loads(read(f"{base_data_path}/proper/wikidata_id__language__label.json"))
    d = json.loads(read(f"{base_data_path}/proper/wikidata_id__genre.json"))
    e = json.loads(read(f"{base_data_path}/proper/wikidata_id__review.json"))
    f = json.loads(read(f"{base_data_path}/proper/wikidata_id__imdb_id.json"))
    g = json.loads(read(f"{base_data_path}/proper/wmedia_id__wdirector_id.json"))
    data = {}
    for k, v in a.items():
        for k2 in v:
            b_item = b.get(k2)
            c_item = c.get(k)
            d_item = d.get(k, {})
            e_item = e.get(k, {})
            f_item = f.get(k, {})
            g_item = g.get(k, {})
            if b_item and c_item:
                if not data.get(k):
                    data[k] = {
                        "image_url": {},
                        "omdb_id": {},
                        "label": {},
                        "genre": {},
                        "omdb_url": {},
                        "imdb_url": {},
                        "review": {},
                        "director": {},
                        "wikidata_url": f"https://www.wikidata.org/wiki/{k}",
                    }
                data[k]["omdb_id"][k2] = ""
                data[k]["omdb_url"][f"https://www.omdb.org/movie/{k2}"] = ""
                for k3, v3 in f_item.items():
                    data[k]["imdb_url"][f"https://www.imdb.com/title/{k3}"] = ""
                for k3, v3 in b_item.items():
                    data[k]["image_url"][f"https://www.omdb.org/image/default/{k3}.jpeg?v={v3}"] = ""
                for k3, v3 in c_item.items():
                    data[k]["label"][k3] = v3
                for k3, v3 in d_item.items():
                    data[k]["genre"][k3] = v3
                data[k]["review"] = e_item
                for k3, v3 in g_item.items():
                    data[k]["director"][k3] = v3
    write_force(
        f"{base_data_path}/proper/media_wikidata_id__media_with_image.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def directors():
    a = json.loads(read(f"{base_data_path}/proper/media_wikidata_id__media_with_image.json"))
    b = json.loads(read(f"{base_data_path}/proper/wmedia_id__wdirector_id.json"))
    c = json.loads(read(f"{base_data_path}/proper/director__language__label.json"))
    data = {}
    for k, v in b.items():
        for k2 in v:
            if not data.get(k2):
                data[k2] = {
                    'label': {},
                    'wikidata_url': f"https://www.wikidata.org/wiki/{k2}",
                    'media': {},
                }
            if a.get(k):
                data[k2]['media'][k] = a[k]
            data[k2]["label"] = c.get(k2)

    for k, v in data.items():
        sum_ = 0
        count_ = 0
        for k2, v2 in v['media'].items():
            # logging.info(v2)
            for k3 in v2['review'].get('scores', []):
                if k3['score']:
                    sum_ += k3['score']
                    count_ += 1
        if count_:
            data[k]['score_mean'] = sum_/count_
            data[k]['score_count'] = count_
        else:
            data[k]['score_mean'] = None
            data[k]['score_count'] = None
    write_force(
        f"{base_data_path}/proper/directors.json",
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def top():
    data = json.loads(read(f"{base_data_path}/proper/media_wikidata_id__media_with_image.json"))
    data2 = [
        v for v in data.values() if len(v['review'].get('scores', [])) >= 3
    ]
    def fitness(item):
        return item['review'].get("mean_score", 0)
    def compare(item1, item2):
        if fitness(item1) < fitness(item2):
            return -1
        elif fitness(item1) > fitness(item2):
            return 1
        else:
            return 0
    data2 = sorted(data2, key=functools.cmp_to_key(compare))
    data2.reverse()
    results = data2[0:1000]
    for x in results:
        try:
            url = list(x['imdb_url'].keys())[0]
        except:
            url = list(x['omdb_url'].keys())[0]
        # logging.info(f"{int(x['review']['mean_score']*100)} | {x['label']['en']} | {url}")
    # logging.info(json.dumps(, indent=2))


def top_director():
    data = json.loads(read(f"{base_data_path}/proper/directors.json"))
    data2 = [
        v for v in data.values() if v.get('score_count') and v.get('score_count') >= 30
    ]
    def fitness(item):
        return item.get('score_mean', 0)
    def compare(item1, item2):
        if fitness(item1) < fitness(item2):
            return -1
        elif fitness(item1) > fitness(item2):
            return 1
        else:
            return 0
    data2 = sorted(data2, key=functools.cmp_to_key(compare))
    data2.reverse()
    results = data2[0:100]
    for x in results:
        try:
            url = x['wikidata_url']
        except:
            url = ""
        try:
            label = x['label']['en']
        except:
            label = ""
        logging.info(f"{int(x['score_mean']*100)} | {label} | {url}")
        # logging.info(f"{x}")


# transform_omdb_data()
# omdb_id__omdb_image_id__omdb_image_version()
# omdb_id__omdb_image_id()
# find_by_label("ghost in the shell")
# find_by_label_2("ghost in the shell")
# transform_omdb_data_2()
# transform_omdb_data_3()


# pull_data_labels()
# pull_data_relations()
build_mappings_v2()


# wikidata_id__omdb_id()
# wikidata_label__omdb_image_id__omdb_image_version() -- drepecated
# wikidata_label__wikidata_id() -- deprecated
# wikidata_id__language__label()
# wikidata_id__genre()
# wikidata_id__review()
# wikidata_id__imdb_id()
# wmedia_id__wdirector_id()
# media_wikidata_id__media_with_image()
director__language__label()
directors()
# top_media()
top_director()
