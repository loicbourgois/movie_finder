#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/movie_finder/database
cargo fmt
# cargo +nightly test --test "*"
# cargo +nightly bench --test "*"
cargo run --release
