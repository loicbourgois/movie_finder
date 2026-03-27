#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/movie_finder/database
cargo +nightly bench --test "*"
