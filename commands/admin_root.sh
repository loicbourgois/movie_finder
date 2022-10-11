#!/bin/bash
set -e
path_root=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".path_root")
host=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".host")
echo "ssh -i $path_root root@$host"
ssh -i $path_root root@$host
