from .config import get_config
from .convert_to_csv import convert_to_csv
from .convert_to_sql import convert_to_sql
from .generate_database_config import generate_database_config
from .get_queries import get_queries
from .logger import logger
from .omdb_pull import omdb_pull
from .pull_data import pull_data
import json
from .shared import write_force


def main():
    logger.info("start")
    config = get_config()
    write_force(
        "/root/github.com/loicbourgois/movie_finder/data_builder/config.json",
        json.dumps(config, indent=2),
    )
    # queries = get_queries(config)
    # omdb_pull(config)
    # pull_data(config, queries)
    # convert_to_csv(config, queries)
    # convert_to_sql(config)
    generate_database_config(config)


if __name__ == "__main__":
    main()
