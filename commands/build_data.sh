#!/bin/sh
set -e
# docker compose duplicates logs
# docker-compose \
#   --file $HOME/github.com/loicbourgois/movie_finder/docker-compose.yml \
#   up \
#   --renew-anon-volumes --build --force-recreate --remove-orphans \
#   data_builder
cd $HOME/github.com/loicbourgois/movie_finder
$HOME/github.com/loicbourgois/movie_finder/.venv/bin/python \
  -m data_builder.main
chmod +x $HOME/github.com/loicbourgois/movie_finder/database/go_inner_py.sh
