import logging
logging.basicConfig(level=logging.INFO)
from sqlalchemy import (
    text as sql_text,
)
from .util import database_engine


def answer(x):
    if x['winner'] > x['loser']:
        option_a = x['loser']
        option_b = x['winner']
    else:
        option_a = x['winner']
        option_b = x['loser']
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            insert into answer (user_id, question_id, option_a, option_b, option_win, option_lose)
            values (:user_id, :question_id, :option_a, :option_b, :option_win, :option_lose)
        '''), {
            'user_id': x['user_id'],
            'question_id': x['question_id'],
            'option_a': option_a,
            'option_b': option_b,
            'option_win': x['winner'],
            'option_lose': x['loser'],
        })
