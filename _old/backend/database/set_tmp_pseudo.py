from .common import *


def set_tmp_pseudo(x):
    with database_engine.connect() as connection:
        connection.execute(
            sql_text(f'''
                update tmp_user
                set pseudo = :pseudo
                where id = :tmp_user_id ;
            '''),
            x
        )
    return True


# belief, lifestyle, general preferences etc ..
