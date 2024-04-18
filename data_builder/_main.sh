#!/bin/sh
cd /root/github.com/loicbourgois
# python -m movie_finder.data_builder.main
python -m movie_finder.data_builder.rdf_to_sql
# pylint --jobs=0 \
#     --rcfile $HOME/github.com/loicbourgois/movie_finder/data_builder/pylintrc \
#     $HOME/github.com/loicbourgois/movie_finder/data_builder/rdf_to_sql.py
