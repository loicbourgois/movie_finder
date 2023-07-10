from .common import *


def delete_all_user():
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from dtw_user;
        '''))
