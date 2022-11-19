#!/bin/sh
# $HOME/github.com/loicbourgois/downtowhat/movie_back/_go.sh
docker-compose \
  --file $HOME/github.com/loicbourgois/downtowhat/movie_back/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
