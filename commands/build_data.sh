#!/bin/sh
set -e
docker compose \
  --file $HOME/github.com/loicbourgois/movie_finder/data_builder/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
