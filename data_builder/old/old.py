import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("start")
import requests
from .misc import (
    pull_data,
    convert_data,
    build_mappings,
    endpoint_url,
)
import os

from .builder import common


import urllib
from .builder import (
    film_cast_member, 
    film_label,
    film_director,
    film_publication,
    occupation,
    film_cast_member_2,
    film_cast_member_3,
    film_cast_member_4,
    film_image,
    film_imdb,
    film_omdb,
    film_screenwriter,
    film_voice_actor,
    voice_actor_label,
    screenwriter_label,
    cast_member_label,
    director_label,
    actor_label,
    film_composer,
    composer_label,
    film_main_subject,
    main_subject_label,
    film_genre,
    genre_label,
    television_series_label,
)
data_builders = (
    # actor_label,
    # film_label,
    # film_cast_member,
    # film_director,
    # film_publication,
    # film_image,
    # film_imdb,
    # film_omdb,
    # film_screenwriter,
    # film_voice_actor,
    # voice_actor_label,
    # director_label,
    # screenwriter_label,
    # film_composer,
    # composer_label,
    # film_main_subject,
    # main_subject_label,
    # film_genre,
    # genre_label,
    television_series_label,
)
# pull_data(data_builders)
# convert_data(data_builders)
# build_mappings(data_builders)
pull_data_v2()


def run(query):
    data = None
    for i in range(len(query['select'])-1):
        a = list(query['select'])[i]
        b = list(query['select'])[1:][i]
        logging.info(f"{a}__{b}")
        json_ = json.loads(read(f"{base_data_path}/proper/{a}__{b}.json"))
        for k, v in query['where'].items():
            if k == a:
                for k2, v2 in v.items():
                    if k2 == "like":
                        json_ = {
                            k3: v3 for k3, v3 in json_.items() if v2.lower() in k3.lower()
                        }
            # logging.info(json_)
            elif k == b:
                for k2, v2 in v.items():
                    if k2 == "like":
                        json_ = {
                            k3: {
                                k4: v4 for k4, v4 in v3.items() if v2.lower() in k4.lower()
                            } for k3, v3 in json_.items()
                        }
            # else:
            #     pass
        if i == 0:
            data = json_
        elif i == 1:
            for k, v in data.items():
                for k2 in v:
                    data[k][k2] = json_.get(k2, {})
        elif i == 2:
            for k, v in data.items():
                for k2, v2 in v.items():
                    for k3 in v2:
                        data[k][k2][k3] = json_.get(k3, {})
    logging.info(json.dumps(data, indent=4))



# run({
#     "select": [
#         "wikidata_label",
#         "wikidata_id",
#         "omdb_id",
#         "omdb_image_id",
#     ],
#     "where" : {
#         "wikidata_label": {
#             "like": "ghost in the shel"
#         },
#         # "omdb_id": {
#         #     "like": "31711"
#         # }
#     }
# })
