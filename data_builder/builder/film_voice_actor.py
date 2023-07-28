from .common import instance_of_any_subclass_of, film, with_voice_actor, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?movie ?voice_actor
WHERE {{
  ?movie {instance_of_any_subclass_of} {film} .
  ?movie {with_voice_actor} ?voice_actor .
}}
{limit}
'''
def to_list(dict_):
    data = [  [  x['@name'] for x in dict_['sparql']['head']['variable']  ] ]
    for x in dict_['sparql']['results']['result']:
      try:
        data.append([ 
          x['binding'][0]['uri'].replace('http://www.wikidata.org/entity/Q',''),
          x['binding'][1]['uri'].replace('http://www.wikidata.org/entity/Q',''),
          x['binding'][2]['literal']['#text'],
          x['binding'][3]['literal']['#text'],
        ])
      except Exception as e:
        pass
    return data
