import json


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
        "country_of_citizenship": "wdt:P27",
        "sex_or_gender": "wdt:P21",
        "gender_identity": "wdt:P21",
        "distributed_by": "wdt:P750",
        "inspired_by": "wdt:P941",
        "set_in_period": "wdt:P2408",
        "narrative_location": "wdt:P840",
        "filming_location": "wdt:P915",
        "duration": "wdt:P2047",
        "award_received": "wdt:P166",
        "nominated_for": "wdt:P1411",
        "box_office": "wdt:P2142",
        "capital_cost": "wdt:P2130",
        "characters": "wdt:P674",
        "depicts": "wdt:P180",
        "imdb_id": "wdt:P345",
        "omdb_id": "wdt:P3302",
        "creator": "wdt:P170",
        "film_editor": "wdt:P1040",
        "review_score": "wdt:P444",
        "attendance": "wdt:P1110",
    }
    wikidata_items = {
        "documentary": "wd:Q4164344",
        "film": "wd:Q11424",
        "television_series": "wd:Q5398426",
        "anime": "wd:Q1107",
        "film_series": "wd:Q24856",
        "western_animation": "wd:Q83646243",
        "animated_television_series": "wd:Q117467246",
        "country": "wd:Q6256",
        "gender_identity": "wd:Q48264",
        "country_of_citizenship": "wd:Q6256",
        "gender": "wd:Q48277",
        # "painter": {
        #     "relation": "P106", # occupation
        #     "item": "Q1028181", # painter
        # },
        "professional_painter": {
            "predicate": "wdt:P101",    # field of work
            "object": "wd:Q11629",      # art of painting
        },
        "professional_artist": {
            "predicate": "wdt:P101",
            "object": "wd:Q56055944", # type of arts
        },
        "professional_actor": {
            "predicate": "wdt:P101",
            "object": "wd:Q222749", # acting
        },
    }
    media_person = {
        "gender": {},
        "date_of_birth": {},
        "occupation": {},
        "nominated_for": {},
        "award_received": {},
        "genre": {},
    }
    media = {
        "director": json.loads(json.dumps(media_person)),
        "producer": json.loads(json.dumps(media_person)),
        "creator": json.loads(json.dumps(media_person)),
        "screen_writer": json.loads(json.dumps(media_person)),
        "publication_date": {},
        "cast_member": json.loads(json.dumps(media_person)),
        "imdb_id": {},
        "narrator": json.loads(json.dumps(media_person)),
        "award_received": {},
        "genre": {},
        "characters": json.loads(json.dumps(media_person)),
        "main_subject": {},
        "original_language": {},
        "composer": json.loads(json.dumps(media_person)),
        "film_editor": json.loads(json.dumps(media_person)),
        "inspired_by": {},
        "depicts": {},
        "nominated_for": {},
        "attendance": {},
        "duration": {},
        "omdb_id": {},
        "box_office": {},
        "capital_cost": {},
        "review_score": {},
    }
    data = {
        # "documentary": json.loads(json.dumps(media)),
        # "film_series": json.loads(json.dumps(media)),
        # "western_animation": json.loads(json.dumps(media)),
        # "anime": json.loads(json.dumps(media)),
        "animated_television_series": json.loads(json.dumps(media)),
        "television_series": json.loads(json.dumps(media)),
        "film": json.loads(json.dumps(media)),
        # "country": {},
        # "gender": {},
        # "professional_painter": json.loads(json.dumps(media_person)),
        # "professional_artist": json.loads(json.dumps(media_person)),
        # "professional_actor": json.loads(json.dumps(media_person)),
    }
    # data['film']['cast_member-by-gender'] = {}
    bys = {
        # "country_of_citizenship": {
        #     "csv": "country",
        # },
        "gender": {
            "csv": "gender",
        }
    }
    languages = {
        "en": {},
        # "fr": {},
        # "ja": {},
    }
    return {
        "data": data,
        "languages": languages,
        "wikidata_fields": wikidata_fields,
        "wikidata_items": wikidata_items,
        "bys": bys,
        "custom": {
            "en/film/cast_member": {}, # too big to pull
            "ja/film/cast_member": {}, # too big to pull
            "film/cast_member/nominated_for": {},
        },
        "omdb": {
            "movie_links": {},
            "image_ids": {},
            "movie_references": {},
            "category_names": {},
            "movie_categories": {},
            "all_categories": {},
            "all_votes": {},
        },
    }
