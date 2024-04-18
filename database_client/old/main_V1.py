import os
import logging
import json
from .submodules.utils.files import (
    read,
    write_force,
)
logging.basicConfig(level=logging.INFO)
logging.info("# start")
c = read(f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder/database_client/{os.environ['QUERY_ID']}.alq")
def find_next(words, word_to_find):
    for i, word in enumerate(words):
        if word == word_to_find:
            return i
def alq_to_sql(text):
    word = ""
    words = []
    keep_spaces = False
    for c in text:
        skips = ["'", " ", "\n"]
        if c == "'" and word == "":
            keep_spaces = True
        elif c == "'":
            keep_spaces = False
        if keep_spaces:
            skips = ["'"]
        if c not in skips:
            word += c
        if c in skips and word != "":
            words.append(word)
            word = ""
    words.append(word)
    mode = ""
    alq = {
        'select': {
            
        },
        'where': [],
        'limit': None
    }
    i = -1
    while i < len(words)-1:
        i+=1
        word = words[i]
        if word == "select":
            mode = "select"
        elif word == "where":
            mode = "where"
        elif word == "limit":
            mode = "limit"
        else:
            if mode == "limit":
                alq['limit'] = word
            if mode == 'where':
                alq['where'].append({
                    'field': words[i], 
                    'comparator': words[i+1], 
                    'value': words[i+2],
                })
                i+=2
            if mode == 'select':
                if words[i+1:i+3] == ['as', '(']:
                    i2 = find_next(words[i:], ")")
                    sub_words = words[i+3:i+i2]
                    alq['select'][word] = {
                        'kinds': { x:"" for x in sub_words if x != 'or' }
                    }
                    i += i2
                else:
                    splt = word.split(".")
                    alq['select'][splt[1]] = {
                        'item': splt[0],
                        'field': splt[1],
                    }
    logging.info(json.dumps(alq, indent=2))
    sql_str = []
    sql_withs = []
    joins = []
    select_first = list(alq['select'].keys())[0]
    for k, v in alq['select'].items():
        if v.get('kinds'):
            aa = ",".join( f"'{x}'" for x in v['kinds'])
            sql_withs.append(f"""
                {k} as (
                    select 
                        item___label.label as {k}, 
                        -- item___label.language as {k}_language,
                         item.item_id as {k}_id,
                        item.kind as {k}_kind
                    from item
                    inner join item___label
                        on item.item_id = item___label.item_id
                    where item.kind in ({aa})
                )
            """)
        if v.get("item"):
            qq = f"{v['item']}_{k}"
            sql_withs.append(f"""
                {qq} as (
                    select 
                        item___label.label as {k}, 
                        -- item___label.language as {k}_language, 
                         item___{k}.item_id as {k}_up_id,
                        item___{k}.{k}_id as {k}_id
                    from item___{k}
                    inner join item___label
                        on item___{k}.{k}_id = item___label.item_id
                )
            """)
            joins.append(f"""
                left outer join {qq}
                    on {v['item']}.{v['item']}_id = {qq}.{k}_up_id
            """)
    sql_str.append(
        f"""
            with {",".join(sql_withs)}
        """
    )
    sql_str.append(
        f"""
            select distinct * from {select_first}
        """
    )
    aa = '\n'.join(joins)
    sql_str.append(
        f"""
            {aa}
        """
    )
    sql_str.append(f"limit {alq.get('limit', '4')}")
    r = "\n".join(sql_str)
    logging.info(r)
    return r
write_force(
    f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder/database_client/{os.environ['QUERY_ID']}.sql",
    alq_to_sql(c),
)
