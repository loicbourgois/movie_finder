from .common import *


def get_tmp_user_share_id(tmp_user_id):
    with database_engine.connect() as connection:
        return {
            'id': connection.execute(
                sql_text(f'''
                    select share_id from tmp_user where id = :tmp_user_id;
                '''),
                {'tmp_user_id':tmp_user_id}
            ).all()[0][0]
        }
