#!/bin/sh
set -e

# until ./wait_for_postgres.p '\l'; do
#     echo >&2 "Postgres is unavailable - sleeping"
#     sleep 1
# done
# if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
#     python manage.py migrate --noinput
# fi

echo >&2 "Runing post container scripts"

# python wait_for_postgres.py &&
./physionet-django/manage.py migrate
# && python ./physionet-django/manage.py collectstatic --noinput

exec "$@"
