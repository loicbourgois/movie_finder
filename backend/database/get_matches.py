import logging
logging.basicConfig(level=logging.INFO)
from sqlalchemy import (
    text as sql_text,
)
from .util import database_engine


def get_matches(user_id, x):
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            with q1 as (
              select
                t_a.user_id as ua,
                t_b.user_id as ub,
                t_a.option_a,
                t_a.option_b,
                t_a.option_win = t_b.option_win as same
              from
                answer t_a,
                answer t_b
              where
                t_a.user_id < t_b.user_id
                and t_a.option_a = t_b.option_a
                and t_a.option_b = t_b.option_b
            ),
            q2 as (
              select count(same)as total , ua, ub  from q1 group by ua, ub
            ),
            q3 as (
              select count(same)as same, ua, ub,
              ( select count(*) from answer where user_id = ua ) as total_a,
              ( select count(*) from answer where user_id = ub ) as total_b
              from q1 where same group by ua, ub
            ),
            q4 as (
                select
                  q2.ua,
                  q2.ub,
                  total_a,
                  total_b,
                  total as total_ab,
                  same,
                  cast(same as float) * 2.0 / cast(total_a + total_b as float) as match,
                  ( case when q2.ua != :user_id then q2.ua else q2.ub end ) as other_id
                from q2, q3
                where q2.ua = q3.ua
                  and q2.ub = q3.ub
                  and (
                    q2.ua = :user_id
                    or q2.ub = :user_id
                  )
                group by total, same, q2.ua, q2.ub, q3.total_a, q3.total_b
            )
            select q4.*, dtw_user.username, dtw_user.description
            from q4
            join dtw_user
                on dtw_user.id = other_id
            where match >= :min_match
            order by match desc
            limit 12 ;
        '''), {
            'user_id': user_id,
            'min_match': x['filters']['min_match'],
        }).all()
        return {
            i: {
                'ua': x[0],
                'ub': x[1],
                'ta': x[2],
                'tb': x[3],
                'tab': x[4],
                'same': x[5],
                'm': x[6],
                'o_id': x[7],
                'o_username': x[8],
                'od': x[9],
            }
            for i, x in enumerate(r)
        }
