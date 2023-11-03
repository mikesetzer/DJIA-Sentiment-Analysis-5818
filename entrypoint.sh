#!/bin/bash
# Docker entrypoint script.

# Prepare log files and start outputting logs to stdout
# Your log preparation here

# Check if the DB_MIGRATE environment variable is set to 'true'
if [ "$DB_MIGRATE" == "true" ]; then
    # Apply database migrations
    echo "Applying database migrations"
    python manage.py migrate

    # Import stock data
    echo "Importing stock data"
    python manage.py import_stocks

    # Load database
    echo "Loading database"
    python manage.py load_database
fi

# Start Gunicorn processes
echo "Starting Gunicorn."
exec gunicorn core.wsgi:application --config gunicorn-cfg.py
