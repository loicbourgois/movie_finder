#!/bin/sh
set -e
docker-compose --file $HOME/github.com/loicbourgois/downtowhat/database/docker-compose.yml up --renew-anon-volumes --build --force-recreate &
$HOME/github.com/loicbourgois/downtowhat/database/migrate/create.sh 000
