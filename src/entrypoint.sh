#!/bin/bash

while ! nc -z $POSTGRES_HOST $PGPORT; do
      sleep 0.1
done 

echo Applying migrations...
alembic upgrade head

exec "$@"