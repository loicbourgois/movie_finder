from .common import instance_of_any_subclass_of, film, with_cast_member, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?cast_member ?cast_member_label (lang(?cast_member_label) as ?lang)
WHERE {{
  ?movie {instance_of_any_subclass_of} {film} .
  ?movie {with_cast_member} ?cast_member .
  # ?cast_member rdfs:label ?cast_member_label.
  ?cast_member rdfs:label ?cast_member_label filter (lang(?cast_member_label) = "en").
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
