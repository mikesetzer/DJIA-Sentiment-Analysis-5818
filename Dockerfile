FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Apply database migrations
RUN python manage.py migrate

# Run the custom management commands to load data
# Assuming that the load_database already includes the functionality of import_stocks, hence not repeating it
RUN python manage.py load_database

# Start gunicorn with the specified configuration file
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
