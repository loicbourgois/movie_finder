#!/bin/sh
set -e
docker-compose --file $HOME/github.com/loicbourgois/movie_finder/docker-compose.yml down
docker-compose --file $HOME/github.com/loicbourgois/movie_finder/docker-compose.yml up \
  --build --force-recreate database
