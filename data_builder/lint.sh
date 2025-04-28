#!/bin/sh
cd /root/github.com/loicbourgois
pylint --jobs=0 \
    --rcfile $HOME/github.com/loicbourgois/movie_finder/data_builder/pylintrc \
    $HOME/github.com/loicbourgois/movie_finder/data_builder
