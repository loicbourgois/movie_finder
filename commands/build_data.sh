#!/bin/sh
set -e
docker compose \
  --file $HOME/github.com/loicbourgois/movie_finder/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans \
  data_builder
chmod +x $HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/go_inner.sh
