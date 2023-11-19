#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/movie_finder
git add .
git commit -m "up" || true
git push
path=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".path")
path_root=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".path_root")
user=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".user")
host=$(cat $HOME/github.com/loicbourgois/movie_finder_local/secrets.json | jq -r ".host")
cat $HOME/github.com/loicbourgois/movie_finder/commands/deploy_remote.sh | ssh -i $path $user@$host 'bash -s'
