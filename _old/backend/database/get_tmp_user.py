from .common import *


def get_tmp_user(tmp_user_id):
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
              ),
              q5 as (
                select id, pseudo from tmp_user
                where id = :tmp_user_id
              )
              select count_answered, total_rounds, (count_answered / total_rounds) as progress, pseudo, id
              from q4 , q3, q5;
        '''), {
            'tmp_user_id': tmp_user_id,
        }).all()
        return {
            'count_answered': r[0][0],
            'total_rounds': r[0][1],
            'progress': r[0][2],
            'pseudo': r[0][3],
            'id': r[0][4],
        }
