#!/bin/sh
set -e
cp $HOME/github.com/loicbourgois/downtowhat/submodules/image-conversion/build/conversion.js \
  $HOME/github.com/loicbourgois/downtowhat/front/libs/image_conversion.js
docker-compose \
  --file $HOME/github.com/loicbourgois/downtowhat/backend/docker-compose.yml \
  up \
  --renew-anon-volumes --build --force-recreate --remove-orphans
