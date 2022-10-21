import logging
from flask import (
    Flask,
    request,
    make_response,
    send_from_directory,
)
import string
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
from . import database
from random import (
    random,
    choices,
)
import uuid


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


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


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
            insert into dtw_user (username, email, hash, salt, description)
            values (:username, :email, :hash, :salt, :description)
            returning id, username, email, salt, hash;
        '''), {
            'username': user['username'],
            'email': user['email'],
            'hash': kdf.derive(bytes(user['password'], 'utf-8')).hex(),
            'salt': salt,
            'description': user['description'],
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
            insert into question (title, prompt, priority)
            values (:title, :prompt, :priority)
            returning id;
        '''), {
            'title': x['title'],
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
        return {'id':id}


def get_user(email):
    with database_engine.connect() as connection:
        x = connection.execute(sql_text(f'''
            select username, salt, hash, email, id
            from dtw_user where email = :email;
        '''), {
            'email': email
        }).all()[0]
        return {
            'username': x[0],
            'salt': x[1],
            'hash': x[2],
            'email': x[3],
            'id': x[4],
        }


def delete_all_questions():
    with database_engine.connect() as connection:
        connection.execute(sql_text(f'''
            delete from option;
            delete from question;
        '''))


def test(database_engine):
    logging.info('Testing')
    test_connection(database_engine)
    database.delete_all_tmp_answer()
    database.delete_all_answer()
    delete_all_questions()
    database.delete_all_tmp_user()
    database.delete_all_user()
    # add_question({
    #     'title': 'Ideal match',
    #     'prompt': 'Who are you looking for ?',
    #     'options': [
    #         'A life partner',
    #         'A lover',
    #         'A friend',
    #         'A distraction',
    #         'A fuck buddy',
    #     ]
    # })['id']
    # add_question({
    #     'title': 'First date',
    #     'prompt': "What's best for a first date ?",
    #     'options': [
    #         'A Walk',
    #         'Sex',
    #         'Drinks',
    #         'Coffee',
    #         'Dinner',
    #         'A movie',
    #     ]
    # })
    add_question({
        'title': 'Good or intersting ',
        'prompt': "What would you rather be a part of ?",
        'options': [
            'Someting good',
            'Something interesting',
        ]
    })
    add_question({
        'title': 'Best place to be',
        'prompt': 'Best place to be ?',
        'options': [
            'At the beach',
            'In the mountains',
            'In the forest',
            'In a vibrant city',
            'In the countryside',
        ]
    })
    add_question({
        'title': 'Crossing the road',
        'prompt': "Why did the frog cross the road ?",
        'options': [
            'To get to the other side',
            'Because a llama ate her hat',
            'To get a job',
        ]
    })
    add_question({
        'title': 'Consequences or intentions',
        'prompt': "Which is most important ?",
        'options': [
            'Intentions',
            'Consequences',
        ]
    })
    add_question({
        'title': 'comparse',
        'prompt': "Which kind of person would you rather have by your side?",
        'options': [
            'Someone brave',
            'Someone loyal',
            'Someone funny',
            'Someone respectful',
            'Someone ambitious',
            'Someone honest',
        ]
    })
    add_question({
        'title': 'toomuch',
        'prompt': "Is 100.000.000$ too much for one person to own ?",
        'options': [
            'Yes',
            'No',
        ]
    })
    add_question({
        'title': 'enough',
        'prompt': "How much is enough ?",
        'options': [
            '1.000$',
            '10.000$',
            '100.000$',
            '1.000.000$',
        ]
    })
    add_question({
        'title': 'earth',
        'prompt': "How old is the earth ?",
        'options': [
            '4.5 billion years old',
            '6000 years old',
        ]
    })
    add_question({
        'title': 'spirits',
        'prompt': "Do you believe in spirits ?",
        'options': [
            'Yes',
            'No',
        ]
    })
    add_question({
        'title': 'stories images',
        'prompt': "Stories are best enjoyed as ...",
        'options': [
            'TV Shows',
            'Movies',
            'Animes',
            'Cartoons',
            'Books',
            'Games',
        ]
    })
    add_question({
        'title': 'commi',
        'prompt': "Is communism a good idea ?",
        'options': [
            'Yes',
            'No',
        ]
    })
    add_question({
        'title': 'capitalism',
        'prompt': "Is capitalism a good idea ?",
        'options': [
            'Yes',
            'No',
        ]
    })
    add_question({
        'title': 'socialism',
        'prompt': "Is socialism a good idea ?",
        'options': [
            'Yes',
            'No',
        ]
    })
    add_question({
        'title': 'suni',
        'prompt': "DO you prefer sunrise or sunset ?",
        'options': [
            'Sunrise',
            'Sunset',
        ]
    })
    # for x in range(0, 10):
    #     add_question({
    #         'title': f'test-{x}',
    #         'prompt': f'test-{x}',
    #         'options': [
    #             f'test-{x}-1',
    #             f'test-{x}-2',
    #             f'test-{x}-3',
    #         ]
    #     })
    for y in range(0, 3):
        r = random()
        tmp_user_id = database.create_tmp_user()['id']
        for x in range(0, int(5*random())):
            logging.info(f"t.{y}.{x}")
            question = database.get_tmp_question(tmp_user_id)
            if random() < r:
                database.tmp_answer({
                    'question_id': question['question_id'],
                    'winner': question['option_a_id'],
                    'loser': question['option_b_id'],
                    'tmp_user_id': tmp_user_id,
                })
            else:
                database.tmp_answer({
                    'question_id': question['question_id'],
                    'winner': question['option_b_id'],
                    'loser': question['option_a_id'],
                    'tmp_user_id': tmp_user_id,
                })
    for y in range(0, 15):
        logging.info(y)
        r = random()
        email = f"test{y}@test.com"
        description = []
        for x in range(0, int(50*random())):
            description.append("".join(choices(list(string.ascii_lowercase), k=( int(10*random()) + 1 ) ) ))
        description = (" ".join(description)).capitalize() + "."
        add_user(database_engine, {
            'username': f'Test {y}',
            'email': email,
            'password': 'hunter',
            'description': description,
        })
        user = get_user(email)
        for x in range(0, int(15*random())):
            logging.info(f"f.{y}.{x}")
            question = database.get_question(user['id'])
            if random() < r:
                database.answer({
                    'question_id': question['question_id'],
                    'winner': question['option_a_id'],
                    'loser': question['option_b_id'],
                    'user_id': user['id'],
                })
            else:
                database.answer({
                    'question_id': question['question_id'],
                    'winner': question['option_b_id'],
                    'loser': question['option_a_id'],
                    'user_id': user['id'],
                })
    user = get_user('test0@test.com')
    x = database.get_matches(user['id'], {
        'filters': {
            'min_match': 0
        }
    })
    # logging.info(x)
    logging.info('All tests ok')


test(database_engine)
# test(database_engine)


def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       try:
           assert request.referrer.startswith(os.environ['referrer'])
           token_a = request.headers['Authorization'].split("Bearer ")[1]
           token_c = request.cookies.get('access_token')
           assert token_a != token_c, f"{token_a} | {token_c}"
           data_a = jwt.decode(token_a, app.config['SECRET_KEY'], algorithms=["HS256"])
           data_c = jwt.decode(token_c, app.config['SECRET_KEY_2'], algorithms=["HS256"])
           assert data_a['exp'] == data_c['exp']
           assert data_a['email'] == data_c['email']
           user = get_user(data_a['email'])
       except Exception as e:
           return jsonify({'message': 'invalid token'})
       return f(user, *args, **kwargs)
   return decorator


app = Flask(
    __name__,
)
app.config['SECRET_KEY'] = os.urandom(16).hex()
app.config['SECRET_KEY_2'] = os.urandom(16).hex()


@app.route('/login', methods=['POST'])
def login_user():
    try:
        user = get_user(request.json['email'])
        verify(request.json['password'], user['salt'], user['hash'])
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=45)
        token_a = jwt.encode(
            {
                'email' : request.json['email'],
                'exp' : exp,
            },
            app.config['SECRET_KEY'],
            "HS256"
        )
        token_c = jwt.encode(
            {
                'email' : request.json['email'],
                'exp' : exp,
            },
            app.config['SECRET_KEY_2'],
            "HS256"
        )
        return jsonify({
            'a': token_a,
            'c': token_c
        })
    except Exception as e:
        logging.error(e)
        return make_response('could not verify',  401, {'Authentication': 'login required'})


@app.route('/questions', methods = ['POST'])
def route_questions():
    return jsonify(database.get_questions())


@app.route('/create_tmp_user', methods = ['POST'])
def route_create_tmp_user():
    return jsonify(database.create_tmp_user())


# @app.route('/get_tmp_user', methods = ['POST'])
# def route_get_tmp_user():
#     return jsonify(database.get_tmp_user(
#         request.json['user_id']
#     ))


@app.route('/get_tmp_question', methods = ['POST'])
def route_get_tmp_question():
    return jsonify(database.get_tmp_question(
        request.json['user_id']
    ))


@app.route('/tmp_answer', methods = ['POST'])
def route_tmp_answer():
    return jsonify(database.tmp_answer(request.json))


@app.route('/set_tmp_pseudo', methods = ['POST'])
def route_set_tmp_pseudo():
    return jsonify(database.set_tmp_pseudo(request.json))


@app.route('/tmp_match_percent', methods = ['POST'])
def route_tmp_match_percent():
    return jsonify(database.tmp_match_percent(
        request.json['tmp_user_id_left'],
        request.json['tmp_user_id_right'],
    ))


@app.route('/tmp_match_percent_by_share_id', methods = ['POST'])
def route_tmp_match_percent_by_share_id():
    return jsonify(database.tmp_match_percent_by_share_id(
        request.json['tmp_user_id'],
        request.json['tmp_user_share_id'],
    ))


@app.route('/get_tmp_user_share_id', methods = ['POST'])
def route_get_tmp_user_share_id():
    return jsonify(database.get_tmp_user_share_id(
        request.json['tmp_user_id'],
    ))


@app.route('/get_tmp_user', methods = ['POST'])
def route_get_tmp_user():
    return jsonify(database.get_tmp_user(
        request.json['tmp_user_id'],
    ))


@app.route('/tmp_reset', methods = ['POST'])
def route_tmp_reset():
    return jsonify(database.tmp_reset(
        request.json['tmp_user_id'],
    ))


@app.route('/', methods = ['GET'])
def index():
    return front('index.html')


@app.route('/about', methods = ['GET', 'POST'])
def about():
    return jsonify({'version' : '0'})


@app.route('/<path>', methods = ['GET'])
def front(path):
    if path in [
        'play',
        'login',
        'pictures',
        'profile',
    ]:
        return front('index.html')
    else:
        return send_from_directory(env('front_dir'), {}.get(path, path))


@app.route('/<path>/<path2>', methods = ['GET'])
def front_2(path, path2):
    if path == 'play' and is_valid_uuid(path2):
        return front('index.html')
    return send_from_directory(env('front_dir'), {}.get(f"{path}/{path2}", f"{path}/{path2}"))


#
# Private routes
#


@app.route('/protected', methods = ['POST'])
@token_required
def protected(user):
    return jsonify({'message' : 'protected'})


@app.route('/get_matches', methods = ['POST'])
@token_required
def route_get_matches(user):
    return jsonify(database.get_matches(user['id'], request.json))


@app.route('/add_picture', methods = ['POST'])
@token_required
def route_add_picture(user):
    return jsonify(database.add_picture(user['id'], request.json))


@app.route('/get_picture', methods = ['POST'])
@token_required
def route_get_picture(user):
    return jsonify(database.get_picture(user['id'], request.json))
