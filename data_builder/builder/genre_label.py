from .common import instance_of_any_subclass_of, genre, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?genre ?genre_label (lang(?genre_label) as ?lang)
WHERE {{
  ?genre {instance_of_any_subclass_of} {genre} .
  ?genre rdfs:label ?genre_label filter (lang(?genre_label) = "en").
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
