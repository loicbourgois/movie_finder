import os
import random

import pandas
from imdb import Cinemagoer

HOME = os.environ["HOME"]


def file_exists(path):
    return os.path.exists(path)


def pull_imdb_descriptions():
    ia = Cinemagoer()
    df_in = pandas.read_csv(f"{HOME}/github.com/loicbourgois/movie_finder_local/data_v3/database/item___imdb_id.csv")
    data = df_in.to_dict(orient="records")
    path_out = f"{HOME}/github.com/loicbourgois/movie_finder_local/data_v3/database/imdb_id___description.csv"
    for _ in range(1000):
        random.shuffle(data)
        if file_exists(path_out):
            df_out = pandas.read_csv(path_out)
        else:
            df_out = pandas.DataFrame(columns={
                "imdb_id": str,
                "plot_idx": int,
                "plot": str,
                "plot_author": str,
            })
        c1 = df_in["imdb_id"].nunique()
        c2 = df_out["imdb_id"].nunique()
        print(f"item___imdb_id:        { c1}")
        print(f"imdb_id___description: { c2}")
        print(f"progress:              { round(c2/c1*100,2)}%")
        data_todo = data[0:10]
        l = len(data_todo)
        for i, x in enumerate(data_todo):
            if df_out["imdb_id"].str.contains(x["imdb_id"]).any():
                print(f"{i+1}/{l} - SKIP")
            else:
                print(f"{i+1}/{l} - PULL")
                try:
                    movie = ia.get_movie(x["imdb_id"].replace("tt", ""), info=["plot"])
                    for plot_idx, plot_str in enumerate(movie.get("plot", [])):
                        parts = plot_str.split("—")
                        if len(parts) == 2:
                            plot = parts[0]
                            plot_author = parts[1]
                        else:
                            plot = plot_str
                            plot_author = None
                        df_out = pandas.concat([df_out, pandas.DataFrame([{
                            "imdb_id": x["imdb_id"],
                            "plot_idx": plot_idx,
                            "plot": plot,
                            "plot_author": plot_author,
                        }])], ignore_index=True)
                except Exception as e:
                    print(f"ERROR: {e}")
        print(df_out)
        df_out.to_csv(path_out, index=False)
