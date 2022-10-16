import os
from sqlalchemy import (
    create_engine,
)

def env(k):
    return os.environ[k]


def get_dataserver_url(a, b, c):
    return f"postgresql://{env(a)}:{env(b)}@{env(c)}"


def get_database_url(a, b, c, d):
    return f"{get_dataserver_url(a,b,c)}/{env(d)}"



database_engine = create_engine(get_database_url('DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME'))
