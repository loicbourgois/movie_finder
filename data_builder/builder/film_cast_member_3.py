from .common import instance_of, film, languages, with_cast_member, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?movie ?cast_member
WHERE {{
  ?movie {instance_of} {film} .
  ?movie {with_cast_member} ?cast_member .
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