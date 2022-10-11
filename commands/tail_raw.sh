#!/bin/sh
set -e
tail -n 1 $HOME/github.com/loicbourgois/movie_finder_local/data/*.raw | grep -B 1 "at java"
