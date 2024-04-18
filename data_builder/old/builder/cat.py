from .common import instance_of, cat, languages
import os
import csv
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?item ?itemLabel
WHERE {{
  ?item {instance_of} {cat} .
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "{languages}"
  }}
}}
'''
def to_list(dict_):
    data = [  [  x['@name'] for x in dict_['sparql']['head']['variable']  ] ]
    for x in dict_['sparql']['results']['result']:
        data.append(  [ x['binding'][0]['uri'],x['binding'][1]['literal']['#text']  ]  )
    return data