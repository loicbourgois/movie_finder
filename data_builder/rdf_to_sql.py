import os
import logging
import json
import urllib
import requests
import csv
import pandas
import time
from datetime import datetime
logging.basicConfig(level=logging.INFO)
logging.info("start")
def read(path):
    with open(path, "r") as file:
        return file.read()


endpoint_url = "https://query.wikidata.org/sparql"
instance_of_any_subclass_of = "wdt:P31/wdt:P279*"
subclass_of_any_subclass_of = "wdt:P279/wdt:P279"


def get_config():
    wikidata_fields = {
        "director": "wdt:P57",
        "producer": "wdt:P162",
        "main_subject": "wdt:P921",
        "genre": "wdt:P136",
        "original_language": "wdt:P364", # of_film_or_TV_show
        "date_of_birth": "wdt:P569",
        "gender": "wdt:P21",
        "publication_date": "wdt:P577",
        "screen_writer": "wdt:P58",
        "cast_member": "wdt:P161",
        "occupation": "wdt:P106",
        "composer": "wdt:P86",
        "narrator": "wdt:P2438",
        "production_company": "wdt:P272",
        "distributed_by": "wdt:P750",
        "inspired_by": "wdt:P941",
        "set_in_period": "wdt:P2408",
        "narrative_location": "wdt:P840",
        "filming_location": "wdt:P915",
        "duration": "wdt:P2047",
        "review_score": "wdt:P444",
        "award_received": "wdt:P166",
        "nominated_for": "wdt:P1411",
        "box_office": "wdt:P2142",
        "cost": "wdt:P2130",
        "characters": "wdt:P674",
        "depicts": "wdt:P180",
        "imdb_id": "wdt:P345",
        "omdb_id": "wdt:P3302",
        "creator": "wdt:P170",
    }
    wikidata_items = {
        "documentary": "wd:Q4164344",
        "film": "wd:Q11424",
        "television_series": "wd:Q5398426",
        "anime": "wd:Q1107",
        "film_series": "wd:Q24856",
        "western_animation": "wd:Q83646243",
        "animated_television_series": "wd:Q117467246",
    }
    media_person = {
        "gender": {},
        "date_of_birth": {},
        "occupation": {},
    }
    media = {
        "director": media_person,
        "producer": media_person,
        "creator": media_person,
        "screen_writer": media_person,
        "publication_date": {},
        # "cast_member": media_person,
        # "omdb_id": {},
        # "imdb_id": {},
        # "narrator": media_person,
        "award_received": {},
        # "characters": media_person,
    }
    data = {
        "documentary": media,
        "film_series": media,
        "western_animation": media,
        "anime": media,
        "animated_television_series": media,
        # "television_series": media,
        # "film": media,
    }
    languages = {
        "en": {},
        "fr": {},
    }
    return {
        "data": data,
        "languages": languages,
        "wikidata_fields": wikidata_fields,
        "wikidata_items": wikidata_items,
        "custom": {
            "en/film/cast_member": {},
            "fr/film/cast_member": {},
            "fr/television_series/cast_member": {},
        }
    }
config = get_config()


def with_qx(x):
    return """
        with {{
            {query_x}
        }} as %qx
    """.replace("x", f"{x}")


query_0 = """
SELECT distinct ?{item_k}
WHERE {{
    ?{item_k} {instance_of_any_subclass_of} {item_v} .
}}
"""
query_1 = """# {item_k} -.-> {field_k}
SELECT distinct ?{item_k} ?{field_k}
{with_q0}
WHERE {{
    include %q0
    ?{item_k} {field_v} ?{field_k} .
}}
"""
query_2 = """# {item_k}__{field_k} -.-> {sub_field_k}
select distinct ?{field_k} ?{sub_field_k}
{with_q0}
{with_q1}
where {{
    include %q1
    ?{field_k} {sub_field_v} ?{sub_field_k} .
}}
"""

q0l = """
SELECT ?{item_k} ?{item_k}_label (lang(?{item_k}_label) as ?lang)
{with_q0}
WHERE {{
    include %q0
    ?{item_k} rdfs:label ?{item_k}_label filter (lang(?{item_k}_label) = "{lang}").
}}
"""
q1l = """
SELECT ?{field_k} ?{field_k}_label (lang(?{field_k}_label) as ?lang)
{with_q0}
{with_q1}
with {{
    SELECT distinct ?{field_k}
    WHERE {{
        include %q1
    }}
}} as %q
WHERE {{
    include %q
    ?{field_k} rdfs:label ?{field_k}_label filter (lang(?{field_k}_label) = "{lang}").
}}
"""
q2l = """
SELECT ?{sub_field_k} ?{sub_field_k}_label (lang(?{sub_field_k}_label) as ?lang)
{with_q0}
{with_q1}
{with_q2}
with {{
    SELECT distinct ?{sub_field_k}
    WHERE {{
        include %q2
    }}
}} as %q
WHERE {{
    include %q
    ?{sub_field_k} rdfs:label ?{sub_field_k}_label filter (lang(?{sub_field_k}_label) = "{lang}").
}}
"""


def write_force(path, content):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, 'w') as f:
        f.write(content)
lines = ""

queries = {}


def add_query(path, q):
    assert queries.get(path) is None
    queries[path] = q


for lang in config['languages']:
    for item_k, v in config['data'].items():
        item_v = config['wikidata_items'][item_k]
        add_query(
            f"{lang}/{item_k}",
            q0l.format(
                item_k=item_k,
                lang=lang,
                with_q0=with_qx(0).format(
                    query_0=query_0.format(
                        item_k=item_k,
                        item_v=item_v,
                        instance_of_any_subclass_of=instance_of_any_subclass_of,
                    ),
                ),
            )
        )
        for field_k, subfields in v.items():
            field_v = config['wikidata_fields'][field_k]
            add_query(
                f"{lang}/{item_k}/{field_k}",
                q1l.format(
                    field_k=field_k,
                    lang=lang,
                    with_q0=with_qx(0).format(
                        query_0=query_0.format(
                            item_k=item_k,
                            item_v=item_v,
                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                        ),
                    ),
                    with_q1=with_qx(1).format(
                        query_1=query_1.format(
                            item_k=item_k,
                            item_v=item_v,
                            field_k=field_k,
                            field_v=field_v,
                            with_q0="",
                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                        ),
                    ),
                )
            )
            for sub_field_k in subfields:
                sub_field_v = config['wikidata_fields'][sub_field_k]
                add_query(
                    f"{lang}/{item_k}/{field_k}/{sub_field_k}",
                    q2l.format(
                        sub_field_k=sub_field_k,
                        lang=lang,
                        with_q0=with_qx(0).format(
                            query_0=query_0.format(
                                item_k=item_k,
                                item_v=item_v,
                                instance_of_any_subclass_of=instance_of_any_subclass_of,
                            ),
                        ),
                        with_q1=with_qx(1).format(
                            query_1=query_1.format(
                                item_k=item_k,
                                item_v=item_v,
                                field_k=field_k,
                                field_v=field_v,
                                with_q0="",
                                instance_of_any_subclass_of=instance_of_any_subclass_of,
                            ),
                        ),
                        with_q2=with_qx(2).format(
                            query_2=query_2.format(
                                item_k=item_k,
                                item_v=item_v,
                                field_k=field_k,
                                field_v=field_v,
                                sub_field_k=sub_field_k,
                                sub_field_v=sub_field_v,
                                with_q0="",
                                with_q1="",
                                instance_of_any_subclass_of=instance_of_any_subclass_of,
                            ),
                        ),
                    )
                )
for item_k, v in config['data'].items():
    item_v = config['wikidata_items'][item_k]
    add_query(
        f"{item_k}",
        query_0.format(
            item_k=item_k,
            item_v=item_v,
            instance_of_any_subclass_of=instance_of_any_subclass_of,
        )
    )
    for field_k, subfields in v.items():
        field_v = config['wikidata_fields'][field_k]
        add_query(
            f"{item_k}/{field_k}",
            query_1.format(
                item_k=item_k,
                item_v=item_v,
                field_k=field_k,
                field_v=field_v,
                with_q0=with_qx(0).format(
                    query_0=query_0.format(
                        item_k=item_k,
                        item_v=item_v,
                        instance_of_any_subclass_of=instance_of_any_subclass_of,
                    ),
                ),
                instance_of_any_subclass_of=instance_of_any_subclass_of,
            )
        )
        for sub_field_k in subfields:
            sub_field_v = config['wikidata_fields'][sub_field_k]
            add_query(
                f"{item_k}/{field_k}/{sub_field_k}",
                query_2.format(
                    item_k=item_k,
                    item_v=item_v,
                    with_q0=with_qx(0).format(
                        query_0=query_0.format(
                            item_k=item_k,
                            item_v=item_v,
                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                        ),
                    ),
                    with_q1=with_qx(1).format(
                        query_1=query_1.format(
                            item_k=item_k,
                            item_v=item_v,
                            field_k=field_k,
                            field_v=field_v,
                            with_q0="",
                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                        ),
                    ),
                    field_k=field_k,
                    field_v=field_v,
                    sub_field_k=sub_field_k,
                    sub_field_v=sub_field_v,
                    instance_of_any_subclass_of=instance_of_any_subclass_of,
                )
            )
write_force(
    "/root/github.com/loicbourgois/movie_finder_local/data_v3/rdf_to_sql.sparql", 
    "\n".join(
        [
            f"# {k}\n{v}" for k, v in queries.items()
        ]
    )
)
shared = {
    "sleep_time": 0,
}
def query_to_file(path, query):
    logging.info(f"sleep_time: {shared['sleep_time']}")
    time.sleep( shared['sleep_time'] )
    start = time.time()
    # logging.info(path)
    # logging.info(query)
    args = urllib.parse.urlencode({
        'query': query,
        'format': 'json'
    })
    r = requests.get(f"{endpoint_url}?{args}", timeout=3600)
    logging.info(f"CODE: {r.status_code}")
    write_force(path, r.text)
    end = time.time()
    shared['sleep_time'] = max(0, 3 - (end - start))


def pull_data():
    remaining_queries = {}
    for i, (k, v) in enumerate(queries.items()):
        logging.info(f"{i+1}/{len(queries)} - {k}")
        try:
            c = json.loads(read("/root/github.com/loicbourgois/movie_finder_local/data_v3/json/"+k+".json"))
            logging.info(f"  count: {len(c['results']['bindings'])}")
        except Exception as e:
            logging.error(f"  {e}")
            remaining_queries[k] = v
    for i, (k, v) in enumerate(remaining_queries.items()):
        logging.info(f"{i}/{len(remaining_queries)} - {k}")
        if k in config['custom']:
            logging.info("  skip")
        else:
            query_to_file("/root/github.com/loicbourgois/movie_finder_local/data_v3/json/"+k+".json", v)


def create_parent_folder(path):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)


def write_force_csv(path, rows):
    create_parent_folder(path)
    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def convert_to_csv():
    remaining_queries = {}
    for i, (k, v) in enumerate(queries.items()):
        logging.info(f"{i+1}/{len(queries)} - {k}")
        try:
            pandas.read_csv("/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/"+k+".csv")
        except Exception as e:
            logging.error(f"  {e}")
            remaining_queries[k] = v
    for i, (k, v) in enumerate(remaining_queries.items()):
        logging.info(f"{i}/{len(remaining_queries)} - {k}")
        if k in config['custom']:
            logging.info("  skip")
        else:
            d = json.loads(read("/root/github.com/loicbourgois/movie_finder_local/data_v3/json/"+k+".json"))
            rows = [ d['head']['vars'] ]
            for x in d['results']['bindings']:
                rows.append( [
                    x[column_id]['value']
                    for column_id in rows[0]
                ] )
            write_force_csv("/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/"+k+".csv", rows)


def column_type(ck):
    return {
        "date_of_birth": "date",
        "publication_date": "date",
    }.get(ck, 'uuid')
def column_name(ck):
    return {
        "date_of_birth": "date_of_birth",
        "publication_date": "publication_date",
    }.get(ck, f"{ck}_id")



def get_df_label(path=None, k=None):
    df = pandas.read_csv(path)
    df.rename(columns={
        k: "item_id",
        f"{k}_label": "label",
        "lang": "language"
    }, inplace=True)
    def transform(row):
        row['item_id'] = int(row['item_id'].replace("http://www.wikidata.org/entity/Q", ''))
        return row
    df = df.transform(transform, axis=1)
    return df


def to_database(
    tables=None,
    k=None,
    k_parent=None,
    path=None,
):
    table_name = f"item___{k}"
    if tables.get(table_name, pandas.DataFrame()).empty:
        tables[table_name] = pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', column_name(k): 'int'}.items()})
    df = pandas.read_csv(path)
    df.rename(
        columns={
            k_parent: "item_id",
            k: column_name(k),
        }, 
        inplace=True
    )
    def transform(row):
        for k4 in row.keys():
            if column_type(k4) == "uuid":
                if "http://www.wikidata.org/entity/Q" in row[k4]:
                    row[k4] = int(row[k4].replace("http://www.wikidata.org/entity/Q", ''))
                else:
                    logging.info(f"error: {k4}: {row[k4]}")
                    row[k4] = None
            elif column_type(k4) == "date":
                try:
                    row[k4] = datetime.strptime(row[k4], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                except Exception as e:
                    logging.info(e)
                    row[k4] = None
            else:
                raise "Bob"
        return row
    df = df.transform(transform, axis=1)
    df = df.dropna()
    tables[table_name] = pandas.concat([tables[table_name], df])
    if column_type(column_name(k)) == "uuid":
        df.rename(
            columns={
                "item_id": "type",
                column_name(k): f"item_id",
            }, 
            inplace=True
        )
        df['type'] = k
        tables["item"] = pandas.concat([tables["item"], df])
    return tables


def add_kind(kinds, k, v):
    if column_type(column_name(k)) == "uuid":
        kinds[k] = k
    for k2, v2 in v.items():
        add_kind(kinds, k2, v2)


def create_table(table_create_queries, k, v):
    table_create_queries[k] = {
        'name': f"item___{k}",
        'column': f"{k}_id",
        'column_type': "int",
    }
    if column_type(column_name(k)) != "uuid":
        table_create_queries[k]["column"] = k
        table_create_queries[k]["column_type"] = column_type(column_name(k))
    for k2, v2 in v.items():
        create_table(table_create_queries, k2, v2)


def convert_to_sql():
    tables = {
        "item": pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', 'type': 'str'}.items()}),
        "item___label": pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', 'language': 'str', 'label': 'str'}.items()}),
    }
    kinds = {}
    table_create_queries = {}
    for k, v in config['data'].items():
        add_kind(kinds, k, v)
        create_table(table_create_queries, k, v)
    kinds_str = ",\n".join([  f"'{k}'" for k in kinds])
    create_table_str = "\n".join([  
        f"""CREATE TABLE {v['name']} (
            item_id int not null,
            {v['column']} {v['column_type']} not null
        );"""
        for k, v in table_create_queries.items()
    ])
    logging.info(kinds_str)
    logging.info(create_table_str)
    for k, v in config['data'].items():
        logging.info(f"{k}")
        df = pandas.read_csv(f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{k}.csv")
        df['type'] = k
        df.rename(columns={k: "item_id"}, inplace=True)
        def transform(row):
            row['item_id'] = int(row['item_id'].replace("http://www.wikidata.org/entity/Q", ''))
            return row
        df = df.transform(transform, axis=1)
        tables["item"] = pandas.concat([tables["item"], df])
        for k2, v2 in v.items():
            logging.info(f"{k}/{k2}")
            tables = to_database(
                tables=tables,
                k=k2,
                k_parent=k,
                path=f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{k}/{k2}.csv",
            )
            for k3, v3 in v2.items():
                logging.info(f"{k}/{k2}/{k3}")
                tables = to_database(
                    tables=tables,
                    k=k3,
                    k_parent=k2,
                    path=f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{k}/{k2}/{k3}.csv",
                )
    for l in config['languages']:
        logging.info(f"{l}")
        for k, v in config['data'].items():
            logging.info(f"{l}/{k}")
            tables["item___label"] = pandas.concat([
                tables["item___label"],
                get_df_label(
                    path=f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{l}/{k}.csv",
                    k=k
                )
            ])
            for k2, v2 in v.items():
                logging.info(f"{l}/{k}/{k2}")
                tables["item___label"] = pandas.concat([
                    tables["item___label"],
                    get_df_label(
                        path=f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{l}/{k}/{k2}.csv",
                        k=k2
                    )
                ])
                for k3, v3 in v2.items():
                    logging.info(f"{l}/{k}/{k2}/{k3}")
                    tables["item___label"] = pandas.concat([
                        tables["item___label"],
                        get_df_label(
                            path=f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{l}/{k}/{k2}/{k3}.csv",
                            k=k3
                        )
                    ])
    for i, (k, v) in enumerate(tables.items()):
        logging.info(f"{i+1}/{len(tables)} - {k}")
        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/database/{k}.csv"
        create_parent_folder(path)
        v.drop_duplicates(inplace=True)
        v.to_csv(path, index=False)
    import_csv_str = "\n".join(
        [
            f'''    -c "\copy {table_name} FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/{table_name}.csv' CSV HEADER;" \\'''
            for table_name in tables
        ]
    )
    write_force(
        "/root/github.com/loicbourgois/movie_finder_local/data_v3/database/go_inner.sh",
        read("/root/github.com/loicbourgois/movie_finder/database/go_inner.template").format(IMPORT_CSV=import_csv_str)
    )
    write_force(
        "/root/github.com/loicbourgois/movie_finder_local/data_v3/database/init_1.sql",
        read("/root/github.com/loicbourgois/movie_finder/database/init_1.template").format(
            create_table_str=create_table_str,
            kinds_str=kinds_str,
        )
    )


# pull_data()
# convert_to_csv()
convert_to_sql()
