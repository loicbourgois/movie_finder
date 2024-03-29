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
)
pull_data(data_builders)
convert_data(data_builders)
build_mappings(data_builders)

