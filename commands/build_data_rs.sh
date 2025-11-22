#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/movie_finder/data_builder
cargo run
chmod +x $HOME/github.com/loicbourgois/movie_finder/database/go_inner_rs.sh
