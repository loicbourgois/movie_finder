import csv
import json
import os
import pandas
from .logger import get_logger
from .shared import read, path_local, aligned_advancement
logger = get_logger("data_builder")


def create_parent_folder(path):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)


def write_force_csv(path, rows):
    create_parent_folder(path)
    with open(path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def convert_to_csv(config, queries):
    remaining_queries = {}
    for i, (k, v) in enumerate(queries.items()):
        path = "/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/"+k+".csv"
        try:
            pandas.read_csv(path)
            logger.info(f"(skip) {aligned_advancement(i,len(queries))} - {path_local(path)}")
        except Exception:
            logger.info(f"(todo) {aligned_advancement(i,len(queries))} - {path_local(path)}")
            remaining_queries[k] = v
    for i, (k, v) in enumerate(remaining_queries.items()):
        path_out = "/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/"+k+".csv"
        if k in config['custom']:
            logger.info(f"(skip) {aligned_advancement(i,len(remaining_queries))} - {path_local(path_out)}")
        else:
            try:
                d = json.loads(read("/root/github.com/loicbourgois/movie_finder_local/data_v3/json/"+k+".json"))
                rows = [ d['head']['vars'] ]
                for x in d['results']['bindings']:
                    rows.append( [
                        x[column_id]['value']
                        for column_id in rows[0]
                    ] )
                write_force_csv(path_out, rows)
                logger.info(f"( ok ) {aligned_advancement(i,len(remaining_queries))} - {path_local(path_out)}")
            except:
                logger.info(f"(fail) {aligned_advancement(i,len(remaining_queries))} - {path_local(path_out)}")
