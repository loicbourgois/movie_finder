import pandas

from .convert_to_sql import (
    column_type,
    column_type_sql,
    get_column_name,
    nullability_sql,
)
from .shared import read, write_force


def add_kind(kinds, k, v):
    if column_type(get_column_name(k)) == "qid":
        kinds[k] = k
    for k2, v2 in v.items():
        add_kind(kinds, k2, v2)


def create_table(table_create_queries, k, v, level=1):
    if level>=1:
        column_type_ = column_type(get_column_name(k))
        if column_type_ != "qid":
            column = k
        else:
            column = f"{k}_id"
        table_create_queries[k] = {
            'name': f"item___{k}",
            'column': column,
            'column_type': column_type_sql(get_column_name(k)),
            'level': level,
        }
    for k2, v2 in v.items():
        create_table(table_create_queries, k2, v2, level+1)


def generate_database_config(config):
    table_create_queries = {}
    for k, v in config['data'].items():
        create_table(table_create_queries, k, v)
    create_tables = [
        f"""CREATE TABLE {v['name']} (
            item_id int not null,
            {v['column']} {v['column_type']} not null
        );"""
        for k, v in table_create_queries.items() if "-by-" not in v['name']
    ]
    table_names = {
        v['name']:v['name']
        for k, v in table_create_queries.items() if v['level'] > 1
    }
    table_names['item'] = 'item'
    table_names['item___label'] = 'item___label'
    kinds = {}
    for k, v in config['data'].items():
        add_kind(kinds, k, v)
    kinds_str = ",\n".join([  f"'{k}'" for k in kinds])
    for name in config['omdb'].keys():
        x = {
            'short_path': f"omdb/{name}",
            'level': 'omdb',
            'table': f"omdb___{name}",
        }
        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{x['short_path']}.csv"
        df = pandas.read_csv(path, on_bad_lines='warn')
        for column_name in list(df.columns):
            df = df.astype({column_name: str})
            df[column_name] = df[column_name].str.replace("\\N", "")
        columns_list = [
            f"    {column_name} {column_type_sql(column_name, 'omdb')} {nullability_sql(column_name, 'omdb')}"
            for column_name in list(df.columns)
        ]
        sep = ",\n"
        create_tables.append(
            f"""CREATE TABLE {x['table']} (
    {sep.join(columns_list)}
) ;"""
        )
        table_names[x['table']] = x['table']
    write_force(
        "/root/github.com/loicbourgois/movie_finder/database/go_inner.sh",
        read("/root/github.com/loicbourgois/movie_finder/database/go_inner.template.sh").format(
            IMPORT_CSV="\n".join(
                [
                    f'''    -c "\\copy {table_name} FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/{table_name}.csv' CSV HEADER;" \\'''
                    for table_name in table_names
                ]
            )
        )
    )
    write_force(
        "/root/github.com/loicbourgois/movie_finder/database/init_1.sql",
        read("/root/github.com/loicbourgois/movie_finder/database/init_1.template.sql").format(
            create_table_str="\n".join(create_tables),
            kinds_str=kinds_str,
        )
    )
