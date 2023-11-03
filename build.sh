#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Run the custom management commands to load data into the database
# It's assumed that load_database.py script is idempotent and can be run safely multiple times
python manage.py load_database
