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
    -c "\copy item___director FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___director.csv' CSV HEADER;" \
    -c "\copy item___gender FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___gender.csv' CSV HEADER;" \
    -c "\copy item___date_of_birth FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___date_of_birth.csv' CSV HEADER;" \
    -c "\copy item___occupation FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___occupation.csv' CSV HEADER;" \
    -c "\copy item___nominated_for FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___nominated_for.csv' CSV HEADER;" \
    -c "\copy item___award_received FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___award_received.csv' CSV HEADER;" \
    -c "\copy item___genre FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___genre.csv' CSV HEADER;" \
    -c "\copy item___producer FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___producer.csv' CSV HEADER;" \
    -c "\copy item___creator FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___creator.csv' CSV HEADER;" \
    -c "\copy item___screen_writer FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___screen_writer.csv' CSV HEADER;" \
    -c "\copy item___publication_date FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___publication_date.csv' CSV HEADER;" \
    -c "\copy item___cast_member FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___cast_member.csv' CSV HEADER;" \
    -c "\copy item___imdb_id FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___imdb_id.csv' CSV HEADER;" \
    -c "\copy item___narrator FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___narrator.csv' CSV HEADER;" \
    -c "\copy item___characters FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___characters.csv' CSV HEADER;" \
    -c "\copy item___main_subject FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___main_subject.csv' CSV HEADER;" \
    -c "\copy item___original_language FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___original_language.csv' CSV HEADER;" \
    -c "\copy item___composer FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___composer.csv' CSV HEADER;" \
    -c "\copy item___film_editor FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___film_editor.csv' CSV HEADER;" \
    -c "\copy item___inspired_by FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___inspired_by.csv' CSV HEADER;" \
    -c "\copy item___depicts FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___depicts.csv' CSV HEADER;" \
    -c "\copy item___attendance FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___attendance.csv' CSV HEADER;" \
    -c "\copy item___duration FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___duration.csv' CSV HEADER;" \
    -c "\copy item___omdb_id FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___omdb_id.csv' CSV HEADER;" \
    -c "\copy item___box_office FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___box_office.csv' CSV HEADER;" \
    -c "\copy item___capital_cost FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___capital_cost.csv' CSV HEADER;" \
    -c "\copy item___review_score FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___review_score.csv' CSV HEADER;" \
    -c "\copy item FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item.csv' CSV HEADER;" \
    -c "\copy item___label FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/item___label.csv' CSV HEADER;" \
    -c "\copy omdb___movie_links FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___movie_links.csv' CSV HEADER;" \
    -c "\copy omdb___image_ids FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___image_ids.csv' CSV HEADER;" \
    -c "\copy omdb___movie_references FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___movie_references.csv' CSV HEADER;" \
    -c "\copy omdb___category_names FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___category_names.csv' CSV HEADER;" \
    -c "\copy omdb___movie_categories FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___movie_categories.csv' CSV HEADER;" \
    -c "\copy omdb___all_categories FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___all_categories.csv' CSV HEADER;" \
    -c "\copy omdb___all_votes FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___all_votes.csv' CSV HEADER;" \
    -c "\copy omdb___all_movies FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___all_movies.csv' CSV HEADER;" \
    -c "\copy omdb___all_series FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/omdb___all_series.csv' CSV HEADER;" \
	-f "$HOME/github.com/loicbourgois/movie_finder/database/init_2.sql"
