from .common import instance_of, film, languages, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?movie ?movieLabel
WHERE {{
  ?movie {instance_of} {film} .
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "{languages}"
  }}
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
        ])
      except Exception as e:
        pass
    return data