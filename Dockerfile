# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
# - PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script into the container
COPY entrypoint.sh /usr/src/app/entrypoint.sh

# Make sure the script is executable
RUN chmod +x /usr/src/app/entrypoint.sh

# Copy the current directory contents into the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Make port 5005 available to the world outside this container
EXPOSE 5005

# Run the entrypoint script to start the application
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
