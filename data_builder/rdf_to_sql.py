import os
import logging
import json
import urllib
import requests
import csv
import pandas
import time
from datetime import datetime
from functools import cmp_to_key
from .config import get_config
from .query import (
    query_0,
    query_1,
    query_2,
    q0l,
    q1l,
    q2l,
    query_by,
)


def read(path):
    with open(path, "r") as file:
        return file.read()


def with_qx(x):
    return """
        with {{
            {query_x}
        }} as %qx
    """.replace("x", f"{x}")


def wikidata_ids_from_csv(path, csv_file):
    df = pandas.read_csv(path)
    data = df.to_dict(orient="records")
    data = [
        x[csv_file].replace('http://www.wikidata.org/entity/', '')
        for x in data
    ]
    def cmp_(a,b):
        return len(a) - len(b)
    cmp_key = cmp_to_key(cmp_)
    data.sort(key=cmp_key)
    return data


def write_force(path, content):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, 'w') as f:
        f.write(content)


def add_query(path, q):
    assert queries.get(path) is None
    queries[path] = q
    path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/query/{path}.sparql"
    # logging.info(path.replace("/root", "$HOME"))
    write_force(
        path, 
        q,
    )


def replace_root(str_):
    return str_.replace("/root/", "$HOME/")


def query_to_file(path, query):
    time.sleep( shared['sleep_time'] )
    start = time.time()
    args = urllib.parse.urlencode({
        'query': query,
        'format': 'json'
    })
    r = requests.get(f"{endpoint_url}?{args}", timeout=3600)
    logging.info(f"  {r.status_code} | {replace_root(path)}")
    write_force(path, r.text)
    end = time.time()
    shared['sleep_time'] = max(0, 3 - (end - start))


def pull_data():
    remaining_queries = {}
    for i, (k, v) in enumerate(queries.items()):
        path_json = "/root/github.com/loicbourgois/movie_finder_local/data_v3/json/" + k + ".json"
        try:
            c = json.loads(read(path_json))
            logging.info(f"(skip) {i+1}/{len(queries)} - {path_json.replace('/root', '$HOME')} - {len(c['results']['bindings'])}")
        except Exception as e:
            logging.info(f"(todo) {i+1}/{len(queries)} - {k}")
            remaining_queries[k] = v
    for i, (k, v) in enumerate(remaining_queries.items()):
        logging.info(f"{i+1}/{len(remaining_queries)} - {k}")
        if k in config['custom']:
            logging.info("  skip")
        else:
            query_to_file("/root/github.com/loicbourgois/movie_finder_local/data_v3/json/" + k + ".json", v)


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
        try:
            pandas.read_csv("/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/"+k+".csv")
            logging.info(f"(skip) {i+1}/{len(queries)} - {k}")
        except Exception as e:
            logging.info(f"(todo) {i+1}/{len(queries)} - {k}")
            remaining_queries[k] = v
    for i, (k, v) in enumerate(remaining_queries.items()):
        if k in config['custom']:
            logging.info(f"(skip) {i+1}/{len(remaining_queries)} - {k}")
        else:
            try:
                d = json.loads(read("/root/github.com/loicbourgois/movie_finder_local/data_v3/json/"+k+".json"))
                rows = [ d['head']['vars'] ]
                for x in d['results']['bindings']:
                    rows.append( [
                        x[column_id]['value']
                        for column_id in rows[0]
                    ] )
                write_force_csv("/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/"+k+".csv", rows)
                logging.info(f"( ok ) {i+1}/{len(remaining_queries)} - {k}")
            except:
                logging.info(f"(fail) {i+1}/{len(remaining_queries)} - {k}")


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
                    # logging.info(f"error: {k4}: {row[k4]}")
                    row[k4] = None
            elif column_type(k4) == "date":
                try:
                    row[k4] = datetime.strptime(row[k4], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                    assert len(row[k4]) == 10
                except Exception as e:
                    logging.error(row[k4])
                    logging.error(e)
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
    logging.info("convert_to_sql - A")
    tables = {
        "item": pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', 'type': 'str'}.items()}),
        "item___label": pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', 'language': 'str', 'label': 'str'}.items()}),
    }
    kinds = {}
    table_create_queries = {}

    logging.info("convert_to_sql - B")
    for k, v in config['data'].items():
        add_kind(kinds, k, v)
        create_table(table_create_queries, k, v)
    kinds_str = ",\n".join([  f"'{k}'" for k in kinds])
    create_table_str = "\n".join([  
        f"""CREATE TABLE {v['name']} (
            item_id int not null,
            {v['column']} {v['column_type']} not null
        );"""
        for k, v in table_create_queries.items() if "-by-" not in v['name']
    ])
    logging.info(kinds_str)
    logging.info(create_table_str)

    logging.info("convert_to_sql - C")
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
            if "-by-" in k2:
                pass # by only useful for labels with language
            else:
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

    logging.info("convert_to_sql - D")
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
                if f"{l}/{k}/{k2}" in config['custom']:
                    logging.info(f"(skip) {l}/{k}/{k2}")
                else:
                    logging.info(f"( ok ) {l}/{k}/{k2}")
                    if "-by-" in k2:
                        k2a = k2.split("-by-")[0]
                        k2b = k2.split("-by-")[1]
                        csv_file = config['bys'][k2b]['csv']
                        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{csv_file}.csv"
                        for with_wd in wikidata_ids_from_csv(path, csv_file):
                            uu = f"{l}/{k}/{k2a}/by/{k2b}/{with_wd}"
                            logging.info(uu)
                            tables["item___label"] = pandas.concat([
                                tables["item___label"],
                                get_df_label(
                                    path=f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{uu}.csv",
                                    k=k2a,
                                )
                            ])
                    else:
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

    logging.info("convert_to_sql - E")
    for i, (k, v) in enumerate(tables.items()):
        logging.info(f"{i+1}/{len(tables)} - {k}")
        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/database/{k}.csv"
        create_parent_folder(path)
        v.drop_duplicates(inplace=True)
        v.to_csv(path, index=False)

    logging.info("convert_to_sql - F")
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


logging.basicConfig(level=logging.INFO)
logging.info("start")
endpoint_url = "https://query.wikidata.org/sparql"
instance_of_any_subclass_of = "wdt:P31/wdt:P279*"
config = get_config()
queries = {}


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
            if "-by-" in field_k:
                field_ka = field_k.split("-by-")[0]
                field_kb = field_k.split("-by-")[1]
                item_wdt = config['wikidata_fields'][field_ka]
                with_wdt = config['wikidata_fields'][field_kb]
                qk = f"{lang}/{item_k}/{field_ka}/by/{field_kb}"
                csv_file = config['bys'][field_kb]['csv']
                path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{csv_file}.csv"
                for with_wd in wikidata_ids_from_csv(path, csv_file):
                    add_query(
                        f"{qk}/{with_wd}",
                        query_by.format(
                            parent=item_k,
                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                            parent_wd=item_v,
                            item_wdt=item_wdt,
                            item=field_ka,
                            with_wdt=with_wdt,
                            with_wd=with_wd,
                            lang=lang,
                        ),
                    )
            else:
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
        if "-by-" in field_k:
            # -by- is only useful for labels so far
            pass
        else:
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


pull_data()
convert_to_csv()
# convert_to_sql()
