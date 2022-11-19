#!/bin/sh
cd /root/github.com/loicbourgois/
gunicorn --bind 0.0.0.0:81 downtowhat.movie_back.main:app
