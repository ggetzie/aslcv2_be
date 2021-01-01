#!/bin/sh

python manage.py collectstatic --noinput
pwd
ls /usr/local/src/aslcv2_be/srv/docker
exec "$@"
