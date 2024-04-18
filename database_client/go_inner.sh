#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/movie_finder
QUERY_ID=$QUERY_ID python -m database_client.main
# PGPASSWORD=local_dev_password psql \
# 	--username local_dev \
# 	--dbname local_dev \
# 	--host host.docker.internal \
# 	--port 5432 \
# 	-c "\timing" \
# 	-f $HOME/github.com/loicbourgois/movie_finder/database_client/${QUERY_ID}_table.sql
PGPASSWORD=local_dev_password psql \
	--username local_dev \
	--dbname local_dev \
	--host host.docker.internal \
	--port 5432 \
	-c "\timing" \
	-f $HOME/github.com/loicbourgois/movie_finder/database_client/${QUERY_ID}_json.sql
