#!/bin/sh
set -e
run_command_and_measure() {
  start=$(gdate +%s%3N)
  echo "# $@" | sed "s#$HOME#~#g"
  "$@"
  end=$(gdate +%s%3N)
  duration=$((end - start))
  echo "${duration} ms"
}
run_command_and_measure sqruff fix $HOME/github.com/loicbourgois/movie_finder/database_client/sql/
run_command_and_measure sqruff fix $HOME/github.com/loicbourgois/movie_finder/database/init_1_py.sql
run_command_and_measure sqruff fix $HOME/github.com/loicbourgois/movie_finder/database/init_1_rs.sql
run_command_and_measure ruff check \
  --config $HOME/github.com/loicbourgois/movie_finder/ruff.toml \
  "$HOME/github.com/loicbourgois/movie_finder/data_builder"
run_command_and_measure \
  cargo +nightly clippy \
  --manifest-path $HOME/github.com/loicbourgois/movie_finder/database/Cargo.toml \
  --release \
  --all-targets \
  --all-features \
  -- -D warnings \
  -W clippy::pedantic \
  -W clippy::nursery \
  -W clippy::cargo \
  -A clippy::missing_panics_doc \
  -A clippy::cargo_common_metadata

# run_command_and_measure $HOME/github.com/loicbourgois/movie_finder/.venv/bin/python \
#   -m mypy \
#   $HOME/github.com/loicbourgois/movie_finder/data_builder
# Used to check for E0401 (import-error)
# which is not implemented by ruff yet
# https://github.com/astral-sh/ruff/issues/970 
# run_command_and_measure $HOME/github.com/loicbourgois/movie_finder/.venv/bin/python \
#   -m pylint \
#   --disable=all \
#   --enable=E0401 \
#   $HOME/github.com/loicbourgois/movie_finder/data_builder
echo "[OK]"
