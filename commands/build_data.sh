#!/bin/sh
set -e
# docker compose duplicates logs
docker-compose \
  --file $HOME/github.com/loicbourgois/movie_finder/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans \
  data_builder
chmod +x $HOME/github.com/loicbourgois/movie_finder/database/go_inner_py.sh
