#!/bin/sh
set -e
$HOME/github.com/loicbourgois/movie_finder/.venv/bin/python \
  -m pip install \
  -r $HOME/github.com/loicbourgois/movie_finder/data_builder/requirements.txt
