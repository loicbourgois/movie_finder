#!/bin/sh
# $HOME/github.com/loicbourgois/movie_finder/movie_front/_go.sh
docker-compose \
  --file $HOME/github.com/loicbourgois/movie_finder/movie_front/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
