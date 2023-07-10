#!/bin/sh
set -e
migration=$1
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
migrations_folder="$SCRIPT_DIR/../migrations/"
environment=$environment \
  migrations_folder=$migrations_folder \
    migration=$migration \
  docker-compose --file $SCRIPT_DIR/docker-compose.yml up --build --force-recreate dtw_database_migration_create
