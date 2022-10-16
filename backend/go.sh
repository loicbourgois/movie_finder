#!/bin/sh
set -e
docker-compose \
  --file $HOME/github.com/loicbourgois/downtowhat/backend/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
