#!/bin/sh

# Add the concerned values in these environment variables

export DISCOG_DEV_DB
export POSTGRES_USER
export POSTGRES_USER_PASSWORD
export SENTRY_DNS

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for TimescaleDB ...."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "Postgres DB started"
fi

echo "Running the migrations"
python manage.py migrate
echo "Collecting staticfiles"
python manage.py collectstatic --no-input --clear
exec "$@"
