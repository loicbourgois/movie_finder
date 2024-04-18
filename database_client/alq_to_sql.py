from .parse_alq import parse_alq
from .sql_elements import sql_elements
from .utils import logging
import json
from .utils import format_sql


def alq_to_sql(text):
    alq = parse_alq(text)
    logging.info(json.dumps(alq, indent=2))
    x = sql_elements(alq)
    kf = x['select_first']
    r = format_sql(
        f""" 
            with {",".join(x['sql_withs'])} 
            ,q_all as (
                select distinct * from {kf}  
                {' '.join(x['joins'])}
            )
            ,q_limit as (
                select distinct {kf}_id from q_all
                limit {alq.get('limit')}
            )
            select q_all.* 
            from q_all
            inner join q_limit
                on q_all.{kf}_id = q_limit.{kf}_id
        """
    )
    return r