#!/bin/sh
set -e
mkdir -p $HOME/github.com/loicbourgois/downtowhat_local/data/map/
docker compose \
  --file $HOME/github.com/loicbourgois/downtowhat/data_builder/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
