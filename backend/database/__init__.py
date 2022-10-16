import os
import logging
from sqlalchemy import (
    create_engine,
    text as sql_text,
)


def env(k):
    return os.environ[k]


def get_dataserver_url(a, b, c):
    return f"postgresql://{env(a)}:{env(b)}@{env(c)}"


def get_database_url(a, b, c, d):
    return f"{get_dataserver_url(a,b,c)}/{env(d)}"


logging.basicConfig(level=logging.INFO)
database_engine = create_engine(get_database_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME'))


from .delete_all_user import delete_all_user
from .delete_all_answer import delete_all_answer
from .get_matches import get_matches
from .get_question import get_question
from .answer import answer


def get_questions():
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            select id, title, prompt, priority
            from question
            order by priority;
        ''')).all()
        r2 = connection.execute(sql_text(f'''
            select id, question_id, str
            from option;
        ''')).all()
    return {
        a[1] : {
            'id': str(a[0]),
            'title': a[1],
            'prompt': a[2],
            'priority': a[3],
            'options': {
                str(b[0]): {
                    'id': str(b[0]),
                    'question_id': str(b[1]),
                    'str': b[2],
                }
                for b in r2 if b[1] == a[0]
            }
        }
        for a in r
    }


def create_tmp_user():
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            insert into tmp_user DEFAULT VALUES
            returning *;
        ''')).all()[0]
        return {
            'id': r[0],
        }


def get_tmp_user(user_id):
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            select id from tmp_user where id = :id;
        '''), {
            'id': user_id
        }).all()
        return {
            'id': r[0][0],
        }


def get_tmp_question(tmp_user_id):
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            with prio_max as (
              select max(priority) as prio_max
              from question
            ),
            q1 as (
                select
                    question.id,
                  question.prompt,
                  question.priority,
              (
                select count(*)
                from tmp_answer
                where question_id = question.id
                  and tmp_answer.tmp_user_id = :tmp_user_id
              ) as answer_count,
              (
                select count(*)
                from option
                where question.id = option.question_id
              ) as option_count
              from question, tmp_user
            ),
            q2 as (
                select *
                from q1, prio_max
            ),
            q3 as (
                select *, ((option_count)*(option_count-1)/2) as rounds
                from q2
            ),
            q4 as (
                select *, (cast(answer_count as float) / cast(rounds as float)) as progress
                from q3
            ),
            q5 as (
                select *, (cast( (prio_max+1-priority) as float) * (1.0  - progress ) * (1.0  - progress ) ) as priority_x_remaining
                from q4
            ),
            Q as (
                select * from q5
            ),
            question_ as (
                select
                     Q.id as question_id
                  from
                      Q
                  inner join option as option_a
                    on Q.id = option_a.question_id
                  inner join option as option_b
                    on Q.id = option_b.question_id
                  LEFT JOIN tmp_answer
                    on option_a.id = tmp_answer.option_a
                      and option_b.id = tmp_answer.option_b
                      and tmp_answer.tmp_user_id = :tmp_user_id
                  where
                      option_a.id < option_b.id
                      and tmp_answer.tmp_user_id is null
                  order by
                      Q.priority_x_remaining desc
                  limit 1
            )
            select
                Q.prompt,
                option_a.str,
                option_b.str,
                  Q.id as question_id,
                  option_a.id,
                  option_b.id
              from
                  Q
              inner join question_ as question_
                on Q.id = question_.question_id
              inner join option as option_a
                on Q.id = option_a.question_id
              inner join option as option_b
                on Q.id = option_b.question_id
              LEFT JOIN tmp_answer
                on option_a.id = tmp_answer.option_a
                  and option_b.id = tmp_answer.option_b
                  and tmp_answer.tmp_user_id = :tmp_user_id
              where
                  option_a.id < option_b.id
                  and tmp_answer.tmp_user_id is null
                  and question_.question_id = Q.id
              ORDER BY RANDOM ()
              limit 1
            ;
        '''), {
            'tmp_user_id': tmp_user_id,
        }).all()
        try:
            return {
                'prompt': r[0][0],
                'option_a': r[0][1],
                'option_b': r[0][2],
                'question_id': r[0][3],
                'option_a_id': r[0][4],
                'option_b_id': r[0][5],
            }
        except Exception as e:
            return {}


def delete_all_tmp_user():
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from tmp_user;
        '''))


def delete_all_tmp_answer():
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from tmp_answer;
        '''))


def tmp_answer(x):
    if x['winner'] > x['loser']:
        option_a = x['loser']
        option_b = x['winner']
    else:
        option_a = x['winner']
        option_b = x['loser']
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            insert into tmp_answer (tmp_user_id, question_id, option_a, option_b, option_win, option_lose)
            values (:tmp_user_id, :question_id, :option_a, :option_b, :option_win, :option_lose)
        '''), {
            'tmp_user_id': x['tmp_user_id'],
            'question_id': x['question_id'],
            'option_a': option_a,
            'option_b': option_b,
            'option_win': x['winner'],
            'option_lose': x['loser'],
        })


def tmp_match_percent(tmp_user_id_1, tmp_user_id_2):
    if  tmp_user_id_1 < tmp_user_id_2:
        tmp_user_id_a = tmp_user_id_1
        tmp_user_id_b = tmp_user_id_2
    else:
        tmp_user_id_a = tmp_user_id_2
        tmp_user_id_b = tmp_user_id_1
    with database_engine.connect() as connection:
        try:
            r = connection.execute(sql_text(f'''
                with q1 as (
                  select
                    t_a.tmp_user_id as ua,
                    t_b.tmp_user_id as ub,
                    t_a.option_a,
                    t_a.option_b,
                    t_a.option_win = t_b.option_win as same
                  from
                    tmp_answer t_a,
                    tmp_answer t_b
                  where
                    t_a.tmp_user_id < t_b.tmp_user_id
                    and t_a.option_a = t_b.option_a
                    and t_a.option_b = t_b.option_b
                    and t_a.tmp_user_id = :tmp_user_id_a
                    and t_b.tmp_user_id = :tmp_user_id_b
                ),
                q2 as (
                  select count(same)as total , ua, ub  from q1 group by ua, ub
                ),
                q3 as (
                  select count(same)as same, ua, ub,
                  ( select count(*) from tmp_answer where tmp_user_id = ua ) as total_a,
                  ( select count(*) from tmp_answer where tmp_user_id = ub ) as total_b
                  from q1 where same group by ua, ub
                )
                select
                  q2.ua, q2.ub,
                  total_a,
                  total_b,
                  total as total_ab,
                  same,
                  cast(same as float) * 2.0 / cast(total_a + total_b as float) as match
                from q2, q3
                where q2.ua = q3.ua
                  and q2.ub = q3.ub
                group by total, same, q2.ua, q2.ub, q3.total_a, q3.total_b
                order by match desc limit 10
            '''), {
                'tmp_user_id_a': tmp_user_id_a,
                'tmp_user_id_b': tmp_user_id_b,
            }).all()
            return r[0][6]
        except Exception as e:
            pass


def tmp_progress(tmp_user_id):
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            with q1 as (
                  select question.*, (
                      select count(*)
                      from option
                      where option.question_id = question.id
                  ) as option_count
                  from question
                  group by  question.id
              ),
              q2 as (
                  select *, ((option_count)*(option_count-1)/2) as rounds
                  from q1
              ),
              q3 as (
                  select count(*) as count_answered
                  from tmp_answer
                  where tmp_user_id = :tmp_user_id
              ),
              q4 as (
                select sum(rounds) as total_rounds
                from q2
              )
              select count_answered, total_rounds, (count_answered / total_rounds) as progress
              from q4 , q3;

        '''), {
            'tmp_user_id': tmp_user_id,
        }).all()
        return {
            'count_answered': r[0][0],
            'total_rounds': r[0][1],
            'progress': r[0][2],
        }


def tmp_reset(id):
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from tmp_answer where tmp_user_id = :id
        '''), {
            'id':id
        })
