from .common import instance_of_any_subclass_of, film, with_image, limit
import os
name = os.path.basename(__file__).replace('.py', '')
query = f'''
SELECT ?movie ?image
WHERE {{
  ?movie {instance_of_any_subclass_of} {film} .
  ?movie {with_image} ?image .
}}
{limit}
'''
