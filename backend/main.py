import logging
from flask import (
    Flask,
    request,
    make_response,
    send_from_directory,
)
from flask import jsonify as flask_jsonify
import bleach
from sqlalchemy import (
    create_engine,
    text as sql_text,
)
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from functools import wraps
import uuid
import jwt
import datetime


def env(k):
    return os.environ[k]


def get_dataserver_url(a, b, c):
    return f"postgresql://{env(a)}:{env(b)}@{env(c)}"


def get_database_url(a, b, c, d):
    return f"{get_dataserver_url(a,b,c)}/{env(d)}"


logging.basicConfig(level=logging.INFO)
logging.info('Start')
database_engine = create_engine(get_database_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME'))


def test_connection(engine):
    with engine.connect() as connection:
        assert connection.execute(sql_text(f'''
            select true;
        ''')).all()[0][0]


def jsonify(data):
    response = flask_jsonify(data)
    response.set_data(bleach.clean(response.get_data().decode()))
    return response


def kdf_salt(salt=None):
    if not salt:
        salt = os.urandom(16).hex()
    return Scrypt(
        salt=bytes.fromhex(salt),
        length=32,
        n=2**14,
        r=8,
        p=1,
    ), salt


def verify(password, salt, hash):
    kdf, _ = kdf_salt(salt)
    kdf.verify(bytes(password, 'utf-8'), bytes.fromhex( hash ))


def add_user(engine, user):
    # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#scrypt
    with engine.connect() as connection:
        kdf, salt = kdf_salt()
        r = connection.execute(sql_text(f'''
            insert into dtw_user (username, email, hash, salt)
            values (:username, :email, :hash, :salt)
            returning id, username, email, salt, hash;
        '''), {
            'username': user['username'],
            'email': user['email'],
            'hash': kdf.derive(bytes(user['password'], 'utf-8')).hex(),
            'salt': salt,
        }).all()[0]
    verify(user['password'], r[3], r[4])


def delete_user(engine, username):
    with engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from dtw_user where username = :username;
        '''), {
            'username': username,
        })


def add_question(x):
    with database_engine.connect() as connection:
        transaction = connection.begin()
        priority = 1
        try:
            priority = connection.execute(sql_text(f'''
                select max(priority) from question;
            ''')).all()[0][0] + 1
        except Exception as e:
            pass
        id = connection.execute(sql_text(f'''
            insert into question (description, prompt, priority)
            values (:description, :prompt, :priority)
            returning id;
        '''), {
            'description': x['description'],
            'prompt': x['prompt'],
            'priority': priority,
        }).all()[0][0]
        for xx in x['options']:
            connection.execute(sql_text(f'''
                insert into option (question_id, str)
                values (:question_id, :str);
            '''), {
                'question_id': id,
                'str': xx,
            })
        transaction.commit()


def get_user(email):
    with database_engine.connect() as connection:
        x = connection.execute(sql_text(f'''
            select username, salt, hash
            from dtw_user where email = :email;
        '''), {
            'email': email
        }).all()[0]
        return {
            'username': x[0],
            'salt': x[1],
            'hash': x[2],
        }


def test(database_engine):
    logging.info('Testing')
    test_connection(database_engine)
    delete_user(database_engine, 'test')
    delete_user(database_engine, 'test2')
    add_user(database_engine, {
        'username': 'test',
        'email': 'test@test.com',
        'password': 'hunter',
    })
    add_user(database_engine, {
        'username': 'test2',
        'email': 'test2@test.com',
        'password': 'hunter',
    })
    delete_user(database_engine, 'test2')
    add_question({
        'description': 'Ideal match',
        'prompt': 'Who you looking for ?',
        'options': [
            'A life partner',
            'A lover',
            'A friend',
            'A date',
            'A distraction',
            'A fuck buddy',
        ]
    })
    add_question({
        'description': 'First date',
        'prompt': 'What to do for a first date ?',
        'options': [
            'Walk and talk',
            'Have sex',
            'Get a drink',
            'Grab a coffee',
            'Have dinner',
            'Go to the movie',
            'Chill',
        ]
    })
    add_question({
        'description': 'Best place to be',
        'prompt': 'Best place to be ?',
        'options': [
            'At the beach',
            'In the mountains',
            'Deep in the forest',
            'In a vibrant city',
            'Lost at sea',
            'The countryside',
        ]
    })
    add_question({
        'description': 'Good or intersting ',
        'prompt': "What would you rather be a part of ?",
        'options': [
            'Someting good',
            'Something interesting',
        ]
    })
    logging.info('All tests ok')


test(database_engine)
test(database_engine)


def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       try:
           token = request.headers['Authorization'].split("Bearer ")[1]
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           user = get_user(data['email'])
       except:
           return jsonify({'message': 'token is invalid'})
       return f(user, *args, **kwargs)
   return decorator


app = Flask(
    __name__,
)
app.config['SECRET_KEY'] = os.urandom(16).hex()


@app.route('/login', methods=['POST'])
def login_user():
    try:
        user = get_user(request.json['email'])
        verify(request.json['password'], user['salt'], user['hash'])
        token = jwt.encode(
            {
                'email' : request.json['email'],
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)
            },
            app.config['SECRET_KEY'],
            "HS256"
        )
        return jsonify({'token' : token})
    except Exception as e:
        return make_response('could not verify',  401, {'Authentication': 'login required'})


@app.route('/protected', methods = ['POST'])
@token_required
def protected(user):
    return jsonify({'message' : 'protected'})


@app.route('/', methods = ['GET'])
def index():
    return front('index.html')


@app.route('/about', methods = ['GET', 'POST'])
def about():
    return jsonify({'version' : '0'})


@app.route('/<path>', methods = ['GET'])
def front(path):
    if path in [
        'me',
        'quiz',
        'home',
    ]:
        return front('index.html')
    else:
        return send_from_directory(env('front_dir'), {}.get(path, path))


@app.route('/<path>/<path2>', methods = ['GET'])
def front_2(path, path2):
    return send_from_directory(env('front_dir'), {}.get(f"{path}/{path2}", f"{path}/{path2}"))
