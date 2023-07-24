#!/bin/bash -x

sleep 5s
python manage.py migrate --noinput || exit 1
python manage.py collectstatic --noinput || exit 1
cp -r /app/collected_static/. /backend_static/static/ || exit 1
rm -f /app/entrypoint.sh || exit 1
exec "$@"
