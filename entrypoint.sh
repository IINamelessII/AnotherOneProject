#!/bin/sh

python manage.py migrate users
python manage.py migrate main
python manage.py migrate
python manage.py collectstatic --no-input --clear
