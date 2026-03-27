from .common import (
  with_occupation, 
  actor,
  limit, 
  film_actor,
  with_sex,
  sex_female,
  sex_male,
)
import os
multi = True
name = os.path.basename(__file__).replace('.py', '')
queries = [
    f'''
        SELECT ?actor ?actor_label
        WHERE {{
          ?actor {with_occupation} {actor} .
          ?actor {with_sex} {sex_male} .
          ?actor rdfs:label ?actor_label filter (lang(?actor_label) = "en") .
        }}
    ''',
    f'''
        SELECT ?actor ?actor_label
        WHERE {{
          ?actor {with_occupation} {actor} .
          ?actor {with_sex} {sex_female} .
          ?actor rdfs:label ?actor_label filter (lang(?actor_label) = "en") .
        }}
    ''',
    f'''
        SELECT ?actor ?actor_label
        WHERE {{
          ?actor {with_occupation} {actor} .
          ?actor {with_sex} ?sex .
          FILTER ( ?sex not in ( {sex_male}, {sex_female} ) )
          ?actor rdfs:label ?actor_label filter (lang(?actor_label) = "en") .
        }}
    ''',
    f'''
        SELECT ?actor ?actor_label
        WHERE {{
          {{
            ?actor {with_occupation} {film_actor} .
          }}
          ?actor rdfs:label ?actor_label filter (lang(?actor_label) = "en") .
        }}
        {limit}
    ''',
]
