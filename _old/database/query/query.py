import logging
import os
from sqlalchemy import (
    create_engine,
    text as sql_text,
)
import time
import uuid
import subprocess


def test_connection(engine):
    with engine.connect() as connection:
        assert connection.execute(sql_text(f'''
            select true;
        ''')).all()[0][0]


def env(k):
    return os.environ[k]


def get_dataserver_url(a, b, c):
    return f"postgresql://{env(a)}:{env(b)}@{env(c)}"


def get_database_url(a, b, c, d):
    return f"{get_dataserver_url(a,b,c)}/{env(d)}"


def get_database_url_no_password(a, c, d):
    return f"postgresql://{env(a)}@{env(c)}/{env(d)}"


def execute_sql(engine, query):
    with engine.connect() as connection:
        connection.execute(sql_text(query))


def read(path):
    with open(path, "r") as file:
        return file.read()


def write(path=None, content=None):
    assert path is not None
    assert content is not None
    with open(path, 'w') as file:
        file.write(content)


runcmd_list_stdouts = {}
def runcmd_list(
    command: list,
    quiet=False,
    shell=False,
    parallel=False,
    dir=None,
    format=None,
    env=os.environ.copy(),
    ignore_return_code=False,
):
    if not quiet:
        for line in " ".join(command).split("\n"):
            dir_str = ""
            if dir:
                dir_str = grey(f" # in {dir}")
            line = ("$ " + line + dir_str)
            if parallel:
                line = f"[{os.getpid()}]" + line
            logging.info(line)
    def stream_process(process, command_id):
        go = process.poll() is None
        for line in process.stdout:
            l = os.linesep.join([s for s in line.decode("UTF8").splitlines() if s])
            if not quiet:
                if parallel:
                    logging.info((f"  [{os.getpid()}] {l}"))
                else:
                    logging.info(("  " + l))
            runcmd_list_stdouts[command_id].append(l)
        return go
    command_id = str(uuid.uuid4())
    runcmd_list_stdouts[command_id] = []
    process = subprocess.Popen(
        command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dir
    )
    while stream_process(process, command_id):
        time.sleep(0.1)
    if not ignore_return_code:
        assert (
            process.returncode == 0
        ), f"invalid returncode: expected 0, got {process.returncode} - command: {command}"
    return runcmd_list_stdouts[command_id]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Start')
    database_url = get_database_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME')
    database_url_no_password = get_database_url_no_password('DATABASE_USER', 'DATABASE_HOST', 'DATABASE_NAME')
    database_engine = create_engine(database_url)
    runcmd_list([
        'psql',
        database_url_no_password,
        '-c',
        '\set ON_ERROR_STOP on',
        '-c',
        '\\timing',
        '-f',
        "/root/github.com/loicbourgois/downtowhat/database/query/query.sql",
    ])
    logging.info('End')
