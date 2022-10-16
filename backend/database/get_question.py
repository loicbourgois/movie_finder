import logging
logging.basicConfig(level=logging.INFO)
from sqlalchemy import (
    text as sql_text,
)
from .util import database_engine


def get_question(user_id):
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
                from answer
                where question_id = question.id
                  and answer.user_id = :user_id
              ) as answer_count,
              (
                select count(*)
                from option
                where question.id = option.question_id
              ) as option_count
              from question, dtw_user
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
                  LEFT JOIN answer
                    on option_a.id = answer.option_a
                      and option_b.id = answer.option_b
                      and answer.user_id = :user_id
                  where
                      option_a.id < option_b.id
                      and answer.user_id is null
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
              LEFT JOIN answer
                on option_a.id = answer.option_a
                  and option_b.id = answer.option_b
                  and answer.user_id = :user_id
              where
                  option_a.id < option_b.id
                  and answer.user_id is null
                  and question_.question_id = Q.id
              ORDER BY RANDOM ()
              limit 1
            ;
        '''), {
            'user_id': user_id,
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
