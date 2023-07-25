#!/bin/sh
docker-compose \
  --file $HOME/github.com/loicbourgois/downtowhat/data_builder/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
