#!/bin/sh
# file://./../../movie_finder_local/data_v3/database/go_inner.sh
set -e
DATABASE_USER=local_dev
DATABASE_DBNAME=local_dev
DATABASE_PASSWORD=local_dev_password
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	-- fix for 
	-- 	checkpoints are occurring too frequently
	--	HINT:  Consider increasing the configuration parameter "max_wal_size".
	ALTER SYSTEM SET max_wal_size = '4GB';
	-- Reload configuration to apply changes
    SELECT pg_reload_conf(); 
	CREATE USER $DATABASE_USER PASSWORD '$DATABASE_PASSWORD';
	CREATE DATABASE $DATABASE_DBNAME OWNER $DATABASE_USER;
EOSQL
PGPASSWORD=$DATABASE_PASSWORD psql -v ON_ERROR_STOP=1 --username $DATABASE_USER --dbname $DATABASE_DBNAME \
	-c "\timing" \
	-f "$HOME/github.com/loicbourgois/movie_finder/database/init_1.sql" \
{IMPORT_CSV}
	-f "$HOME/github.com/loicbourgois/movie_finder/database/init_2.sql"
