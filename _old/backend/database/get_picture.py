from .common import *


def get_picture(user_id, x):
    picture_column = ['picture_1', 'picture_2', 'picture_3', 'picture_4'][x['picture_id']]
    with database_engine.connect() as connection:
        r = connection.execute(sql_text(f'''
            select encode({picture_column}, 'base64')
            from dtw_user
            where id = :user_id ;
        '''), {
            'user_id': user_id,
            'picture_column': picture_column,
        }).all()
        return {"data":str(r[0][0])}
