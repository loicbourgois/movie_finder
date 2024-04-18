#/!bin/sh
set -e
cargo +nightly fmt --manifest-path $HOME/github.com/loicbourgois/movie_finder/server/Cargo.toml
cargo clippy \
    --manifest-path $HOME/github.com/loicbourgois/movie_finder/server/Cargo.toml \
    --fix \
    --allow-dirty \
    -- \
    -A clippy::single_match \
    -A clippy::too_many_arguments \
    -W clippy::pedantic \
    -A clippy::cast_precision_loss \
    -A clippy::cast_sign_loss \
    -A clippy::cast_possible_truncation \
    -A clippy::module_name_repetitions \
    -A clippy::unused_self \
    -A clippy::too_many_lines \
    -A clippy::match_same_arms \
    -A clippy::similar_names \
    -A clippy::many_single_char_names \
    -A clippy::match_on_vec_items \
    -A clippy::single_match_else \
    -A clippy::missing_panics_doc \
    -A clippy::must_use_candidate
cargo  test --manifest-path $HOME/github.com/loicbourgois/movie_finder/server/Cargo.toml --release -- --nocapture
