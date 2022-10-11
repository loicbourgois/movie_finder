psql --username "$POSTGRES_USER" --dbname "downtowhat_rw" \
  -c "\copy item FROM '/docker-entrypoint-initdb.d/data/item/$query_hash.csv' DELIMITER ',' CSV HEADER;"

psql --username "$POSTGRES_USER" --dbname "downtowhat_rw" \
  -c "\copy item_label FROM '/docker-entrypoint-initdb.d/data/label/$query_hash.csv' DELIMITER '|' CSV HEADER;"

psql --username "$POSTGRES_USER" --dbname "downtowhat_rw" \
  -c "\copy subclass FROM '/docker-entrypoint-initdb.d/data/subclass/$query_hash.csv' DELIMITER '|' CSV HEADER;"
