#!/bin/bash
# Run tests with SQLite database
export DJANGO_SETTINGS_MODULE=library.settings
export TEST_DATABASE=sqlite
cd /Volumes/Macintosh HD/Users/kb/gits/momentum-api
poetry run python library/manage.py test tests
