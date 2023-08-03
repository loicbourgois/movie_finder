#!/bin/sh
set -e
echo ""
mkdir -p $HOME/github.com/loicbourgois
cd $HOME/github.com/loicbourgois
git clone https://github.com/loicbourgois/downtowhat.git || true
cd $HOME/github.com/loicbourgois/downtowhat
git fetch --all
git reset --hard
git checkout origin/movie
git status
sleep 1
# $HOME/github.com/loicbourgois/downtowhat/commands/build_data.sh
# $HOME/github.com/loicbourgois/downtowhat/commands/tail_raw.sh
$HOME/github.com/loicbourgois/downtowhat/commands/run_remote.sh
