#!/bin/bash
set -e
path=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".path")
user=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".user")
host=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".host")
# ssh -i $$path $user@$host 'tail -n 100 $HOME/movie_finder_server.log'
# downtowhat_server.log
# ssh -i $$path $user@$host
