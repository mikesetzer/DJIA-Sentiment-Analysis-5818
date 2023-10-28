#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip to the latest version
#python -m pip install --upgrade pip

# Install required Python packages
#pip install -r requirements.txt

# Collect static files from apps and other locations in a single location.
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Custom command to load stock data into your database
python manage.py import_stocks

# Build recommendations database
python manage.py load_database