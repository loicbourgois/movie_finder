#!/bin/sh
set -e
mkdir -p $HOME/github.com/loicbourgois
cd $HOME/github.com/loicbourgois
git clone https://github.com/loicbourgois/downtowhat.git || true
cd $HOME/github.com/loicbourgois/downtowhat
git fetch --all
git checkout origin/movie
git status
sleep 1
# docker run hello-world
$HOME/github.com/loicbourgois/downtowhat/commands/build_data.sh
rm /home/gravitle/github.com/loicbourgois/downtowhat_local/data/cast_member_label.raw
rm /home/gravitle/github.com/loicbourgois/downtowhat_local/data/film_cast_member_2.raw
rm /home/gravitle/github.com/loicbourgois/downtowhat_local/data/film_cast_member_4.raw
$HOME/github.com/loicbourgois/downtowhat/commands/tail_raw.sh
