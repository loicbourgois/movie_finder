#!/bin/sh
set -e
QUERY_ID=$1 docker-compose --file $HOME/github.com/loicbourgois/movie_finder/docker-compose.yml up \
  --build --force-recreate database_client
