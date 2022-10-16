import logging
logging.basicConfig(level=logging.INFO)
from sqlalchemy import (
    text as sql_text,
)
from .util import database_engine


def delete_all_user():
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from dtw_user;
        '''))
