from .utils import column_type
from .utils import logging


def wheres(k, alq):
    l = ['true']
    for x in alq['where']:
        if x['field'] == k or x['field'].replace(".", "_") == k:
            l.append(f"item___label.label {x['comparator']} '{x['value']}'")
    return " and ".join(l) 


def sql_elements(alq):
    sql_withs = []
    joins = []
    select_first = list(alq['select'].keys())[0]
    for k in alq['select_keys']:
        v = alq['select'][k]
        if v.get('kinds'):
            aa = ",".join( f"'{x}'" for x in v['kinds'])
            sql_withs.append(f"""
                {k} as (
                    select 
                        item___label.label as {k}, 
                        item___label.language as {k}_language,
                         item.item_id as {k}_id,
                        item.kind as {k}_kind
                    from item
                    inner join item___label
                        on item.item_id = item___label.item_id
                    where /*w1*/ item.kind in ({aa}) and {wheres(k, alq)}
                )
            """)
        if v.get("item"):
            aa = ""
            field = v['field']
            if v.get("parent_item"):
                aa = v['parent_item'] + "_"
            parent_table = f"{aa}{v['item']}"
            table = f"item___{v['field']}"
            joins.append(f"""
                left outer join {k}
                    on {parent_table}.{parent_table}_id = {k}.{k}_up_id
            """)
            if column_type(k) == 'int':
                sql_withs.append(f"""
                    {k} as (
                        select 
                            item___label.label as {k}, 
                            item___label.language as {k}_language, 
                            {table}.item_id as {k}_up_id,
                            {table}.{field}_id as {k}_id
                        from {table}
                        inner join item___label
                            on {table}.{field}_id = item___label.item_id
                        where /*w2*/ {wheres(k, alq)}
                    )
                """)
            else:
                sql_withs.append(f"""
                    {k} as (
                        select 
                            {table}.item_id as {k}_up_id,
                            {table}.{k} as {k}
                        from {table}
                    )
                """)
    where = ['True']
    for x in alq['where']:
        where.append(f"{x['field'].replace(".", "_")} {x['comparator']} '{x['value']}'")
    return {
        'sql_withs': sql_withs,
        'joins': joins,
        'select_first': select_first,
        'where': where,
    }