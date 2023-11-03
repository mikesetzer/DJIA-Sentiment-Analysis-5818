#!/bin/bash
# Docker entrypoint script.

# Wait for the DB to be ready before attempting to use it
# Here you would include your logic to wait for a database if needed

# Prepare log files and start outputting logs to stdout
# Add any log file preparation here if needed

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate

# Import stock data
echo "Importing stock data"
python manage.py import_stocks

# Load database
echo "Loading database"
python manage.py load_database

# Start Gunicorn processes
echo "Starting Gunicorn."
exec gunicorn core.wsgi:application --config gunicorn-cfg.py
