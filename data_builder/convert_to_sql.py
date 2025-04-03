import os
from functools import cmp_to_key
import pandas
from .shared import write_force, aligned_advancement, read
from .logger import get_logger
logger = get_logger('data_builder')


def create_parent_folder(path):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)


def column_type(ck):
    return {
        "date_of_birth": "date",
        "publication_date": "date",
        "attendance": "numeric",
        "duration": "numeric",
        "box_office": "numeric",
        "capital_cost": "numeric",
        "omdb_id": "numeric",
        "review_score": "review_score",
        "imdb_id": "string",
    }.get(ck, 'qid')


def column_type_sql(ck, kind="wikidata"):
    return {
        "wikidata": {
            "date_of_birth": "date",
            "publication_date": "date",
            "attendance": "float",
            "duration": "float",
            "box_office": "float",
            "capital_cost": "float",
            "omdb_id": "float",
            "review_score": "float",
            "imdb_id": "text",
        },
        "omdb": {
            "image_id": "int",
            "object_id": "int",
            "object_type": "text",
            "image_version": "int",
            "source": "text",
            "key": "text",
            "language_iso_639_1": "text",
            "name": "text",
            "type": "text",
            "vote_average": "float",
            "date": "date",
        },
    }[kind].get(ck, 'int')


def nullability_sql(ck, kind):
    return {
        "omdb": {
            "image_id": "not null",
            "object_id": "",
            "object_type": "",
            "image_version": "",
            "type": "",
            "parent_id": "",
            "date": "",
        },
    }[kind].get(ck, "not null")


def column_name(ck):
    return {
        "date_of_birth": "date_of_birth",
        "publication_date": "publication_date",
        "attendance": "attendance",
        "duration": "duration",
        "box_office": "box_office",
        "capital_cost": "capital_cost",
        "omdb_id": "omdb_id",
        "review_score": "review_score",
        "imdb_id": "imdb_id",
    }.get(ck, f"{ck}_id")


def get_df_label(path=None, k=None):
    df = pandas.read_csv(path)
    df.rename(columns={
        k: "item_id",
        f"{k}_label": "label",
        "lang": "language"
    }, inplace=True)
    col = "item_id"
    df = df[df[col].str.contains('http://www.wikidata.org/entity/Q')]
    df[col] = df[col].str.replace("http://www.wikidata.org/entity/Q", '')
    df = df.astype({col: int})
    return df


def transform_review_score(row):
    try:
        str_ = row['review_score'].replace(",", ".")
        split_1 = str_.split("/")
        if str_.endswith("%"):
            row['review_score'] = float(str_.replace("%", "")) / 100.0
        elif len(split_1) == 2:
            row['review_score'] = float(split_1[0]) / float(split_1[1])
        else:
            s = float(str_)
            if s > 10:
                row['review_score'] = s / 100
            else:
                row['review_score'] = s / 10
    except Exception:
        logger.warn(f"could not transform review_score: {row['review_score']}")
        row['review_score'] = None
    return row


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
    df = df.dropna()
    for col in list(df.columns):
        if column_type(col) == "qid":
            df = df[df[col].str.contains('http://www.wikidata.org/entity/Q')]
            df[col] = df[col].str.replace("http://www.wikidata.org/entity/Q", '')
            df = df.astype({col: int})
        elif column_type(col) == "date":
            df[col] = pandas.to_datetime(df[col], format="%Y-%m-%dT%H:%M:%SZ", errors="coerce")
        elif column_type(col) == "int":
            df = df.astype({col: int})
        elif column_type(col) == "numeric":
            df = df.astype({col: str})
            df = df[~df[col].str.contains('http://www.wikidata.org/.well-known/genid') ]
            df[col] = pandas.to_numeric(df[col])
        elif column_type(col) == "string":
            df = df.astype({col: str})
        elif column_type(col) == "review_score":
            # df = df.astype({col: str})
            df = df.transform(transform_review_score, axis=1)
            df[col] = pandas.to_numeric(df[col])
        else:
            raise Exception("error in to_database")
    df = df.dropna()
    tables[table_name] = pandas.concat([tables[table_name], df])
    if column_type(column_name(k)) == "qid":
        df.rename(
            columns={
                "item_id": "type",
                column_name(k): "item_id",
            },
            inplace=True
        )
        df['type'] = k
        tables["item"] = pandas.concat([tables["item"], df])
    return tables


def add_kind(kinds, k, v):
    if column_type(column_name(k)) == "qid":
        kinds[k] = k
    for k2, v2 in v.items():
        add_kind(kinds, k2, v2)


def create_table(table_create_queries, k, v):
    table_create_queries[k] = {
        'name': f"item___{k}",
        'column': f"{k}_id",
        'column_type': column_type_sql(column_name(k)),
    }
    if column_type(column_name(k)) != "qid":
        table_create_queries[k]["column"] = k
    for k2, v2 in v.items():
        create_table(table_create_queries, k2, v2)


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


def convert_to_sql(config):
    logger.info("convert_to_sql - A")
    tables = {
        "item": pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', 'type': 'str'}.items()}),
        "item___label": pandas.DataFrame({c: pandas.Series(dtype=t) for c, t in {'item_id': 'int', 'language': 'str', 'label': 'str'}.items()}),
    }
    kinds = {}
    table_create_queries = {}
    logger.info("convert_to_sql - B")
    for k, v in config['data'].items():
        add_kind(kinds, k, v)
        create_table(table_create_queries, k, v)
    kinds_str = ",\n".join([  f"'{k}'" for k in kinds])
    create_tables = [
        f"""CREATE TABLE {v['name']} (
            item_id int not null,
            {v['column']} {v['column_type']} not null
        );"""
        for k, v in table_create_queries.items() if "-by-" not in v['name']
    ]
    logger.info("convert_to_sql - C")
    todos = []
    for k, v in config['data'].items():
        todos.append({
            'short_path': f'{k}',
            'table': 'item',
            'type': k,
            'level': 1,
        })
        for k2, v2 in v.items():
            if "-by-" in k2:
                # by only useful for labels with language
                logger.info(f"(skip) {k}/{k2}")
            else:
                todos.append({
                    'short_path': f'{k}/{k2}',
                    'k_parent': k,
                    'k': k2,
                    'level': 2,
                })
                for k3 in v2.keys():
                    if f"{k}/{k2}/{k3}" in config['custom']:
                        logger.info(f"(skip) {k}/{k2}/{k3}")
                    else:
                        todos.append({
                            'short_path': f'{k}/{k2}/{k3}',
                            'k_parent': k2,
                            'k': k3,
                            'level': 3,
                        })
    for l in config['languages']:
        for k, v in config['data'].items():
            todos.append({
                'short_path': f'{l}/{k}',
                'k': k,
                'level': 'label',
            })
            for k2, v2 in v.items():
                if f"{l}/{k}/{k2}" in config['custom']:
                    logger.info(f"(skip) {l}/{k}/{k2}")
                else:
                    if "-by-" in k2:
                        k2a = k2.split("-by-")[0]
                        k2b = k2.split("-by-")[1]
                        csv_file = config['bys'][k2b]['csv']
                        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{csv_file}.csv"
                        for with_wd in wikidata_ids_from_csv(path, csv_file):
                            todos.append({
                                'short_path': f"{l}/{k}/{k2a}/by/{k2b}/{with_wd}",
                                'k': k2a,
                                'level': 'label',
                            })
                    else:
                        todos.append({
                            'short_path': f"{l}/{k}/{k2}",
                            'k': k2,
                            'level': 'label',
                        })
                        for k3 in v2.keys():
                            todos.append({
                                'short_path': f"{l}/{k}/{k2}/{k3}",
                                'k': k3,
                                'level': 'label',
                            })
    for name in config['omdb'].keys():
        todos.append({
            'short_path': f"omdb/{name}",
            'level': 'omdb',
            'table': f"omdb___{name}",
        })

    for (i, x) in enumerate(todos):
        logger.info(f"(convert) {aligned_advancement(i,len(todos))} - {x['short_path']}")
        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{x['short_path']}.csv"
        if x['level'] == 1:
            df = pandas.read_csv(path)
            df['type'] = x['type']
            df.rename(columns={x['type']: "item_id"}, inplace=True)
            # start = datetime.now()
            df['item_id'] = df['item_id'].str.replace("http://www.wikidata.org/entity/Q", '')
            df = df.astype({'item_id': int})
            tables[x['table']] = pandas.concat([tables[x['table']], df])
        elif x['level'] in [2, 3]:
            tables = to_database(
                tables=tables,
                k=x['k'],
                k_parent=x['k_parent'],
                path=path,
            )
        elif x['level'] == "label":
            tables["item___label"] = pandas.concat([
                tables["item___label"],
                get_df_label(
                    path=path,
                    k=x['k'],
                )
            ])
        elif x['level'] == "omdb":
            df = pandas.read_csv(path, on_bad_lines='warn')
            for column_name in list(df.columns):
                df = df.astype({column_name: str})
                df[column_name] = df[column_name].str.replace("\\N", "")
            columns_list = [
                f"{column_name} {column_type_sql(column_name, 'omdb')} {nullability_sql(column_name, 'omdb')}"
                for column_name in list(df.columns)
            ]
            tables[x['table']] = df
            sep = ",\n"
            create_tables.append(
                f"""CREATE TABLE {x['table']} (
                    {sep.join(columns_list)}
                );"""
            )
        else:
            raise Exception(f"error: invalid level: {x['level']}")
    logger.info("convert_to_sql - E")
    for i, (k, v) in enumerate(tables.items()):
        logger.info(f"{i+1}/{len(tables)} - {k}")
        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/database/{k}.csv"
        create_parent_folder(path)
        v.drop_duplicates(inplace=True)
        v = v.dropna()
        logger.info(f"  {v.shape}")
        v.to_csv(path, index=False)
    logger.info("convert_to_sql - F")
    import_csv_str = "\n".join(
        [
            f'''    -c "\\copy {table_name} FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/{table_name}.csv' CSV HEADER;" \\'''
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
            create_table_str="\n".join(create_tables),
            kinds_str=kinds_str,
        )
    )
    logger.info("convert_to_sql - done")
