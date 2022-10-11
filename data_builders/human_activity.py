from ..common import instance_of
from ..common import human_activity
from ..common import languages
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?item ?itemLabel
WHERE {{
  ?item {instance_of} {human_activity} .
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "{languages}"
  }}
}}
'''
header = "url,label"
def line(r):
    return f"{r['item']['value']},{r['itemLabel']['value']}"
