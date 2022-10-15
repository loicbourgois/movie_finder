#!/bin/bash
set -e
PGPASSWORD=${DATABASE_PASSWORD} python -m database.query.query
