social_status = "wd:Q189970"
from ..common import instance_of
from ..common import human_activity
from ..common import subclass_of
from ..common import languages
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?item ?itemLabel
WHERE {{
  ?item {instance_of}/{subclass_of} {social_status} .
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "{languages}"
  }}
}}
'''

query = f'''
SELECT ?item ?itemLabel
WHERE {{
  ?item {subclass_of}/{subclass_of} {social_status} .
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "{languages}"
  }}
}}
'''

header = "url,label"
def line(r):
    return f"{r['item']['value']},{r['itemLabel']['value']}"
