# profession = "wd:Q28640"
# subclass_of = "wdt:P279"

# from ..common import instance_of
# from ..common import human_activity
# from ..common import languages
# import os
# name = os.path.basename(__file__).replace('.py', '')
# query = f'''
# SELECT ?item ?itemLabel
# WHERE {{
#   ?item {instance_of}/{subclass_of} {profession} .
#   SERVICE wikibase:label {{
#     bd:serviceParam wikibase:language "{languages}"
#   }}
# }}
# '''
# header = "url,label"
# def line(r):
#     return f"{r['item']['value']},{r['itemLabel']['value']}"
