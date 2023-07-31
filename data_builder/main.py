import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("start")
from .misc import (
    pull_data,
    convert_data,
    build_mappings,
)
import urllib
from .builder import (
    # human_activity,; action,; activity,; professions,; social_status,
    cat,
    film_cast_member, 
    film_label,
    film_label_2,
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
    film_label,
    film_cast_member,
    film_director,
    film_publication,
    film_image,
    film_imdb,
    film_omdb,
    film_screenwriter,
    film_voice_actor,
    voice_actor_label,
    screenwriter_label,
    cast_member_label,
    actor_label,
    director_label,
    film_label_old,
    film_cast_member_2,
    film_cast_member_3,
    film_cast_member_4,
    human_activity,
    action,
    activity,
    occupation,
    cat,
    professions,
    social_status,
    film_composer,
    composer_label,
    film_main_subject,
    main_subject_label,
    film_genre,
    genre_label,
)
pull_data(data_builders)
# convert_data(data_builders)
# build_mappings(data_builders)
