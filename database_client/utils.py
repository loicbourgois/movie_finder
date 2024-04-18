import logging
import sqlglot
logging.basicConfig(level=logging.INFO)
logging.info("# start")


def column_type(k):
    return {
        'publication_date': 'date',
    }.get(k, 'int')


def format_sql(x):
    return sqlglot.transpile(x, write="postgres", pretty=True)[0]
