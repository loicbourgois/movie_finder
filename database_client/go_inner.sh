#!/bin/sh
set -e
PGPASSWORD=local_dev_password psql \
	--username local_dev \
	--dbname local_dev \
	--host host.docker.internal \
	--port 5432 \
	-c "\timing" \
	-f $HOME/github.com/loicbourgois/movie_finder/database_client/$QUERY_ID.sql
