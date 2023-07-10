#!/bin/sh
# $HOME/github.com/loicbourgois/downtowhat/database/query/query.sh
set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
environment=$environment \
  docker-compose --file $SCRIPT_DIR/docker-compose.yml up --build --force-recreate dtw_database_query
