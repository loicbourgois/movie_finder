#!/bin/bash
set -e
path=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".path")
user=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".user")
host=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".host")
ssh -i $path $user@$host 'tail -n 100 $HOME/downtowhat_server.log'
