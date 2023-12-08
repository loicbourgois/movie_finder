import os
from .submodules.utils.files import (
    read,
    write_force,
)
import json
from .parse_alq import parse_alq
from .alq_to_sql import alq_to_sql
from .alq_to_sql_json import alq_to_sql_json
c = read(f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder/database_client/{os.environ['QUERY_ID']}.alq")
a = alq_to_sql(c)
b = alq_to_sql_json(c)
d = json.dumps(parse_alq(c), indent=4)
write_force(
    f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder/database_client/{os.environ['QUERY_ID']}_alq.json",
    d,
)
write_force(
    f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder/database_client/{os.environ['QUERY_ID']}_table.sql",
    a,
)
write_force(
    f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder/database_client/{os.environ['QUERY_ID']}_json.sql",
    b,
)
