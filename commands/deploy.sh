#!/bin/sh
set -e
path=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".path")
path_root=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".path_root")
user=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".user")
host=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".host")
# ssh -i $path $user@$host
cat $HOME/github.com/loicbourgois/downtowhat/commands/deploy_remote.sh | ssh -i $path $user@$host 'bash -s'
