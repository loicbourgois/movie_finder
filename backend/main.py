import logging
from flask import (
    Flask,
    # request,
    send_from_directory,
)
from flask import jsonify as flask_jsonify
import bleach
from sqlalchemy import (
    create_engine,
    text as sql_text,
)
import os


def env(k):
    return os.environ[k]


def get_dataserver_url(a, b, c):
    return f"postgresql://{env(a)}:{env(b)}@{env(c)}"


def get_database_url(a, b, c, d):
    return f"{get_dataserver_url(a,b,c)}/{env(d)}"


def test_connection(engine):
    with engine.connect() as connection:
        assert connection.execute(sql_text(f'''
            select true;
        ''')).all()[0][0]


def jsonify(data):
    response = flask_jsonify(data)
    response.set_data(bleach.clean(response.get_data().decode()))
    return response


def test(database_engine):
    logging.info('Testing')
    test_connection(database_engine)
    logging.info('All tests ok')


logging.basicConfig(level=logging.INFO)
logging.info('Start')


database_engine = create_engine(get_database_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME'))
test(database_engine)


app = Flask(
    __name__,
)


@app.route('/', methods = ['GET'])
def index():
    return front('index.html')


@app.route('/<path>', methods = ['GET'])
def front(path):
    if path in [
        'tab',
    ]:
        return front('index.html')
    else:
        return send_from_directory(env('front_dir'), {}.get(path, path))
