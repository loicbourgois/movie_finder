#!/bin/sh
set -e
gunicorn --bind ${API_HOST}:${API_PORT} backend.main:app
