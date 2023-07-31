#!/bin/sh
set -e
mkdir -p $HOME/github.com/loicbourgois
cd $HOME/github.com/loicbourgois
git clone https://github.com/loicbourgois/downtowhat.git || true
cd $HOME/github.com/loicbourgois/downtowhat
git fetch --all
git checkout origin/movie
ls