# from .common import instance_of
# from .common import action
# from .common import languages
# import os
# name = os.path.basename(__file__).replace('.py', '')
# query = f'''
# SELECT ?item ?itemLabel
# WHERE {{
#   ?item {instance_of} {action} .
#   SERVICE wikibase:label {{
#     bd:serviceParam wikibase:language "{languages}"
#   }}
# }}
# '''
# header = "url,label"
# def line(r):
#     return f"{r['item']['value']},{r['itemLabel']['value']}"
