from .parse_alq import parse_alq
from .sql_elements import sql_elements
from .utils import column_type
from .utils import format_sql
from .utils import logging


def fields_str(kf, alq):
    # logging.info(f"{kf}.fields")
    fields = []
    for k, v in alq['select'].items():
        oo = v.get('field')
        # logging.info(f"  {v.get('item_full')}")
        if v.get('item_full') == kf:
            if column_type(k) == 'int':
                fields.append(f"""
                    ,'{oo}', coalesce(json_object_agg(
                        {k}_id,
                        {k}_data /* 6.1 */
                    ) FILTER (WHERE {k}_id IS NOT NULL), '{{}}'::JSON)
                """)
            else:
                fields.append(f"""
                    ,'{k}', {k}
                """)
    return "\n".join(fields)


def joins_str(kf, alq):
    joins = []
    for k, v in alq['select'].items():
        if v.get('item') == kf :
            join_type = "left outer"
            for uu in alq['where']:
                if uu['field'] == k:
                    join_type = "inner"
            joins.append(
                f"""
                    /* c3 */
                    {join_type} JOIN {k}_j ON {kf}.{kf}_id = {k}_j.{k}_up_id
                """
            )
        elif kf == f"{v.get('parent_item')}_{v.get('item')}":
            join_type = "left outer"
            for uu in alq['where']:
                if uu['field'] == k:
                    join_type = "inner"
            joins.append(
                f"""
                    /* c4 */
                    {join_type} JOIN {k}_j /* 7.1 */ 
                    ON {kf}.{kf}_id = {k}_j.{k}_up_id
                """
            )
    return "\n".join(joins)


def alq_to_sql_json(text):
    alq = parse_alq(text)
    x = sql_elements(alq)
    kf = x['select_first']
    group_bys = [f"{kf}.{kf}_id", f"{kf}.{kf}_kind"]
    alq['select_keys'].reverse()
    for k in alq['select_keys']:
        v = alq['select'][k]
        if v.get('item'):
            a = v.get('item')
            b = v.get('field')
            if column_type(k) == 'int':
                x['sql_withs'].append(
                    f"""
                        /* 7.2 */
                        {k}_j AS (
                        SELECT
                            {k}_up_id,
                            {k}_id,
                            json_build_object(
                                'label', 
                                json_object_agg({k}_language, {k})
                                {fields_str(k, alq)}
                            ) AS {k}_data /* 6.2 */
                        FROM {k}
                            {joins_str(f'{a}_{b}', alq)}
                        GROUP BY
                            {k}_up_id,
                            {k}_id
                        )
                    """
                )
            else:
                group_bys.append(b)
                x['sql_withs'].append(
                    f"""
                        /* c1 */
                        {a}_{b}_j AS (
                        SELECT
                            {b}_up_id,
                            {b}
                        FROM {a}_{b}
                        GROUP BY
                            {b}_up_id,
                            {b}
                        )
                    """
                )
    group_bys_str = ",".join(group_bys)
    x['sql_withs'].append(
        f"""
            {kf}_j AS (
                SELECT
                    {kf}_id,
                    json_build_object(
                        'label', json_object_agg({kf}_language, {kf}),
                        'kind', {kf}.{kf}_kind
                        {fields_str(kf, alq)}
                    ) AS {kf}_data
                FROM {kf}
                    {joins_str(kf, alq)}
                GROUP BY
                    {group_bys_str}
            )
        """
    )
    x['end'] = f"""
        ,q_limit AS (
            SELECT DISTINCT {kf}_id 
            FROM {kf}_j 
            LIMIT {alq.get('limit')}
        ),
        q2 AS (
        SELECT json_object_agg(
            {kf}_j.{kf}_id, {kf}_j.{kf}_data
        ) AS data
        FROM {kf}_j
        INNER JOIN q_limit
            ON {kf}_j.{kf}_id = q_limit.{kf}_id
            LIMIT 3
        )
        SELECT jsonb_pretty(data::JSONB) AS data
        FROM q2;
    """
    r = format_sql(" ".join([
        f""" with {",".join(x['sql_withs'])} """,
        x['end'],
    ]))
    return r
