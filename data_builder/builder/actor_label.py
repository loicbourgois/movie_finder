from .common import (
  with_occupation, 
  instance_of_any_subclass_of, 
  actor, 
  with_cast_member, 
  limit, 
  subclass_of,
  film_actor,
  subclass_of_any_subclass_of
)
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?actor ?actor_label
WHERE {{
  {{
    ?actor {with_occupation} {actor} .
  }}
  UNION
  {{
    ?actor {with_occupation} {film_actor} .
  }}
  ?actor rdfs:label ?actor_label filter (lang(?actor_label) = "en") .
}}
{limit}
'''
def to_list(dict_):
    data = [  [  x['@name'] for x in dict_['sparql']['head']['variable']  ] ]
    for x in dict_['sparql']['results']['result']:
      try:
        data.append([ 
          x['binding'][0]['uri'].replace('http://www.wikidata.org/entity/Q',''),
          x['binding'][1]['literal']['#text'],
          # x['binding'][2]['literal']['#text'],
        ])
      except Exception as e:
        pass
    return data
