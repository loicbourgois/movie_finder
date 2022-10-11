#!/bin/bash
set -e
path=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".path")
user=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".user")
host=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".host")
echo "ssh -i $path $user@$host"
ssh -i $path $user@$host
