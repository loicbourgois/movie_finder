from .logger import get_logger, set_up_logger
set_up_logger("movie_finder")
from .pull_data import pull_data
from .convert_to_csv import convert_to_csv
from .convert_to_sql import convert_to_sql
from .config import get_config
from .get_queries import get_queries
from .runcmd import runcmd_list
logger = get_logger()
logger.info("start")
endpoint_url = "https://query.wikidata.org/sparql"
instance_of_any_subclass_of = "wdt:P31/wdt:P279*"

# https://www.omdb.org/en/us/content/Help:DataDownload
def omdb_pull(config):
    omdb_folder = "/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/omdb"
    runcmd_list(["mkdir", "-p", omdb_folder])
    for item in config['omdb'].keys():
        url = f"https://www.omdb.org/data/{item}.csv.bz2"
        file = f"{item}.csv.bz2"
        runcmd_list(["curl", url, "-O"], cwd=omdb_folder)
        runcmd_list(["bzip2", "-d", file], cwd=omdb_folder)



# def omdb_convert_to_sql():
#     for x in []:

#         CREATE TABLE item (
#   item_id int not null,
#   kind kind not null
# );


# omdb_pull()
# omdb_convert_to_sql()
config = get_config()
# queries = get_queries(config)
# pull_data(config, queries)
# convert_to_csv(config, queries)
convert_to_sql(config)
