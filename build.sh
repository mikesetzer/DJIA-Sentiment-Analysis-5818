#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to app directory
cd /app

# Upgrade pip to the latest version
python -m pip install --upgrade pip

# Install required Python packages
pip install -r requirements.txt

# Collect static files from apps and other locations in a single location.
python manage.py collectstatic --no-input
