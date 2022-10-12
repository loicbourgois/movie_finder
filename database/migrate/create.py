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


def database_description(database_url):
    table_list = runcmd_list([
        'psql',
        database_url,
        '-c',
        f"\d",
    ])
    command = [
        'psql',
        database_url,
    ]
    for line in table_list[3:len(table_list)-2]:
        table_name = line.split("|")[1].strip()
        command.append("-c")
        command.append(f"\d {table_name}")
    description = runcmd_list(command)
    return "\n".join(description)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Start')
    dataserver_url = get_dataserver_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST')
    database_url = get_database_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME')
    dataserver_engine = create_engine(dataserver_url)
    database_engine = create_engine(database_url)
    for x in range(0,10):
        try:
            test_connection(dataserver_engine)
            break
        except Exception as e:
            time.sleep(1)
    test_connection(dataserver_engine)
    runcmd_list([
        'psql',
        database_url,
        '-c',
        "\d",
    ])
    first_migration = True
    for x in env('migration'):
        if x != "0":
            first_migration = False
    if first_migration:
        write(
            path="/migration_folder/01_before.txt",
            content="",
        )
        runcmd_list([
            'psql',
            dataserver_url,
            '-f',
            "/migration_folder/02_query.sql",
        ])
    else:
        test_connection(database_engine)
        write(
            path="/migration_folder/01_before.txt",
            content=database_description(database_url),
        )
        runcmd_list([
            'psql',
            database_url,
            '-f',
            "/migration_folder/02_query.sql",
        ])
    write(
        path="/migration_folder/03_after.txt",
        content=database_description(database_url),
    )
    output_ = runcmd_list([
        "diff",
        "--unified=5",
        "/migration_folder/01_before.txt",
        "/migration_folder/03_after.txt",
    ], ignore_return_code=True)
    try:
        x[0] = ""
        x[1] = ""
    except Exception as e:
        pass
    write(
        path="/migration_folder/04_diff.txt",
        content="\n".join(output_),
    )
    logging.info('End')
