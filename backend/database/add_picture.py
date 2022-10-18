from .common import *


def add_picture(user_id, x):
    picture_column = ['picture_1', 'picture_2', 'picture_3', 'picture_4'][x['picture_id']]
    picture_column_status = f"{picture_column}_status"
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            update dtw_user
            set {picture_column} = :data,
                {picture_column_status} = 'pending'
            where id = :user_id ;
        '''), {
            'user_id': user_id,
            'picture_column': picture_column,
            'data': x['data'],
            'picture_column_status': picture_column_status,
        })
