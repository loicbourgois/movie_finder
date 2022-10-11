#!/bin/sh
cd /root/github.com/loicbourgois
mkdir -p /root/github.com/loicbourgois/movie_finder_local/data/map/
python -m movie_finder.data_builder.main
