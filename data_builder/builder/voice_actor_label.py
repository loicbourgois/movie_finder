from .common import instance_of_any_subclass_of, film, with_voice_actor, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?voice_actor ?voice_actor_label (lang(?voice_actor_label) as ?lang)
WHERE {{
  ?movie {instance_of_any_subclass_of} {film} .
  ?movie {with_voice_actor} ?voice_actor .
  # ?voice_actor rdfs:label ?voice_actor_label.
  ?voice_actor rdfs:label ?voice_actor_label filter (lang(?voice_actor_label) = "en").
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
          x['binding'][2]['literal']['#text'],
        ])
      except Exception as e:
        pass
    return data
