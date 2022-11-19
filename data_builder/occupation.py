from .common import instance_of
from .common import subclass_of
from .common import occupation
from .common import languages
from .common import instance_of_any_subclass_of
from .common import any_subclass_of
import os
name = os.path.basename(__file__).replace('.py', '')

zop = any_subclass_of
zop = "(wdt:P31|wdt:P279)+/wdt:P279"

query = f'''
SELECT ?item ?itemLabel
WHERE {{
  ?item {zop} {occupation} .
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "{languages}"
  }}
}}
'''
header = "url,label"
def line(r):
    return f"{r['item']['value']},{r['itemLabel']['value']}"
